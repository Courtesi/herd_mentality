import React from 'react';
import { Toaster } from "react-hot-toast";
import { TradingProvider } from '../contexts/TradingContext';
import SocialButtons from '../components/SocialButtons';
import PerformanceHero from '../components/PerformanceHero';
import AutoTraderLive from '../components/AutoTraderLive';
import CombinedVotingLeaderboard from '../components/CombinedVotingLeaderboard';
import PortfolioHistory from '../components/PortfolioHistory';
import { HerdPerformance } from '../components/HerdPerformance';
import ChartComponent from '../components/ChartComponent';
import ProfileDropdown from '../components/ProfileDropdown';

// Main Home Component - Wrapped with TradingProvider
const Home: React.FC = () => {
    return (
        <TradingProvider>
            <div className="min-h-screen">
                <Toaster
                    position="top-left"
                    reverseOrder={false}
                />

                {/* Profile Dropdown - Top Right */}
                <ProfileDropdown />

                {/* Main Content Container */}
                <div className="container mx-auto px-4 py-8">
                    {/* Header Section: Title and Social Icons */}
                    <div className="text-center mb-8">
                        <h1 className="text-7xl font-bold text-gray-50 mb-4">Herd Mentality</h1>
                        <SocialButtons />
                    </div>

                    {/* Performance Hero Section */}
                    <PerformanceHero
                    startingAmount={500}
                    />

                    {/* First Section: Auto Trader Live + Combined Voting/Leaderboard */}
                    <div className="grid grid-cols-1 lg:grid-cols-10 gap-6 mb-8">
                        {/* Auto Trader Live - 70% on desktop, full width on mobile */}
                        <div className="lg:col-span-7">
                            <AutoTraderLive />
                        </div>

                        {/* Combined Voting/Leaderboard - 30% on desktop, full width on mobile */}
                        <div className="lg:col-span-3">
                            <CombinedVotingLeaderboard />
                        </div>
                    </div>

                    {/* Second Section: Portfolio History + Portfolio Chart */}
                    <div className="grid grid-cols-1 lg:grid-cols-10 gap-6 mb-8">
                        {/* Portfolio History - 60% on desktop, full width on mobile */}
                        <div className="lg:col-span-6">
                            <PortfolioHistory />
                        </div>

                        {/* Portfolio Chart - 40% on desktop, full width on mobile */}
                        <div className="lg:col-span-4">
                            <div className="bg-dark-500 rounded-lg h-[460px] flex flex-col p-6">
                                <h2 className="text-lg font-bold text-gray-50 mb-4 text-center">Portfolio Performance</h2>
                                <div className="flex-1 content-center">
                                    <ChartComponent colors = {
                                        {
                                            backgroundColor: "#323232",
                                            textColor: "#FAFAF9",
                                            gridColor: "#FAFAF9"
                                        }
                                    }/>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Third Section: Herd Performance */}
                    <div className="mb-8">
                        <HerdPerformance />
                    </div>
                </div>
            </div>
        </TradingProvider>
    );
};

export default Home;