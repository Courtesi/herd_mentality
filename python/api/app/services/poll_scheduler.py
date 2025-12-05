import asyncio
import logging
import random
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from exchanges.kalshi.rest.markets import Market
from exchanges.kalshi.rest.portfolio import Portfolio

logger = logging.getLogger(__name__)


class PollScheduler:
	"""Manages automated poll creation from Kalshi markets"""

	def __init__(self):
		self.scheduler = AsyncIOScheduler()
		self.market_client = Market()
		self.portfolio_client = Portfolio()
		self.http_client: Optional[httpx.AsyncClient] = None
		self.is_running = False

	async def start(self):
		"""Start the poll scheduler"""
		if self.is_running:
			logger.warning("Poll scheduler is already running")
			return

		self.http_client = httpx.AsyncClient(timeout=30.0)

		# Check if we're in production environment
		is_production = settings.ENVIRONMENT.lower() == "production"

		if not is_production:
			logger.info(f"Poll scheduler disabled in {settings.ENVIRONMENT} mode. Set ENVIRONMENT=production to enable automatic poll creation.")
			self.is_running = True
			return

		# Schedule poll creation every 36 hours (production only)
		# temp = settings.CREATE_POLL_HOUR_INTERVAL
		# self.scheduler.add_job(
		# 	self.create_poll_from_kalshi,
		# 	trigger=IntervalTrigger(hours=temp),
		# 	id='poll_creator',
		# 	name='Create poll from Kalshi market',
		# 	replace_existing=True
		# )

		# Schedule poll ending every 1 hour (production only)
		temp2 = settings.PROCESS_EXPIRED_POLLS_MIN_INTERVAL
		self.scheduler.add_job(
			self.process_expired_polls,
			trigger=IntervalTrigger(minutes=temp2),
			id='poll_ender',
			name='End expired polls and execute trades',
			replace_existing=True
		)

		self.scheduler.start()
		self.is_running = True
		logger.info("Poll scheduler started - will create polls every 36 hours and check for expired polls every hour")

		# Create first poll immediately (non-blocking, don't fail startup if it errors)
		try:
			await self.create_poll_from_kalshi()
		except Exception as e:
			logger.error(f"Failed to create initial poll on startup: {e}. Will retry on next scheduled interval.", exc_info=True)

	async def stop(self):
		"""Stop the poll scheduler"""
		if not self.is_running:
			return

		self.scheduler.shutdown(wait=False)
		if self.http_client:
			await self.http_client.aclose()

		self.is_running = False
		logger.info("Poll scheduler stopped")

	async def create_poll_from_kalshi(self):
		"""
		Fetch Kalshi events, select one randomly, and create a poll in Spring Boot
		Poll type is determined by the number of markets in the event
		"""
		try:
			logger.info("Starting poll creation from Kalshi markets")

			# 1. Fetch all open Kalshi events that won't close for at least 7 days
			min_close_ts = int((datetime.now() + timedelta(days=7)).timestamp())

			# Wrap synchronous API call with timeout protection
			events_response = await asyncio.wait_for(
				asyncio.to_thread(
					self.market_client.get_events,
					status="open",
					with_nested_markets=True,
					min_close_ts=min_close_ts
				),
				timeout=45.0
			)

			events = events_response.get("events", [])
			if not events:
				logger.warning("No open Kalshi events found that meet the duration requirement")
				return

			logger.info(f"Found {len(events)} eligible Kalshi events")

			# 2. Randomly select an event
			selected_event = random.choice(events)
			series_ticker = selected_event.get("series_ticker")
			event_title = selected_event.get("title")
			markets = selected_event.get("markets", [])

			if not markets:
				logger.warning(f"Series {series_ticker} has no markets")
				return

			logger.info(f"Selected Kalshi event: {event_title} ({series_ticker}) with {len(markets)} market(s)")

			# 3. Determine poll type based on number of markets
			if len(markets) == 1:
				# Single market = Binary poll (Yes/No)
				market = markets[0]
				market_ticker = market.get("ticker")
				poll_data = self._create_binary_poll(event_title, series_ticker, market_ticker)
				logger.info("Creating BINARY poll")
			else:
				# Multiple markets = Contract count poll
				selected_market = random.choice(markets)
				market_ticker = selected_market.get("ticker")
				yes_sub_title = selected_market.get("yes_sub_title", "this outcome")
				poll_data = self._create_contract_count_poll(
					event_title,
					yes_sub_title,
					series_ticker,
					market_ticker
				)
				logger.info(f"Creating CONTRACT COUNT poll for market: {yes_sub_title}")

			# 4. Send to Spring Boot
			await self._send_poll_to_spring_boot(poll_data)

		except asyncio.TimeoutError:
			logger.error("Kalshi API call timed out after 45 seconds. Skipping poll creation.")
		except Exception as e:
			logger.error(f"Failed to create poll from Kalshi: {e}", exc_info=True)

	def _create_binary_poll(
		self,
		event_title: str,
		series_ticker: str,
		market_ticker: str
	) -> Dict[str, Any]:
		"""Create a binary yes/no poll for events with a single market"""
		ends_at = datetime.now() + timedelta(hours=36)

		return {
			"question": event_title,
			"description": f"Based on Kalshi market: {series_ticker}",
			"optionAText": "Yes",
			"optionBText": "No",
			"endsAt": ends_at.isoformat(),
			"kalshiSeriesTicker": series_ticker,
			"kalshiMarketTicker": market_ticker,
			"pollType": "BINARY_PREDICTION"
		}

	def _create_contract_count_poll(
		self,
		event_title: str,
		market_yes_sub_title: str,
		series_ticker: str,
		market_ticker: str
	) -> Dict[str, Any]:
		"""Create a contract count poll for events with multiple markets"""
		ends_at = datetime.now() + timedelta(hours=36)

		# Pick 2 different random numbers from 1-5
		counts = random.sample(range(1, 6), 2)  # Returns 2 unique numbers

		question = f"How many YES contracts should we buy on: {event_title} - {market_yes_sub_title}?"

		return {
			"question": question,
			"description": f"Based on Kalshi event: {series_ticker}, Market: {market_ticker}",
			"optionAText": str(counts[0]),
			"optionBText": str(counts[1]),
			"endsAt": ends_at.isoformat(),
			"kalshiSeriesTicker": series_ticker,
			"kalshiMarketTicker": market_ticker,
			"pollType": "CONTRACT_COUNT"
		}

	async def _send_poll_to_spring_boot(self, poll_data: Dict[str, Any]):
		"""Send poll creation request to Spring Boot API"""
		if not self.http_client:
			logger.error("HTTP client not initialized")
			return

		url = f"{settings.SPRINGBOOT_URL}/api/polls/create"
		headers = {
			"Content-Type": "application/json",
			"X-Internal-API-Key": settings.INTERNAL_API_KEY
		}

		try:
			logger.info(f"Sending poll to Spring Boot: {url}")
			response = await self.http_client.post(
				url,
				json=poll_data,
				headers=headers
			)

			if response.status_code == 201:
				logger.info(f"Successfully created poll: {poll_data['question']}")
				logger.debug(f"Response: {response.json()}")
			else:
				logger.error(
					f"Failed to create poll. Status: {response.status_code}, "
					f"Response: {response.text}"
				)

		except Exception as e:
			logger.error(f"Error sending poll to Spring Boot: {e}", exc_info=True)

	async def process_expired_polls(self):
		"""
		Check for expired polls, determine winner, execute trades, and mark polls inactive
		"""
		try:
			logger.info("Checking for expired polls...")

			# 1. Fetch expired polls from Spring Boot
			url = f"{settings.SPRINGBOOT_URL}/api/polls/expired"
			response = await self.http_client.get(url)

			if response.status_code != 200:
				logger.error(f"Failed to fetch expired polls. Status: {response.status_code}")
				return

			expired_polls = response.json()
			if not expired_polls:
				logger.info("No expired polls found")
				return

			logger.info(f"Processing {len(expired_polls)} expired poll(s)")

			# 2. Process each expired poll
			for poll in expired_polls:
				await self._process_single_poll(poll)
			
			# 3. Create new poll
			await self.create_poll_from_kalshi()

		except Exception as e:
			logger.error(f"Error processing expired polls: {e}", exc_info=True)

	async def _process_single_poll(self, poll: Dict[str, Any]):
		"""Process a single expired poll"""
		poll_id = poll.get('id')
		poll_question = poll.get('question')

		try:
			logger.info(f"Processing poll {poll_id}: {poll_question}")

			# 1. Determine winning option
			winning_option = self._determine_winning_option(poll)

			if winning_option is None:
				logger.info(f"Poll {poll_id} ended in a tie, skipping trade")
				await self._mark_poll_inactive(poll_id)
				return

			option_a_votes = poll.get('optionAVotes', 0)
			option_b_votes = poll.get('optionBVotes', 0)
			logger.info(f"Poll {poll_id} winner: Option {winning_option} ({option_a_votes} vs {option_b_votes})")

			# 2. Build trade order
			order = await self._build_trade_order(poll, winning_option)

			# 3. Execute trade
			await self._execute_trade(poll, order)

			# 4. Mark poll as inactive
			await self._mark_poll_inactive(poll_id)

		except Exception as e:
			logger.error(f"Error processing poll {poll_id}: {e}", exc_info=True)
			# Still mark poll inactive even if trade failed
			try:
				await self._mark_poll_inactive(poll_id)
			except Exception as mark_error:
				logger.error(f"Failed to mark poll {poll_id} inactive: {mark_error}")

	def _determine_winning_option(self, poll: Dict[str, Any]) -> Optional[str]:
		"""Returns 'A' or 'B' for winner, None if tie"""
		option_a_votes = poll.get('optionAVotes', 0)
		option_b_votes = poll.get('optionBVotes', 0)

		if option_a_votes > option_b_votes:
			return 'A'
		elif option_b_votes > option_a_votes:
			return 'B'
		else:
			return None  # Tie

	async def _build_trade_order(self, poll: Dict[str, Any], winning_option: str) -> Dict[str, Any]:
		"""Build Kalshi order based on poll type and winner"""

		poll_type = poll.get('pollType')
		market_ticker = poll.get('marketTicker')
		timestamp = int(datetime.now().timestamp())

		# Fetch current market prices
		logger.info(f"Fetching market data for {market_ticker}")
		market_data = await asyncio.wait_for(
			asyncio.to_thread(
				self.market_client.get_market,
				market_ticker
			),
			timeout=45.0
		)
		market = market_data.get('market', {})

		# Determine side and count based on poll type
		if poll_type == 'BINARY_PREDICTION':
			# Yes vs No poll
			# Assuming option A = "Yes", option B = "No"
			if winning_option == 'A':
				side = "yes"
			else:
				side = "no"
			count = 1  # Buy 1 contract

		elif poll_type == 'CONTRACT_COUNT':
			# Contract count poll - always YES
			side = "yes"
			# Count = the winning option text (e.g., "3")
			if winning_option == 'A':
				count = int(poll.get('optionAText'))
			else:
				count = int(poll.get('optionBText'))
		else:
			raise ValueError(f"Unknown poll type: {poll_type}")

		# Get the appropriate ask price for market order
		if side == "yes":
			# For buying YES, use yes_ask (price sellers are asking)
			price = market.get('yes_ask')
		else:
			# For buying NO, use no_ask
			price = market.get('no_ask')

		if price is None:
			raise ValueError(f"No {side}_ask price available for {market_ticker}")

		logger.info(f"Using {side}_ask price: {price} cents for {market_ticker}")

		# Build order with price in cents
		order = {
			"action": "buy",
			"side": side,
			"ticker": market_ticker,
			"count": count,
			"client_order_id": f"poll_{poll.get('id')}_{timestamp}",
			"type": "market"
		}

		# Add price based on side (in cents)
		if side == "yes":
			order["yes_price"] = price
		else:
			order["no_price"] = price

		return order

	async def _execute_trade(self, poll: Dict[str, Any], order: Dict[str, Any]):
		"""Execute trade on Kalshi"""
		try:
			logger.info(f"Executing trade: BUY {order['count']} {order['side'].upper()} contracts on {order['ticker']}")

			# Execute order using Portfolio client (sync method, so run in executor)
			result = await asyncio.to_thread(self.portfolio_client.create_order, order)

			logger.info(f"Successfully placed order for poll {poll.get('id')}: {result}")

		except Exception as e:
			error_msg = str(e)
			logger.error(f"Failed to execute trade for poll {poll.get('id')}: {error_msg}", exc_info=True)

			# Check if market is closed
			if "market" in error_msg.lower() and "closed" in error_msg.lower():
				logger.warning(f"Market {order['ticker']} is closed, skipping trade")
			else:
				raise  # Re-raise if it's not a market closed error

	async def _mark_poll_inactive(self, poll_id: int):
		"""Mark poll as inactive in Spring Boot"""
		url = f"{settings.SPRINGBOOT_URL}/api/polls/{poll_id}/mark-inactive"
		headers = {
			"Content-Type": "application/json",
			"X-Internal-API-Key": settings.INTERNAL_API_KEY
		}

		try:
			response = await self.http_client.post(url, headers=headers)

			if response.status_code == 200:
				logger.info(f"Marked poll {poll_id} as inactive")
			else:
				logger.error(f"Failed to mark poll {poll_id} inactive. Status: {response.status_code}")

		except Exception as e:
			logger.error(f"Error marking poll {poll_id} inactive: {e}", exc_info=True)


# Global scheduler instance
poll_scheduler = PollScheduler()
