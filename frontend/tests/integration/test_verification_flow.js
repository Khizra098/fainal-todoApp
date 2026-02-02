/**
 * Integration tests for the verification dashboard flow.
 *
 * This module contains integration tests for the complete verification workflow,
 * testing the interaction between components, API calls, and state management.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
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

describe('Verification Dashboard Integration Flow', () => {
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
      },
      {
        id: 3,
        name: 'Chat Functionality',
        description: 'Real-time messaging capability',
        specification_reference: 'SPEC-CHAT-001'
      }
    ]);
  });

  afterEach(() => {
    mockAxios.restore();
  });

  test('full verification flow for multiple features', async () => {
    // Mock verification API calls for each feature
    mockAxios
      .onPost('/api/v1/verification/features/1/verify')
      .reply(200, {
        id: 1,
        feature_id: 1,
        status: 'verified',
        details: 'Login feature verified successfully',
        expected_behavior: 'User should be able to log in with valid credentials',
        actual_behavior: 'Login works as expected',
        issues_found: [],
        created_at: new Date().toISOString()
      })
      .onPost('/api/v1/verification/features/2/verify')
      .reply(200, {
        id: 2,
        feature_id: 2,
        status: 'failed',
        details: 'Todo creation failed verification',
        expected_behavior: 'User should be able to create new todos',
        actual_behavior: 'Creating todos results in error',
        issues_found: ['Validation error', 'Missing field'],
        created_at: new Date().toISOString()
      })
      .onPost('/api/v1/verification/features/3/verify')
      .reply(200, {
        id: 3,
        feature_id: 3,
        status: 'verified',
        details: 'Chat functionality verified successfully',
        expected_behavior: 'Users should be able to send/receive messages',
        actual_behavior: 'Chat works as expected',
        issues_found: [],
        created_at: new Date().toISOString()
      });

    await act(async () => {
      render(<VerificationDashboard />);
    });

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Get all verify buttons
    const verifyButtons = screen.getAllByText('Verify');

    // Click verify for first feature (Login)
    fireEvent.click(verifyButtons[0]);

    // Wait for verification to complete
    await waitFor(() => {
      expect(screen.getByText('Verified')).toBeInTheDocument();
    });

    // Click verify for second feature (Todo Creation)
    const verifyButtonsAfterFirst = screen.getAllByText('Verify');
    fireEvent.click(verifyButtonsAfterFirst[0]); // Second feature's verify button

    // Wait for second verification to complete
    await waitFor(() => {
      const failedStatus = screen.getAllByText('Failed');
      expect(failedStatus.length).toBeGreaterThanOrEqual(1);
    });

    // Click verify for third feature (Chat)
    const verifyButtonsAfterSecond = screen.getAllByText('Verify');
    fireEvent.click(verifyButtonsAfterSecond[0]); // Third feature's verify button

    // Wait for third verification to complete
    await waitFor(() => {
      const verifiedStatus = screen.getAllByText('Verified');
      expect(verifiedStatus.length).toBeGreaterThanOrEqual(2); // First and third should be verified
    });

    // Check summary reflects the results
    await waitFor(() => {
      const summaryCards = screen.getAllByRole('group'); // Assuming cards are group roles

      // Look for elements indicating counts
      const verifiedElements = screen.getAllByText('Verified');
      const failedElements = screen.getAllByText('Failed');

      // At least 2 verified and 1 failed
      expect(verifiedElements.length).toBeGreaterThanOrEqual(2);
      expect(failedElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  test('displays detailed verification results', async () => {
    // Mock verification with issues found
    mockAxios.onPost('/api/v1/verification/features/1/verify').reply(200, {
      id: 1,
      feature_id: 1,
      status: 'failed',
      details: 'Verification failed due to multiple issues',
      expected_behavior: 'Feature should work as specified',
      actual_behavior: 'Feature has several problems',
      issues_found: [
        'UI element misaligned',
        'Performance issue detected',
        'Accessibility concern'
      ],
      created_at: new Date().toISOString()
    });

    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Click verify button
    const verifyButton = screen.getByText('Verify');
    fireEvent.click(verifyButton);

    // Wait for results to be displayed
    await waitFor(() => {
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });

    // Check that issues are displayed
    await waitFor(() => {
      expect(screen.getByText('Issues Found:')).toBeInTheDocument();
      expect(screen.getByText('UI element misaligned')).toBeInTheDocument();
      expect(screen.getByText('Performance issue detected')).toBeInTheDocument();
      expect(screen.getByText('Accessibility concern')).toBeInTheDocument();
    });
  });

  test('handles network errors gracefully', async () => {
    // Mock network error
    mockAxios.onPost('/api/v1/verification/features/1/verify').networkError();

    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Click verify button
    const verifyButton = screen.getByText('Verify');
    fireEvent.click(verifyButton);

    // Wait for error state
    await waitFor(() => {
      const errorStatus = screen.queryAllByText('Error');
      expect(errorStatus.length).toBeGreaterThan(0);
    });
  });

  test('updates summary in real-time as verifications complete', async () => {
    // Mock verification responses with delays to simulate real timing
    mockAxios.onPost('/api/v1/verification/features/1/verify')
      .replyOnce(200, {
        id: 1,
        feature_id: 1,
        status: 'verified',
        details: 'Verified successfully',
        created_at: new Date().toISOString()
      });

    await act(async () => {
      render(<VerificationDashboard />);
    });

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Get initial summary values
    const initialTotal = screen.getByText('Total Features');
    expect(initialTotal).toBeInTheDocument();

    // Click verify
    const verifyButton = screen.getByText('Verify');
    fireEvent.click(verifyButton);

    // Wait for verification to complete and summary to update
    await waitFor(() => {
      const verifiedCountElement = screen.getByText('Verified');
      expect(verifiedCountElement).toBeInTheDocument();
    });
  });

  test('preserves verification state during component re-renders', async () => {
    mockAxios.onPost('/api/v1/verification/features/1/verify').reply(200, {
      id: 1,
      feature_id: 1,
      status: 'verified',
      details: 'Verified successfully',
      created_at: new Date().toISOString()
    });

    const { rerender } = render(<VerificationDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Login Feature')).toBeInTheDocument();
    });

    // Click verify
    const verifyButton = screen.getByText('Verify');
    fireEvent.click(verifyButton);

    // Wait for verification to complete
    await waitFor(() => {
      expect(screen.getByText('Verified')).toBeInTheDocument();
    });

    // Re-render the component (simulating a state update or navigation)
    rerender(<VerificationDashboard />);

    // Verify that the verification state is preserved
    await waitFor(() => {
      expect(screen.getByText('Verified')).toBeInTheDocument();
    });
  });
});