import React, { useEffect, useState } from 'react';
import { apiService } from "../services/api";
import AnimatedCounter from './AnimatedCounter';

interface PerformanceHeroProps {
    startingAmount: number;
    animationDuration?: number;
    className?: string;
    showReturnPercentage?: boolean;
    showLiveIndicator?: boolean;
    isLoading?: boolean;
}

const PerformanceHero: React.FC<PerformanceHeroProps> = ({
    startingAmount,
    animationDuration = 3000,
    className = "",
    showReturnPercentage = true,
}) => {

    const [endedValue, setEndedValue] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [returnPercentage, setReturnPercentage] = useState<string>("");
    const [isProfit, setIsProfit] = useState<boolean>(false);

    useEffect(() => {
        async function fetchPortfolioBalance() {
            try {
                setLoading(true);
                const response = await apiService.getPortfolioBalance();

                if (response.success) {
                    const balance = (response.data.portfolio_value + response.data.balance) / 100;
                    setEndedValue(balance);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load portfolio balance');
                console.error('Failed to fetch portfolio balance:', err);
            } finally {
                setLoading(false);
            }
        }

        fetchPortfolioBalance();
    }, []);

    useEffect(() => {
        setReturnPercentage(((endedValue - startingAmount) / startingAmount * 100).toFixed(1));
        setIsProfit(endedValue > startingAmount);
    }, [endedValue, startingAmount]);

    if (loading) {
        return (
            <div className={`text-center mb-12 ${className}`}>
                <div className="relative">
                    <div className="absolute inset-0 blur-xl"></div>
                    <div className="relative p-8">
                        <div className="flex flex-col items-center gap-4">
                            <div className="h-7 md:h-8 bg-neutral-700 rounded w-64 animate-pulse"></div>
                            <div className="flex items-center gap-3">
                                <div className="h-7 md:h-8 bg-neutral-700 rounded w-32 animate-pulse"></div>
                                <div className="h-12 md:h-16 bg-neutral-700 rounded w-48 animate-pulse"></div>
                            </div>
                            {showReturnPercentage && (
                                <div className="h-5 bg-neutral-700 rounded w-40 animate-pulse mt-2"></div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className={`text-center mb-12 ${className}`}>
                <div className="relative p-8">
                    <div className="text-red-400">Error loading balance: {error}</div>
                </div>
            </div>
        );
    }

    return (
        <div className={`text-center mb-12 ${className}`}>
            <div className="relative">
                <div className="absolute inset-0 blur-xl"></div>
                <div className="relative p-8">
                    <div className="flex flex-col items-center gap-4">
                        <p className="text-xl md:text-2xl text-gray-300 font-medium">
                            Started off with <span className="font-bold">${startingAmount.toLocaleString()}</span>
                        </p>
                        <div className="flex items-center gap-3">
                            <p className="text-xl md:text-2xl text-gray-300 font-medium">
                                currently at
                            </p>
                            <div className={`text-4xl md:text-6xl font-bold ${endedValue > 500 ? 'bg-green-500' : 'bg-red-500'} bg-clip-text text-transparent`}>
                                <AnimatedCounter
                                    targetValue={endedValue}
                                    prefix="$"
                                    duration={animationDuration}
                                    className="font-mono"
                                />
                            </div>
                        </div>
                        {showReturnPercentage && (
                            <div className="flex items-center gap-2 mt-2">
                                <p className={`text-sm font-semibold ${
                                    isProfit ? 'text-green-400' : 'text-red-400'
                                }`}>
                                    {isProfit ? '(+' : '('}{returnPercentage}% Total Return)
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PerformanceHero;
