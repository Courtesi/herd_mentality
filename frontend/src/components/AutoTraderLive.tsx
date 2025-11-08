import React from 'react';
import { useTradingContext } from '../contexts/TradingContext';
import type { LiveTrade as SSELiveTrade } from '../types/trading';

type LiveTrade = {
    id: number;
    symbol: string;
    action: 'BUY' | 'SELL';
    time: string;
    price: number;
    quantity: number;
    status: 'FILLED' | 'PENDING' | 'CANCELLED';
};

const AutoTraderLive: React.FC = () => {
    const {
        liveTrades,
        terminalMessages,
        isReceivingLiveData
    } = useTradingContext();

    // Convert SSE trades to display format
    const convertSSETradeToDisplay = (sseTrade: SSELiveTrade): LiveTrade => ({
        id: parseInt(sseTrade.trade_id.replace(/\D/g, '')) || Date.now(),
        symbol: sseTrade.ticker,
        action: sseTrade.side as 'BUY' | 'SELL',
        time: new Date(sseTrade.timestamp > 1e12 ? sseTrade.timestamp : sseTrade.timestamp * 1000).toLocaleTimeString(),
        price: sseTrade.price,
        quantity: sseTrade.quantity,
        status: 'FILLED' as const
    });

    const displayTrades = liveTrades.map(convertSSETradeToDisplay);

    const displayMessages = isReceivingLiveData
        ? terminalMessages.slice(0, 15)
        : [{ id: 0, timestamp: new Date().toLocaleTimeString(), message: '💤 Bot is sleeping...', type: 'status' as const, source: 'system' as const }];

    return (
        <div className="bg-dark-500 rounded-lg p-6 shadow-lg h-[460px] flex flex-col">
            {/* Header with status indicators */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-50">Auto Trader Live</h2>
                <div className="flex items-center gap-3 text-xs">
                    <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${
                            isReceivingLiveData ? 'bg-green-500' : 'bg-red-500'
                        }`}></div>
                        <span className={isReceivingLiveData ? 'text-green-400' : 'text-red-400'}>
                            {isReceivingLiveData ? 'Bot Online' : 'Bot Offline'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Terminal and Table Side by Side */}
            <div className="grid grid-cols-1 lg:flex-1 lg:flex gap-4 min-h-0">
                {/* Terminal Section - 40% */}
                <div className="flex-[0.4] min-h-0">
                    <div className="bg-black rounded-lg p-4 h-full flex flex-col">
                        <div className="text-green-400 text-xs font-mono mb-2 border-b border-gray-700 pb-2 flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${
                                isReceivingLiveData ? 'bg-red-500 animate-pulse' : 'bg-gray-500'
                            }`}></div>
                            Trading Terminal{isReceivingLiveData ? ' - Live Data' : ''}
                        </div>
                        <div className="flex-1 overflow-hidden min-h-0 flex flex-col justify-end">
                            <div className="space-y-1">
                                {displayMessages.map((msg) => (
                                    <div key={msg.id} className={'text-xs font-mono text-green-500'}>
                                        <span className="text-green-600">[{msg.timestamp}]</span> {msg.message}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Live Trades Table - 60% */}
                <div className="flex-[0.6] min-h-0">
                    <div className="bg-neutral-800 rounded-lg p-4 h-full flex flex-col">
                        <div className="text-gray-200 text-sm font-semibold mb-3 border-b border-gray-600 pb-2">
                            <span>Recent Trades</span>
                        </div>
                        <div className="flex-1 overflow-y-auto min-h-0">
                            <table className="w-full text-xs">
                                <thead>
                                    <tr className="border-b border-gray-600">
                                        <th className="text-left py-1 px-1 text-gray-300">Symbol</th>
                                        <th className="text-left py-1 px-1 text-gray-300">Action</th>
                                        <th className="text-left py-1 px-1 text-gray-300">Price</th>
                                        <th className="text-left py-1 px-1 text-gray-300">Qty</th>
                                        <th className="text-left py-1 px-1 text-gray-300">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {displayTrades.map((trade) => (
                                        <tr key={trade.id} className="border-b border-gray-700">
                                            <td className="py-2 px-1 text-gray-100 font-mono">
                                                {trade.symbol}
                                            </td>
                                            <td className={`py-2 px-1 font-semibold ${
                                                trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                                            }`}>
                                                {trade.action}
                                            </td>
                                            <td className="py-2 px-1 text-gray-100 font-mono">
                                                ${trade.price.toFixed(2)}
                                            </td>
                                            <td className="py-2 px-1 text-gray-100">{trade.quantity}</td>
                                            <td className={`py-2 px-1 text-xs ${
                                                trade.status === 'FILLED' ? 'text-green-400' :
                                                trade.status === 'PENDING' ? 'text-yellow-400' : 'text-red-400'
                                            }`}>
                                                {trade.status}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AutoTraderLive;
