import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, type IChartApi, CandlestickSeries } from 'lightweight-charts';
import type {PollCandlestickData, CandlestickData} from '../services/api';

interface Props {
  pollData: PollCandlestickData;
}

export const PollCandlestickChart: React.FC<Props> = ({ pollData }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  // Format LocalDateTime array to readable date
  const formatClosedDate = (closedAt: number[]): string => {
    const [year, month, day, hour, minute] = closedAt;
    const date = new Date(year, month - 1, day, hour, minute);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Transform Kalshi candlestick data (cents to dollars)
  const transformCandlestickData = (candlesticks: CandlestickData[]) => {
    return candlesticks
      .filter(candle => candle.yes_ask) // Filter out any without yes_ask data
      .map(candle => ({
        time: candle.end_period_ts as any, // Use end_period_ts as time
        open: candle.yes_ask.open / 100,   // Convert cents to dollars
        high: candle.yes_ask.high / 100,
        low: candle.yes_ask.low / 100,
        close: candle.yes_ask.close / 100
      }));
  };

  useEffect(() => {
    if (!chartContainerRef.current || pollData.candlesticks.length === 0) return;

    const container = chartContainerRef.current;

    const chartOptions = {
      layout: {
        textColor: '#d1d5db', // text-gray-300
        background: { type: ColorType.Solid, color: '#3A3A3A' } // bg-dark-500
      },
      width: container.clientWidth,
      height: 300,
      grid: {
        vertLines: { color: '#525252' },
        horzLines: { color: '#525252' }
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false
      }
    };

    const chart = createChart(container, chartOptions);

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350'
    });

    const transformedData = transformCandlestickData(pollData.candlesticks);
    candlestickSeries.setData(transformedData);
    chart.timeScale().fitContent();

    chartRef.current = chart;

    return () => {
      chart.remove();
      chartRef.current = null;
    };
  }, [pollData]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const { poll } = pollData;

  return (
    <div className="bg-neutral-700 rounded-lg p-4">
      {/* Poll Question Title */}
      <h3 className="text-sm font-semibold text-gray-50 mb-2 line-clamp-2">
        {poll.question}
      </h3>

      {/* Investment Start Date */}
      <div className="text-xs text-gray-400 mb-2">
        Investment Started: {formatClosedDate(poll.closedAt)}
      </div>

      {/* Vote Counts */}
      <div className="text-xs text-gray-300 mb-3 flex gap-4">
        <span className="font-medium">{poll.optionAText}: <span className="text-gray-400">{poll.optionAVotes} votes</span></span>
        <span className="font-medium">{poll.optionBText}: <span className="text-gray-400">{poll.optionBVotes} votes</span></span>
      </div>

      {/* Candlestick Chart */}
      <div ref={chartContainerRef} className="h-[300px]" />
    </div>
  );
};
