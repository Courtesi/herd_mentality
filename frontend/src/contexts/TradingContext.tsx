/**
 * TradingContext - Centralized SSE state management for real-time trading data
 * Consolidates SSE connection logic and bot status management in one place
 */

import React, { createContext, useContext, useEffect, useState, useCallback, useRef, type ReactNode } from 'react';
import type {
  LiveTrade,
  TerminalMessage,
  BotStatus,
  SSEConnectionState,
  NewTradesEvent,
  BotStatusEvent,
  InitialStateEvent,
} from '../types/trading';
import { logger } from "../utils/logger.ts";

interface TradingContextType {
  liveTrades: LiveTrade[];
  terminalMessages: TerminalMessage[];
  botStatus: BotStatus;
  connectionState: SSEConnectionState;
  isReceivingLiveData: boolean;
}

const TradingContext = createContext<TradingContextType | undefined>(undefined);

// Custom hook to use trading context
// eslint-disable-next-line react-refresh/only-export-components
export const useTradingContext = (): TradingContextType => {
  const context = useContext(TradingContext);
  if (!context) {
    throw new Error('useTradingContext must be used within a TradingProvider');
  }
  return context;
};

interface TradingProviderProps {
  children: ReactNode;
  maxTrades?: number;
  maxMessages?: number;
}

export const TradingProvider: React.FC<TradingProviderProps> = ({
  children,
  maxTrades = 50,
  maxMessages = 50,
}) => {
  // State for real-time data
  const [liveTrades, setLiveTrades] = useState<LiveTrade[]>([]);
  const [terminalMessages, setTerminalMessages] = useState<TerminalMessage[]>([]);
  const initialBotStatus : BotStatus = {is_online: false, previous_status: false, timestamp: Date.now(),};
  const [botStatus, setBotStatus] = useState<BotStatus>(initialBotStatus);

  // SSE connection state (simplified - no reconnection)
  const [connectionState, setConnectionState] = useState<SSEConnectionState>({
    isConnected: false,
    connectionError: null,
  });

  // Message counter for unique IDs - use Ref to survive StrictMode remounts
  const messageCounterRef = useRef(1);

  const addLiveTrades = useCallback((
      trades: LiveTrade[],
  ) => {

    setLiveTrades(prevLiveTrades => {
      const updated = trades.concat(prevLiveTrades);
      return updated.slice(0, maxTrades);
    })
  }, [maxTrades]);

  const initializeLiveTrades = useCallback((
      trades: LiveTrade[],
  ) => {

    setLiveTrades(() => {
      return trades ? trades.slice(0, maxTrades) : [];
    })
  }, [maxTrades]);


  // Helper to add terminal message with stable reference
  const addTerminalMessage = useCallback((
    message: string,
  ) => {
    const messageId = messageCounterRef.current++;
    const newMessage: TerminalMessage = {
      id: messageId,
      timestamp: new Date().toLocaleTimeString(),
      message,
    };

    setTerminalMessages(prevMessages => {
      const updated = [newMessage, ...prevMessages];
      return updated.slice(0, maxMessages); // Keep only last N messages
    });
  }, [maxMessages]);

  useEffect(() => {
    const eventSource = new EventSource("/api/python/sse/trading");

    eventSource.onopen = () => {
      const newConnectionState: SSEConnectionState = {isConnected: true, connectionError: null};
      setConnectionState(newConnectionState);
    };

    eventSource.addEventListener("initial_state", (e) => {
      try {
        const data : InitialStateEvent = JSON.parse(e.data);
        const recentTrades : LiveTrade[] = data.recent_trades;
        const newBotStatus : boolean = data.is_online;
        const lastUpdate = data.last_update;
        initializeLiveTrades(recentTrades);
        let newBotStatusObject : BotStatus = {is_online: newBotStatus, previous_status: false, timestamp: lastUpdate};
        setBotStatus(newBotStatusObject);
      } catch (error) {
        // logger.log(`error happened parsing: ${error}`);
      }
    });

    eventSource.addEventListener("bot_status", (e) => {
      try {
        const data : BotStatusEvent = JSON.parse(e.data);
        const status : boolean = data.is_online;
        const timestamp : number = data.timestamp;

        const newBotStatusObject : BotStatus = {is_online: status, previous_status: botStatus.previous_status, timestamp: timestamp};
        setBotStatus(newBotStatusObject);
      } catch (error) {
        logger.log(`error happened in bot_status: ${error}`);
      }

    });

    eventSource.addEventListener("bot_trade", (e) => {
      try {
        const data: NewTradesEvent = JSON.parse(e.data);
        const newTrade: LiveTrade[] = data.trades;
        addLiveTrades(newTrade);
      } catch (error) {
        logger.log(`bot_trade error: ${error}`)
      }
    })

    eventSource.addEventListener("bot_message", (e) => {
      try {
        const data = JSON.parse(e.data);
        const message = data.message;
        addTerminalMessage(message);
      } catch (error) {
        logger.log(`bot_message error: ${error}`)
      }
    });

    eventSource.onerror = () => {
      const connectionErrorState: SSEConnectionState = {isConnected: false, connectionError: "SSE initialization error"};
      setConnectionState(connectionErrorState);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);


  // Computed values (single source of truth: botStatus.status)
  const isReceivingLiveData = connectionState.isConnected && botStatus.is_online;

  const value: TradingContextType = {
    liveTrades,
    terminalMessages,
    botStatus,
    connectionState,
    isReceivingLiveData,
  };

  // logger.log(`botStatus connection: ${botStatus.is_online} && connectionState: ${connectionState.isConnected}`);
  // logger.log(`isReceivingLiveData: ${isReceivingLiveData}`);

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
};

// Export context for testing or advanced usage
export { TradingContext };