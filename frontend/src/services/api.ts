// API service for backend communication

// In development, use relative URLs to leverage Vite proxy
// In production, use environment variable or fallback to localhost:8080 for auth
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}


export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

export interface DeleteAccountRequest {
  currentPassword: string | null;
}

export interface UpdatePreferencesRequest {
  notifications: boolean;
  emailUpdates: boolean;
}

export interface ResendVerificationRequest {
  email: string;
}

export interface AuthResponse {
  success?: boolean;
  message?: string;
  user?: ProfileResponse;
}

export interface ProfileResponse {
  email: string;
  fullName: string;
  createdAt: string;
  lastLoginAt: string;
  oauthProvider: string;
  profilePictureUrl: string;
  isOAuth2User: boolean;
  hasPassword: boolean;
  preferences: {
    notifications: boolean;
    emailUpdates: boolean;
  };
}

export interface SessionStatusResponse {
  authenticated: boolean;
  sessionId: string;
  userId: string | number;
  userEmail: string;
  expiresAt: string;
}

export interface DeleteAccountResponse {
  message: string;
  success: boolean;
}

//Kalshi Interfaces
export interface PortfolioFill {
  action: string;  // "buy" or "sell"
  count: number;
  created_time: string;
  fill_id: string;
  is_taker: boolean;
  market_ticker: string;
  no_price: number;
  no_price_fixed: string;
  order_id: string;
  price: number;
  side: string;  // "yes" or "no"
  ticker: string;
  trade_id: string;
  ts: number;
  yes_price: number;
  yes_price_fixed: string;
}

export interface PortfolioFillsResponse {
  fills: PortfolioFill[];
  markets_data: {
    [ticker: string]: MarketMetadata;
  };
  limit: number;
}


export interface MarketPosition {
  fees_paid: number;
  fees_paid_dollars: string;
  last_updated_ts: string;
  market_exposure: number;
  market_exposure_dollars: string;
  position: number;
  realized_pnl: number;
  realized_pnl_dollars: string;
  resting_orders_count: number;
  ticker: string;
  total_traded: number;
  total_traded_dollars: string;
}

export interface MarketMetadata {
  title: string;
  yes_sub_title: string;
  no_sub_title: string;
}

export interface PortfolioPositionsResponse {
  success: boolean;
  data: {
    market_positions: MarketPosition[];
    timestamp: number;
  };
}

export interface PortfolioBalanceResponse {
  balance: number;
  portfolio_value: number;
  timestamp: number;
}

export interface Poll {
  id: number;
  question: string;
  description: string;
  createdAt: string;
  endsAt: string;
  isActive: boolean;
  optionAText: string;
  optionAVotes: number;
  optionBText: string;
  optionBVotes: number;
}

export interface LeaderboardEntry {
  userId: string;
  fullName: string;
  profilePictureUrl: string | null;
  correctPredictionsCount: number;
}

export interface VoteRequest {
  pollId: number;
  optionVoted: string;
}

export interface VoteResponse {
  success: boolean;
  message: string;
  optionVoted: string;
  poll: Poll
}

export interface UserHasVotedRequest {
  pollId: number;
}

export interface UserHasVotedResponse {
  success: boolean;
  message: string;
  hasVoted: boolean;
  optionVoted: string;
  votedAt: string
}

export interface CandlestickData {
  end_period_ts: number;  // Unix timestamp for when this candlestick period ends
  open_interest: number;
  price: {
    close: number | null;
    high: number | null;
    low: number | null;
    open: number | null;
    previous: number | null;
  };
  volume: number;
  yes_ask: {
    close: number;  // in cents
    high: number;   // in cents
    low: number;    // in cents
    open: number;   // in cents
  };
  yes_bid: {
    close: number;
    high: number;
    low: number;
    open: number;
  };
}

export interface PollWithCandlesticks {
  id: number;
  question: string;
  description: string;
  closedAt: number[];  // [year, month, day, hour, minute, second, nanoseconds]
  optionAText: string;
  optionAVotes: number;
  optionBText: string;
  optionBVotes: number;
  seriesTicker: string;
  marketTicker: string;
}

export interface PollCandlestickData {
  poll: PollWithCandlesticks;
  candlesticks: CandlestickData[];
}

export interface HerdPerformanceResponse {
  success: boolean;
  data: PollCandlestickData[];
}


class ApiService {
  private readonly baseURL: string;
  private onSessionExpired?: () => void;
  private onRedirectToLogin?: () => void;

  constructor() {
    this.baseURL = API_BASE_URL;
  }


  setSessionExpiredHandler(handler: () => void): void {
    this.onSessionExpired = handler;
  }

  setRedirectToLoginHandler(handler: () => void): void {
    this.onRedirectToLogin = handler;
  }

  private async publicRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session handling
      ...options,
    };

    const response = await fetch(url, config);

    // Handle different response types
    const contentType = response.headers.get('content-type');
    let data;

    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      throw new Error(typeof data === 'string' ? data : data.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  }

  private async protectedRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    const config: RequestInit = {
      headers,
      credentials: 'include', // Include cookies for session-based auth
      ...options,
    };

    const response = await fetch(url, config);

    // Handle different response types
    const contentType = response.headers.get('content-type');
    let data;

    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      // Handle 401 and session expiration
      if (response.status === 401) {
        // Check if this is a session expired response
        if (typeof data === 'object' && data.type === 'session-expired') {
          if (this.onSessionExpired) {
            this.onSessionExpired();
          }
          throw new Error('SESSION_EXPIRED');
        }

        // For any 401 error, redirect to login page
        if (this.onRedirectToLogin) {
          this.onRedirectToLogin();
        }

        throw new Error('Authentication required. Please log in again.');
      }
      throw new Error(typeof data === 'string' ? data : data.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    return this.publicRequest<AuthResponse>('/api/auth/login', {
      credentials: 'include',
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    return this.publicRequest<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<ProfileResponse> {
    return this.protectedRequest<ProfileResponse>('/api/profile/get', {
      method: 'GET',
    });
  }

  // async verifyEmail(token: string): Promise<AuthResponse> {
  //   return this.publicRequest<AuthResponse>(`/api/auth/verify-email?token=${token}`, {
  //     method: 'GET',
  //   });
  // }
  //
  // async resendVerification(request: ResendVerificationRequest): Promise<string> {
  //   return this.publicRequest<string>(`/api/auth/resend-verification`, {
  //     method: 'POST',
  //     body: JSON.stringify(request),
  //   });
  // }
  //
  // async forgotPassword(request: ForgotPasswordRequest): Promise<AuthResponse> {
  //   return this.publicRequest<AuthResponse>(`/api/auth/forgot-password`, {
  //     method: 'POST',
  //     body: JSON.stringify(request),
  //   });
  // }
  //
  // async resetPassword(token: string, newPassword: string, confirmPassword: string): Promise<{ message: string }> {
  //   return this.publicRequest<{ message: string }>(`/api/auth/reset-password`, {
  //     method: 'POST',
  //     body: JSON.stringify({ token, newPassword, confirmPassword }),
  //   });
  // }
  //
  // async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
  //   return this.protectedRequest<{ message: string }>('/api/auth/change-password', {
  //     method: 'PUT',
  //     body: JSON.stringify(data),
  //   });
  // }

  async deleteAccountDirect(request: DeleteAccountRequest): Promise<DeleteAccountResponse> {
    return this.protectedRequest<DeleteAccountResponse>('/api/profile/delete-account/direct', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Session management endpoints
  async checkSession(): Promise<SessionStatusResponse> {
    return this.protectedRequest<SessionStatusResponse>('/api/auth/session', {
      method: 'GET',
    });
  }

  async destroySession(): Promise<{ message: string }> {
    return this.protectedRequest<{ message: string }>('/api/auth/logout', {
      method: 'POST',
    });
  }

  // Portfolio positions endpoint
  async getPortfolioPositions(): Promise<PortfolioPositionsResponse> {
    return this.protectedRequest<PortfolioPositionsResponse>('/api/python/portfolio/positions', {
      method: 'GET',
    });
  }

  async getPortfolioFills(limit: number = 100): Promise<ApiResponse<PortfolioFillsResponse>> {
    return this.protectedRequest<ApiResponse<PortfolioFillsResponse>>(
        `/api/python/portfolio/fills?limit=${limit}`,
        {
          method: 'GET',
        }
    );
  }

  async getPortfolioBalance(): Promise<ApiResponse<PortfolioBalanceResponse>> {
    return this.protectedRequest<ApiResponse<PortfolioBalanceResponse>>("/api/python/portfolio/balance", {
      method: "GET"
    })
  }

  async getLatestPoll(): Promise<Poll> {
    return this.publicRequest<Poll>("/api/polls", {
      method: "GET"
    })
  }

  async submitVote(request : VoteRequest): Promise<VoteResponse> {
    return this.protectedRequest<VoteResponse>("/api/polls/vote", {
      method: "POST",
      body: JSON.stringify(request)
    })
  }

  async getUserVote(request : UserHasVotedRequest): Promise<UserHasVotedResponse> {
    const pollId = request.pollId;
    return this.protectedRequest<UserHasVotedResponse>(`/api/polls/${pollId}/user-vote`, {
      method: "GET"
    })
  }

  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    return this.publicRequest<LeaderboardEntry[]>("/api/polls/leaderboard", {
      method: "GET"
    })
  }

  async getHerdPerformance(): Promise<HerdPerformanceResponse> {
    return this.publicRequest<HerdPerformanceResponse>("/api/python/polls/history-with-candlesticks", {
      method: "GET"
    })
  }

}

export const apiService = new ApiService();