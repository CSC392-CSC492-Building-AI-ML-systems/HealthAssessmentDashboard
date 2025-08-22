'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api/auth';
import { usersApi } from '@/lib/api/users';
import type { UserProfile, SignupPayload, UserCredentials } from '@/lib/api/types';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  organization_id?: number;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  signup: (userData: SignupData) => Promise<boolean>;
  refreshUser: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

interface SignupData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  organization_id?: number;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = async () => {
    try {
      setIsLoading(true);
      const response = await usersApi.getCurrentUser();
      if (response.data) {
        setUser(response.data);
        setIsAuthenticated(true);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      const response = await usersApi.getCurrentUser();
      if (response.data) {
        setUser(response.data);
        setIsAuthenticated(true);
      }
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const credentials: UserCredentials = { email, password };
      const response = await authApi.login(credentials);

      if (response.data) {
        // Set access token
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
        }
        
        if (response.data.user) {
          setUser(response.data.user);
          setIsAuthenticated(true);
        } else {
          await refreshUser();
        }
        
        return true;
      } else {
        console.error('Login failed:', response.error);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData: SignupData): Promise<boolean> => {
    try {
      setIsLoading(true);
      const signupPayload: SignupPayload = {
        email: userData.email,
        password: userData.password,
        first_name: userData.first_name,
        last_name: userData.last_name,
        organization_id: userData.organization_id || null,
      };

      const response = await authApi.signup(signupPayload);

      if (response.data) {
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
        }
        
        if (response.data.user) {
          setUser(response.data.user);
          setIsAuthenticated(true);
        } else {
          await refreshUser();
        }
        
        return true;
      } else {
        console.error('Signup failed:', response.error);
        return false;
      }
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Skip auth check on public pages
    const publicPages = ['/signup', '/login'];
    const currentPath = window.location.pathname;
    
    if (!publicPages.includes(currentPath)) {
      checkAuth();
    } else {
      setIsLoading(false);
    }
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    signup,
    refreshUser,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
