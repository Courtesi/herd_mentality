import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, BaselineSeries } from 'lightweight-charts';
import { apiService, type MarketPosition } from "../services/api";

interface ChartDataPoint {
    time: string;
    value: number;
}

interface ChartColors {
    backgroundColor?: string;
    textColor?: string;
    gridColor?: string;
}

interface ChartProps {
    colors?: ChartColors;
}

const ChartComponent: React.FC<ChartProps> = (props) => {
    const {
        colors: {
            backgroundColor = '#D6D3D1',
            textColor = 'black',
            gridColor = "#62748E",
        } = {},
    } = props;

    const [dataPoints, setDataPoints] = useState<ChartDataPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const chartContainerRef = useRef<HTMLDivElement | null>(null);

    const transformPositionsToData = (positions: MarketPosition[]): ChartDataPoint[] => {
        const merged = new Map<string, number>();

        for (const p of positions) {
            const time = p.last_updated_ts.split("T")[0];
            const deltaDollars = (p.realized_pnl - p.fees_paid) / 100;

            merged.set(time, (merged.get(time) || 0) + deltaDollars);
        }

        const sorted = Array.from(merged.entries())
            .map(([time, delta]) => ({ time, delta }))
            .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());

        const baseValue = 500;
        let runningTotal = baseValue;
        const cumulative: ChartDataPoint[] = [];

        cumulative.push({ time: "2025-10-22", value: baseValue });

        for (const p of sorted) {
            runningTotal += p.delta;
            cumulative.push({ time: p.time, value: runningTotal });
        }

        return cumulative;
    };

    useEffect(() => {
        async function fetchMarketPositions() {
            try {
                setLoading(true);
                const response = await apiService.getPortfolioPositions();

                if (response.success) {
                    const marketPositions = response.data.market_positions;
                    const dataPoints = transformPositionsToData(marketPositions);
                    setDataPoints(dataPoints);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load chart data');
                console.error('Failed to fetch chart data:', err);
            } finally {
                setLoading(false);
            }
        }

        fetchMarketPositions();
    }, []);

    useEffect(() => {
        const container = chartContainerRef.current;
        if (!container) {
            return;
        }
        const handleResize = () => {
            chart.applyOptions({width: container.clientWidth});
        };

        const chart = createChart(container, {
            layout: {
                background: {type: ColorType.Solid, color: backgroundColor},
                textColor,
            },
            width: container.clientWidth,
            height: 350,
            grid: {
                vertLines: {color: gridColor},
                horzLines: {color: gridColor}
            }
        });
        chart.timeScale().fitContent();

        const newSeries = chart.addSeries(BaselineSeries,
            {
                baseValue: { type: 'price', price: 500 },
                topLineColor: 'rgba( 38, 166, 154, 1)',
                topFillColor1: 'rgba( 38, 166, 154, 0.28)',
                topFillColor2: 'rgba( 38, 166, 154, 0.05)',
                bottomLineColor: 'rgba( 239, 83, 80, 1)',
                bottomFillColor1: 'rgba( 239, 83, 80, 0.05)',
                bottomFillColor2: 'rgba( 239, 83, 80, 0.28)'
            });
        newSeries.setData(dataPoints);

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [dataPoints, backgroundColor, textColor, gridColor]);

    if (loading) {
        return (
            <div className="bg-dark-500 rounded-lg p-6 flex items-center justify-center">
                <div className="text-gray-400">Loading portfolio history...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-dark-500 rounded-lg p-6 flex items-center justify-center">
                <div className="text-red-400">Error: {error}</div>
            </div>
        );
    }

    return (
        <div
            ref={chartContainerRef}
        />
    );
};

export default ChartComponent;
