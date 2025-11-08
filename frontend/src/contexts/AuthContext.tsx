import React, {createContext, type ReactNode, useContext, useEffect, useState} from 'react';
import {apiService, type ProfileResponse, type SessionStatusResponse} from '../services/api';
import type {AuthContextType} from '../types/auth';

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<ProfileResponse | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  // @ts-ignore
  const [sessionInfo, setSessionInfo] = useState<SessionStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [hasInitialized, setHasInitialized] = useState<boolean>(false);

  // Check session validity (fast, lightweight)
  const checkSession = async (): Promise<SessionStatusResponse | null> => {
    try {
      return await apiService.checkSession(); //sessionData
    } catch (error) {
      // console.log('Session check failed:', error);
      return null;
    }
  };

  // Load full user profile (slower, detailed)
  const loadUserProfile = async (): Promise<ProfileResponse | null> => {
    try {
      const userData = await apiService.getCurrentUser();

      // console.log(`loading User Profile?: ${userData}`);

      return { //userProfile
        email: userData.email || "",
        fullName: userData.fullName || "",
        createdAt: userData.createdAt || "",
        lastLoginAt: userData.lastLoginAt || "",
        oauthProvider: userData.oauthProvider || "",
        profilePictureUrl: userData.profilePictureUrl || "",
        isOAuth2User: userData.isOAuth2User || false,
        hasPassword: userData.hasPassword || false,
        preferences: {
          notifications: userData.preferences?.notifications ?? true,
          emailUpdates: userData.preferences?.emailUpdates ?? true,
        }
      };
    } catch (error) {
      console.log('Profile load failed:', error);
      throw error;
    }
  };

  const login = async (credentials: { email: string; password: string }): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);

      const loginData = await apiService.login(credentials);

      if (loginData.success) {
        // console.log("upcoming user data");
        // console.log(loginData.user);
        setUser(loginData.user || null);
        setIsAuthenticated(true);
      }

      // const userProfile = await loadUserProfile();
      // if (userProfile) {
      //   setUser(userProfile);
      // }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await apiService.destroySession();
    } catch (err) {
      console.error('Failed to destroy session on server:', err);
    } finally {
      setUser(null);
      setSessionInfo(null);
      setIsAuthenticated(false);
      setError(null);
    }
  };

  const updateUser = (userData: Partial<ProfileResponse>): void => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
    }
  };

  const refreshUser = async (): Promise<void> => {
    if (!isAuthenticated) return;

    try {
      setIsLoading(true);
      setError(null);
      const userProfile = await loadUserProfile();
      if (userProfile?.email) {
        setUser(userProfile);
      }
    } catch (err) {
      if (err instanceof Error && err.message === 'SESSION_EXPIRED') {
        handleSessionExpired();
      } else {
        setError(err instanceof Error ? err.message : 'Failed to refresh user data');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionExpired = (): void => {
    setUser(null);
    setSessionInfo(null);
    setIsAuthenticated(false);
    setError('Your session has expired. Please log in again.');

    // Automatically redirect to log-in after clearing state
  };


  // Initialize auth on mount using two-step pattern
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setIsLoading(true);

        // Step 1: Fast session check
        const sessionData = await checkSession();
        if (sessionData && sessionData.authenticated) {
          setSessionInfo(sessionData);
          setIsAuthenticated(true);

          // Step 2: Load full profile (in background, don't block initialization)
          loadUserProfile()
            .then(userProfile => {
              if (userProfile?.email) {
                setUser(userProfile);
              }
            })
            .catch(profileError => {
              console.log('Profile load failed during initialization:', profileError);
              // User is still authenticated even if profile load fails
            });
        }
      } catch (err) {
        console.error('Failed to initialize auth:', err);
        // Session doesn't exist or expired, user remains unauthenticated
      } finally {
        setIsLoading(false);
        setHasInitialized(true);
      }
    };

    // Set up global session expiration and redirect handlers
    apiService.setSessionExpiredHandler(handleSessionExpired);
    // apiService.setRedirectToLoginHandler(redirectToLogin);

    initializeAuth();
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      isLoading,
      error,
      hasInitialized,
      login,
      logout,
      updateUser,
      refreshUser,
      handleSessionExpired
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};