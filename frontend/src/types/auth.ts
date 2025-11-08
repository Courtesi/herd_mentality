import type {ProfileResponse} from "../services/api.ts";

export interface AuthContextType {
  user: ProfileResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  hasInitialized: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: Partial<ProfileResponse>) => void;
  refreshUser: () => Promise<void>;
  handleSessionExpired: () => void;
}