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
      // Fetch user details from API
      fetchUserDetailsFromAPI();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserDetailsFromAPI = async () => {
    try {
      const response = await authAPI.getUserDetails();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user details:', error);
      // Clear token if unauthorized
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      const { token: newToken } = response.data;

      localStorage.setItem('token', newToken);
      setToken(newToken);

      // Fetch user details after successful login
      const userDetailsResponse = await authAPI.getUserDetails();
      setUser(userDetailsResponse.data);

      return response;
    } catch (error) {
      // Extract error message from response or provide default
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Login failed. Please try again.';

      // Create a new error with the better message
      const enhancedError = new Error(errorMessage);
      enhancedError.status = error.response?.status;
      enhancedError.response = error.response;

      throw enhancedError;
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await authAPI.register({ name, email, password });
      const { token: newToken } = response.data;

      localStorage.setItem('token', newToken);
      setToken(newToken);

      // Fetch user details after successful registration
      const userDetailsResponse = await authAPI.getUserDetails();
      setUser(userDetailsResponse.data);

      return response;
    } catch (error) {
      // Extract error message from response or provide default
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Registration failed. Please try again.';

      // Create a new error with the better message
      const enhancedError = new Error(errorMessage);
      enhancedError.status = error.response?.status;
      enhancedError.response = error.response;

      throw enhancedError;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const updateUserData = (userData) => {
    setUser(prevUser => ({ ...prevUser, ...userData }));
  };

  const updateUserProfile = async (userData) => {
    try {
      const response = await authAPI.updateUserProfile(userData);
      const updatedUser = response.data.user || { ...user, ...userData };

      // Update the local user state
      setUser(updatedUser);

      return response;
    } catch (error) {
      // Extract error message from response or provide default
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to update profile. Please try again.';

      // Create a new error with the better message
      const enhancedError = new Error(errorMessage);
      enhancedError.status = error.response?.status;
      enhancedError.response = error.response;

      throw enhancedError;
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
    updateUserProfile,
    updateUserData
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