/**
 * Unit tests for the Verification Dashboard component.
 *
 * This module contains unit tests for the frontend verification dashboard,
 * testing UI rendering, state management, and API interactions.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import VerificationDashboard from '@/app/verification/page';

// Mock the auth context
jest.mock('@/lib/auth', () => ({
  useAuth: () => ({ isAuthenticated: true, isLoading: false })
}));

// Mock router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

describe('VerificationDashboard', () => {
  let mockAxios;

  beforeEach(() => {
    mockAxios = new MockAdapter(axios);

    // Mock the features API call
    mockAxios.onGet('/api/v1/verification/features').reply(200, [
      {
        id: 1,
        name: 'Login Feature',
        description: 'User authentication functionality',
        specification_reference: 'SPEC-AUTH-001'
      },
      {
        id: 2,
        name: 'Todo Creation',
        description: 'Ability to create new todo items',
        specification_reference: 'SPEC-TODO-001'
      }
    ]);
  });

  afterEach(() => {
    mockAxios.restore();
  });

  test('renders dashboard header correctly', async () => {
    await act(async () => {
      render(<VerificationDashboard />);
    });

    expect(screen.getByText('Feature Verification Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Monitor and verify all implemented features against original specifications')).toBeInTheDocument();
  });

  test('displays loading state initially', async () => {
    render(<VerificationDashboard />);

    expect(screen.getByText('Loading verification dashboard...')).toBeInTheDocument();
  });

  test('fetches and displays features', async () => {
    await act(async () => {
      render(<VerificationDashboard />);
    });

    // Wait for features to load
    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
      expect(screen.getByText('Todo Creation')).toBeInTheDocument();
    });

    expect(screen.getByText('Login Feature')).toBeInTheDocument();
    expect(screen.getByText('Todo Creation')).toBeInTheDocument();
  });

  test('shows feature details', async () => {
    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    const featureElement = screen.getByText('Login Feature');
    const parentElement = featureElement.closest('li');

    expect(parentElement).toHaveTextContent('User authentication functionality');
    expect(parentElement).toHaveTextContent('Specification: SPEC-AUTH-001');
  });

  test('initial status is pending', async () => {
    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Check that the status badge shows 'Pending' initially
    const statusBadges = screen.getAllByText('Pending');
    expect(statusBadges.length).toBeGreaterThan(0);
  });

  test('triggers verification when button is clicked', async () => {
    // Mock the verification API call
    mockAxios.onPost('/api/v1/verification/features/1/verify').reply(200, {
      id: 1,
      feature_id: 1,
      status: 'verified',
      details: 'Verification completed successfully',
      created_at: new Date().toISOString()
    });

    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Find and click the verify button for the first feature
    const verifyButtons = screen.getAllByText('Verify');
    fireEvent.click(verifyButtons[0]);

    // Should show "Verifying..." text
    await waitFor(() => {
      expect(screen.getByText('Verifying...')).toBeInTheDocument();
    });

    // After verification completes, should show new status
    await waitFor(() => {
      expect(screen.getByText('Verified')).toBeInTheDocument();
    });
  });

  test('handles verification errors gracefully', async () => {
    // Mock a verification error
    mockAxios.onPost('/api/v1/verification/features/1/verify').reply(500, {
      error: 'Verification failed due to server error'
    });

    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Find and click the verify button
    const verifyButtons = screen.getAllByText('Verify');
    fireEvent.click(verifyButtons[0]);

    // Wait for error state to be reflected
    await waitFor(() => {
      const errorStatus = screen.queryAllByText('Error');
      expect(errorStatus.length).toBeGreaterThan(0);
    });
  });

  test('shows verification summary cards', async () => {
    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Check if summary cards are rendered
    expect(screen.getByText('Total Features')).toBeInTheDocument();
  });
});