import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {apiService, type Poll, type LeaderboardEntry, type VoteRequest} from "../services/api";
import AuthModal from './AuthModal';

const CombinedVotingLeaderboard: React.FC = () => {
    const { isAuthenticated } = useAuth();
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const [poll, setPoll] = useState<Poll | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userVote, setUserVote] = useState<'A' | 'B' | null>(null);
    const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([]);
    const [leaderboardLoading, setLeaderboardLoading] = useState(true);
    const [leaderboardError, setLeaderboardError] = useState<string | null>(null);
    const [timeRemaining, setTimeRemaining] = useState<{
        days: number;
        hours: number;
        minutes: number;
        seconds: number;
    } | null>(null);

    useEffect(() => {
        async function fetchLatestPoll() {
            try {
                setLoading(true);
                const pollData = await apiService.getLatestPoll();
                console.log(pollData);
                setPoll(pollData);

                // If user is authenticated, check if they've already voted
                if (isAuthenticated && pollData.id) {
                    try {
                        const voteStatus = await apiService.getUserVote({pollId: pollData.id});
                        if (voteStatus.hasVoted && voteStatus.optionVoted) {
                            setUserVote(voteStatus.optionVoted as 'A' | 'B');
                        }
                    } catch (err) {
                        // If error checking vote status, just continue (user might not have voted)
                        console.log('Could not fetch vote status:', err);
                    }
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load poll');
                console.error('Failed to fetch poll:', err);
            } finally {
                setLoading(false);
            }
        }

        async function fetchLeaderboard() {
            try {
                setLeaderboardLoading(true);
                const leaderboard = await apiService.getLeaderboard();
                setLeaderboardData(leaderboard);
            } catch (err) {
                setLeaderboardError(err instanceof Error ? err.message : 'Failed to load leaderboard');
                console.error('Failed to fetch leaderboard:', err);
            } finally {
                setLeaderboardLoading(false);
            }
        }

        fetchLatestPoll();
        fetchLeaderboard();
    }, [isAuthenticated]);

    // Countdown timer effect
    useEffect(() => {
        if (!poll || !poll.isActive) {
            setTimeRemaining(null);
            return;
        }

        const calculateTimeRemaining = () => {
            const now = new Date().getTime();

            // Handle both array format and ISO string format from Spring Boot
            let endDate: Date;
            if (Array.isArray(poll.endsAt)) {
                // Spring Boot LocalDateTime array format: [year, month, day, hour, minute, second, nanos]
                const [year, month, day, hour, minute, second] = poll.endsAt as number[];
                endDate = new Date(year, month - 1, day, hour, minute, second);
            } else {
                // ISO string format
                endDate = new Date(poll.endsAt);
            }

            const end = endDate.getTime();

            // Check if date parsing was successful
            if (isNaN(end)) {
                console.error('Invalid endsAt date format:', poll.endsAt);
                setTimeRemaining(null);
                return;
            }

            const diff = end - now;

            if (diff <= 0) {
                setTimeRemaining(null);
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            // Ensure all values are valid numbers
            if (!isNaN(days) && !isNaN(hours) && !isNaN(minutes) && !isNaN(seconds)) {
                setTimeRemaining({ days, hours, minutes, seconds });
            }
        };

        calculateTimeRemaining();
        const interval = setInterval(calculateTimeRemaining, 1000);

        return () => clearInterval(interval);
    }, [poll]);

    const handleVote = async (option: 'A' | 'B') => {
        if (!isAuthenticated) {
            setIsAuthModalOpen(true);
            return;
        }

        if (userVote || !poll) return;

        try {
            // Submit vote to backend
            const voteRequest : VoteRequest = {pollId: poll.id, optionVoted: option};
            const response = await apiService.submitVote(voteRequest);

            // Update local state with response
            setUserVote(option);
            setPoll(response.poll);
        } catch (err) {
            console.error('Failed to submit vote:', err);
            // Show error message if vote failed
            const errorMessage = err instanceof Error ? err.message : 'Failed to submit vote';
            alert(errorMessage);
        }
    };

    const handleAuthClick = () => {
        setIsAuthModalOpen(true);
    };

    return (
        <>
            <div className="bg-dark-500 rounded-lg p-4 shadow-lg h-[460px] flex flex-col">
                {/* Voting Section - Top */}
                <div className="mb-4 p-2 border-b border-neutral-600 relative">
                    <h3 className=" mb-3 text-center">
                        <div className="text-2xl bg-gradient-to-r from-cyan-500 to-pink-500 font-bold inline-block text-transparent bg-clip-text">Vote With My Money</div>
                    </h3>

                    {loading ? (
                        <div className="text-center text-gray-400 py-8">Loading poll...</div>
                    ) : error || !poll ? (
                        <div className="text-center text-gray-400 py-8">
                            <p className="font-semibold">Poll Unavailable</p>
                            <p className="text-xs mt-2">Check back soon for the next poll!</p>
                        </div>
                    ) : (
                        <>
                            {/* Poll Ended Notice */}
                            {!poll.isActive && (
                                <div className="mb-3 text-center bg-yellow-900/20 border border-yellow-600/50 rounded-lg p-2">
                                    <p className="text-xs text-yellow-400 font-semibold">⏰ This poll has ended</p>
                                    <p className="text-xs text-yellow-500/80 mt-1">New poll coming soon!</p>
                                </div>
                            )}

                            <div className="mb-4 text-center">
                                <div className="flex items-center justify-center gap-2">
                                    <p className="text-sm text-gray-300">{poll.question}</p>
                                    {(userVote) && (
                                        <span className="text-sm font-mono font-semibold">
                                            <span className="text-green-400">{poll.optionAVotes}</span>
                                            <span className="text-gray-400 mx-1">-</span>
                                            <span className="text-red-400">{poll.optionBVotes}</span>
                                        </span>
                                    )}
                                </div>

                                {/* Countdown Timer */}
                                {poll.isActive && timeRemaining && (
                                    <div className="flex items-center justify-center gap-2 mt-2">
                                        <span className="text-xs text-gray-400">Ends in:</span>
                                        <span className="countdown font-mono text-gray-50 bg-linear-to-r from-purple-500 to-pink-500 p-2 rounded-lg">
                                            <span style={{ '--value': timeRemaining.days } as React.CSSProperties} aria-live="polite" aria-label={timeRemaining.days.toString()}></span>:
                                            <span style={{ '--value': timeRemaining.hours } as React.CSSProperties} aria-live="polite" aria-label={timeRemaining.hours.toString()}></span>:
                                            <span style={{ '--value': timeRemaining.minutes } as React.CSSProperties} aria-live="polite" aria-label={timeRemaining.minutes.toString()}></span>:
                                            <span style={{ '--value': timeRemaining.seconds } as React.CSSProperties} aria-live="polite" aria-label={timeRemaining.seconds.toString()}></span>
                                        </span>
                                    </div>
                                )}
                            </div>

                            <div className={`flex gap-2 transition-all duration-300`}>
                                <button
                                    onClick={() => handleVote('A')}
                                    disabled={userVote !== null || !isAuthenticated}
                                    className={`flex-1 p-3 rounded-lg border-2 transition-all duration-200 w-80 ${
                                        userVote === 'A'
                                            ? 'bg-green-600/20 border-green-500 text-green-300 shadow-lg shadow-green-500/20'
                                            : userVote === 'B'
                                            ? 'bg-neutral-800/50 border-neutral-600 text-gray-500 cursor-not-allowed'
                                            : 'bg-neutral-800 border-neutral-600 text-gray-50 hover:border-green-500 hover:bg-green-600/10 hover:shadow-md cursor-pointer'
                                    }`}
                                >
                                    <div className="text-center">
                                        <div className="font-semibold text-sm">{poll.optionAText}</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleVote('B')}
                                    disabled={userVote !== null || !isAuthenticated}
                                    className={`flex-1 p-3 rounded-lg border-2 transition-all duration-200 w-80 ${
                                        userVote === 'B'
                                            ? 'bg-red-600/20 border-red-500 text-red-300 shadow-lg shadow-red-500/20'
                                            : userVote === 'A'
                                            ? 'bg-neutral-800/50 border-neutral-600 text-gray-500 cursor-not-allowed'
                                            : 'bg-neutral-800 border-neutral-600 text-gray-50 hover:border-red-500 hover:bg-red-600/10 hover:shadow-md cursor-pointer'
                                    }`}
                                >
                                    <div className="text-center">
                                        <div className="font-semibold text-sm">{poll.optionBText}</div>
                                    </div>
                                </button>
                            </div>

                            {/* Authentication Overlay - Over entire voting section */}
                            {!isAuthenticated && (
                                <div className="absolute inset-0 flex items-center justify-center bg-neutral-900/60 rounded-lg">
                                    <button
                                        onClick={handleAuthClick}
                                        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium shadow-lg cursor-pointer"
                                    >
                                        🔒 Sign In To Vote
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Leaderboard Section - Bottom */}
                <div className="flex-1 flex flex-col min-h-0">
                    <h3 className="text-base font-bold text-gray-50 mb-3 text-center">Top Predictors</h3>
                    <div className="flex-1 overflow-y-auto space-y-2 min-h-0">
                        {leaderboardLoading ? (
                            <div className="flex items-center justify-center h-full">
                                <div className="text-gray-400 text-sm">Loading leaderboard...</div>
                            </div>
                        ) : leaderboardError ? (
                            <div className="flex items-center justify-center h-full">
                                <div className="text-red-400 text-sm">{leaderboardError}</div>
                            </div>
                        ) : leaderboardData.length === 0 ? (
                            <div className="flex items-center justify-center h-full">
                                <div className="text-gray-400 text-sm">No predictions yet</div>
                            </div>
                        ) : (
                            leaderboardData.map((entry, index) => {
                                const rank = index + 1;
                                const firstInitial = entry.fullName.charAt(0).toUpperCase();

                                return (
                                    <div key={entry.userId} className="flex items-center justify-between p-2 bg-neutral-800 rounded flex-shrink-0">
                                        <div className="flex items-center gap-2">
                                            {entry.profilePictureUrl ? (
                                                <img
                                                    src={entry.profilePictureUrl}
                                                    alt={entry.fullName}
                                                    className={`
                                                        w-6 h-6 rounded-full object-cover
                                                        ${rank === 1 ? 'ring-2 ring-yellow-400' :
                                                          rank === 2 ? 'ring-2 ring-gray-300' :
                                                          rank === 3 ? 'ring-2 ring-orange-400' : ''}
                                                    `}
                                                />
                                            ) : (
                                                <div className={`
                                                    w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                                                    ${rank === 1 ? 'bg-yellow-400 text-yellow-900' :
                                                      rank === 2 ? 'bg-gray-300 text-gray-700' :
                                                      rank === 3 ? 'bg-orange-400 text-orange-900' :
                                                      'bg-neutral-600 text-gray-50'}
                                                `}>
                                                    {firstInitial}
                                                </div>
                                            )}
                                            <div className="text-xs text-gray-50">{entry.fullName}</div>
                                        </div>
                                        <div className="text-xs text-gray-200">{entry.correctPredictionsCount} wins</div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
            </div>

            {/* Authentication Modal */}
            <AuthModal
                isOpen={isAuthModalOpen}
                onClose={() => setIsAuthModalOpen(false)}
                initialMode="login"
            />
        </>
    );
};

export default CombinedVotingLeaderboard;
