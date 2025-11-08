import React, { useEffect, useState } from 'react';
import { apiService } from "../services/api";

interface HistoryItem {
    id: string;
    date: string;
    market: string;
    action: 'BUY' | 'SELL';
    count: number;
    side: 'YES' | 'NO';
    price: number;
    totalCost: number;
    fees?: number;
}

const PortfolioHistory: React.FC = () => {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const transformFillsToHistory = (fills: any[], marketsData: any): HistoryItem[] => {
        return fills.map((fill) => {
            const ticker = fill.ticker;
            const marketInfo = marketsData[ticker];

            const count = fill.count || 0;
            const side = fill.side?.toUpperCase() as 'YES' | 'NO';
            const action = fill.action?.toUpperCase() as 'BUY' | 'SELL';
            const price = fill.price || 0;
            const totalCost = count * price;

            return {
                id: fill.fill_id,
                date: new Date(fill.created_time).toLocaleDateString(),
                market: marketInfo?.title || ticker,
                action: action,
                count: count,
                side: side,
                price: price,
                totalCost: totalCost
            };
        });
    };

    useEffect(() => {
        async function fetchPortfolioHistory() {
            try {
                setLoading(true);
                const response = await apiService.getPortfolioFills(50);

                if (response.success) {
                    const fills = response.data.fills;
                    const marketsData = response.data.markets_data;

                    if (!Array.isArray(fills)) {
                        console.error('Fills is not an array:', fills);
                        setError('Invalid data format received');
                        return;
                    }

                    const transformedHistory = transformFillsToHistory(fills, marketsData);
                    setHistory(transformedHistory);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load portfolio history');
                console.error('Failed to fetch portfolio history:', err);
            } finally {
                setLoading(false);
            }
        }

        fetchPortfolioHistory();
    }, []);

    if (loading) {
        return (
            <div className="bg-dark-500 rounded-lg p-6 shadow-lg h-[460px] flex items-center justify-center">
                <div className="text-gray-400">Loading portfolio history...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-dark-500 rounded-lg p-6 shadow-lg h-[460px] flex items-center justify-center">
                <div className="text-red-400">Error: {error}</div>
            </div>
        );
    }

    return (
        <div className="bg-dark-500 rounded-lg p-6 shadow-lg h-[460px] flex flex-col">
            <h2 className="text-lg font-bold text-gray-50 mb-4 text-center">Portfolio History</h2>

            <div className="flex-1 overflow-y-auto">
                {history.length === 0 ? (
                    <div className="text-center text-gray-400 py-8">
                        No trades yet
                    </div>
                ) : (
                    <div className="overflow-x-auto ">
                        <table className="w-full text-sm">
                            <thead>
                            <tr className="border-b border-neutral-600">
                                <th className="text-left py-2 px-2 text-gray-200 font-semibold">Date</th>
                                <th className="text-left py-2 px-2 text-gray-200 font-semibold">Market</th>
                                <th className="text-left py-2 px-2 text-gray-200 font-semibold">Action</th>
                                <th className="text-left py-2 px-2 text-gray-200 font-semibold">Quantity</th>
                                <th className="text-left py-2 px-2 text-gray-200 font-semibold">Price</th>
                                <th className="text-left py-2 px-2 text-gray-200 font-semibold">Total</th>
                            </tr>
                            </thead>
                            <tbody>
                            {history.map((trade) => (
                                <tr key={trade.id} className="border-b border-neutral-700 hover:bg-neutral-800/50 transition-colors">
                                    <td className="py-3 px-2 text-gray-50 text-xs whitespace-nowrap">
                                        {trade.date}
                                    </td>
                                    <td className="py-3 px-2 text-gray-50 text-xs">
                                        <div className="max-w-xs truncate" title={trade.market}>
                                            {trade.market}
                                        </div>
                                    </td>
                                    <td className="py-3 px-2 text-xs whitespace-nowrap">
                                              <span className={`font-semibold ${
                                                  trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                                              }`}>
                                                  {trade.action}
                                              </span>
                                    </td>
                                    <td className="py-3 px-2 text-gray-50 text-xs whitespace-nowrap">
                                              <span className={
                                                  trade.side === 'YES' ? 'text-green-400' : 'text-red-400'
                                              }>
                                                  {trade.count} {trade.side}
                                              </span>
                                    </td>
                                    <td className="py-3 px-2 text-gray-50 text-xs whitespace-nowrap">
                                        ${trade.price.toFixed(2)}
                                    </td>
                                    <td className="py-3 px-2 text-gray-50 text-xs whitespace-nowrap">
                                        ${trade.totalCost.toFixed(2)}
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PortfolioHistory;
