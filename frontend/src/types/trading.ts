/**
 * TypeScript types for real-time trading data
 */

export interface LiveTrade {
  timestamp: number;
  ticker: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  trade_id: string;
  source: 'bot_live' | 'simulated' | 'manual_simulation';
}

export interface TerminalMessage {
  id: number;
  timestamp: string;
  message: string;
}

export interface BotStatus {
  is_online: boolean;
  previous_status: boolean;
  timestamp: number;
}

export interface SSEConnectionState {
  isConnected: boolean;
  connectionError: string | null;
}

// SSE Event types that come from FastAPI
export interface NewTradesEvent {
  trades: LiveTrade[];
  count: number;
  timestamp: number;
}

export interface BotStatusEvent {
  is_online: boolean;
  timestamp: number;
  // uptime?: number;
  // position_count?: number;
  // consecutive_failures?: number;
}

export interface HeartbeatEvent {
  timestamp: number;
  connected_clients?: number;
}

export interface InitialStateEvent {
  recent_trades: LiveTrade[];
  is_online: boolean;
  last_update: number;
}

// Props for components that use trading data
export interface TradingDataProps {
  liveTrades: LiveTrade[];
  terminalMessages: TerminalMessage[];
  botStatus: BotStatus;
  connectionState: SSEConnectionState;
}

// export type SSEEventType = 'new_trades' | 'bot_status' | 'heartbeat' | 'initial_state' | 'connected' | 'ping';
//
// export interface SSEEvent<T = any> {
//   type: SSEEventType;
//   data: T;
//   timestamp: number;
// }