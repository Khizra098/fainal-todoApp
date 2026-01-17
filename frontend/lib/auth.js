'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from './api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on initial load
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (storedToken) {
      setToken(storedToken);
      // Optionally verify token or fetch user data here
      // For now, we'll just set a dummy user object
      setUser({ id: 1, email: 'user@example.com' }); // This would typically come from token decode or API call
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { token: newToken } = response.data;

      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser({ id: 1, email }); // This would typically come from the response

      return response;
    } catch (error) {
      throw error;
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await authAPI.register({ name, email, password });
      const { token: newToken } = response.data;

      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser({ id: 1, email, name });

      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const updateUserProfile = async (userData) => {
    try {
      const response = await authAPI.updateUserProfile(userData);
      const updatedUser = response.data.user || { ...user, ...userData };

      // Update the local user state
      setUser(updatedUser);

      return response;
    } catch (error) {
      throw error;
    }
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    register,
    logout,
    updateUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}