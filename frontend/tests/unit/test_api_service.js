/**
 * Unit tests for the API service.
 *
 * This module contains unit tests for the API service functions,
 * including authentication, todo, chat, and verification API calls.
 */

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {
  authAPI,
  todoAPI,
  chatAPI,
  verificationAPI,
  getFeatures,
  verifyFeature
} from '@/lib/api';

describe('API Service', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.reset();
  });

  describe('Verification API', () => {
    test('getFeatures should return features list', async () => {
      const mockFeatures = [
        { id: 1, name: 'Feature 1', description: 'Description 1' },
        { id: 2, name: 'Feature 2', description: 'Description 2' }
      ];

      mock.onGet('/api/v1/verification/features').reply(200, mockFeatures);

      const response = await getFeatures();

      expect(response.data).toEqual(mockFeatures);
      expect(mock.history.get).toHaveLength(1);
    });

    test('verifyFeature should trigger verification', async () => {
      const featureId = 1;
      const mockResponse = {
        id: 1,
        feature_id: featureId,
        status: 'verified',
        details: 'Verification completed successfully'
      };

      mock.onPost(`/api/v1/verification/features/${featureId}/verify`).reply(200, mockResponse);

      const response = await verifyFeature(featureId);

      expect(response.data).toEqual(mockResponse);
      expect(mock.history.post).toHaveLength(1);
    });

    test('getFeatureById should return specific feature', async () => {
      const featureId = 1;
      const mockFeature = {
        id: featureId,
        name: 'Test Feature',
        description: 'A test feature',
        specification_reference: 'SPEC-001'
      };

      mock.onGet(`/api/v1/verification/features/${featureId}`).reply(200, mockFeature);

      const response = await verificationAPI.getFeatureById(featureId);

      expect(response.data).toEqual(mockFeature);
      expect(mock.history.get).toHaveLength(1);
    });
  });

  describe('Authentication API', () => {
    test('login should authenticate user', async () => {
      const credentials = { email: 'test@example.com', password: 'password' };
      const mockResponse = { token: 'mock-token', user: { id: 1, email: 'test@example.com' } };

      mock.onPost('/auth/login').reply(200, mockResponse);

      const response = await authAPI.login(credentials);

      expect(response.data).toEqual(mockResponse);
    });

    test('register should create new user', async () => {
      const userData = { email: 'new@example.com', password: 'password', username: 'newuser' };
      const mockResponse = { id: 2, email: 'new@example.com', username: 'newuser' };

      mock.onPost('/auth/register').reply(200, mockResponse);

      const response = await authAPI.register(userData);

      expect(response.data).toEqual(mockResponse);
    });
  });

  describe('Todo API', () => {
    test('getTodos should return todos list', async () => {
      const userId = 1;
      const mockTodos = [
        { id: 1, description: 'Todo 1', completed: false },
        { id: 2, description: 'Todo 2', completed: true }
      ];

      mock.onGet(`/api/v1/todos?user_id=${userId}`).reply(200, mockTodos);

      const response = await todoAPI.getTodos(userId);

      expect(response.data).toEqual(mockTodos);
    });

    test('createTodo should create new todo', async () => {
      const todoData = { description: 'New Todo', user_id: 1 };
      const mockResponse = { id: 3, description: 'New Todo', completed: false, user_id: 1 };

      const params = new URLSearchParams({
        description: todoData.description,
        user_id: todoData.user_id
      }).toString();

      mock.onPost(`/api/v1/todos?${params}`).reply(200, mockResponse);

      const response = await todoAPI.createTodo(todoData);

      expect(response.data).toEqual(mockResponse);
    });
  });

  describe('Chat API', () => {
    test('sendMessage should send message to chat endpoint', async () => {
      const messageData = { conversation_id: 1, content: 'Hello world' };
      const mockResponse = { id: 1, content: 'Hello world', timestamp: '2023-01-01T00:00:00Z' };

      mock.onPost('/api/v1/chat').reply(200, mockResponse);

      const response = await chatAPI.sendMessage(messageData);

      expect(response.data).toEqual(mockResponse);
    });
  });
});