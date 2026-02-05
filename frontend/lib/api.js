import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  updateUserProfile: (userData) => apiClient.put('/auth/profile', userData),
  getUserDetails: () => apiClient.get('/auth/me'),
  changePassword: (passwordData) => apiClient.put('/auth/change-password', passwordData),
  toggleTwoFactor: (toggleData) => apiClient.post('/auth/toggle-two-factor', toggleData),
  updatePreferences: (prefsData) => apiClient.put('/auth/preferences', prefsData),
  logoutAllDevices: () => apiClient.post('/auth/logout-all-devices'),
  logout: () => {
    localStorage.removeItem('token');
  }
};

// Todo API
export const todoAPI = {
  getTodos: (userId = 1) => apiClient.get(`/api/v1/todos?user_id=${userId}`),
  createTodo: (todoData) => {
    const params = new URLSearchParams({
      description: todoData.description,
      user_id: todoData.user_id || 1  // Default to user_id 1 if not provided
    });
    if (todoData.due_date) params.append('due_date', todoData.due_date);
    if (todoData.category) params.append('category', todoData.category);
    if (todoData.priority) params.append('priority', todoData.priority);

    return apiClient.post(`/api/v1/todos?${params.toString()}`);
  },
  updateTodoStatus: (todoId, statusData, userId = 1) => apiClient.put(`/api/v1/todos/${todoId}/status?user_id=${userId}&status_update=${statusData.status}`),
  editTodo: (todoId, todoData, userId = 1) => {
    const params = new URLSearchParams({
      user_id: userId,
      description: todoData.description
    });
    if (todoData.due_date) params.append('due_date', todoData.due_date);
    if (todoData.category) params.append('category', todoData.category);
    if (todoData.priority) params.append('priority', todoData.priority);

    return apiClient.put(`/api/v1/todos/${todoId}?${params.toString()}`);
  },
  deleteTodo: (todoId, userId = 1) => apiClient.delete(`/api/v1/todos/${todoId}?user_id=${userId}`),
  searchTodos: (queryData) => apiClient.post('/api/v1/todos/search', queryData)
};

// Chat API
export const chatAPI = {
  sendMessage: (messageData) => apiClient.post('/api/v1/chat', messageData),
  getChatHistory: (conversationId) => apiClient.get(`/api/v1/chat/${conversationId}`)
};

// MCP Tools API
export const mcpAPI = {
  createTodo: (todoData) => apiClient.post('/api/v1/mcp/create_todo', todoData),
  listTodos: (filterData) => apiClient.post('/api/v1/mcp/list_todos', filterData),
  updateTodoStatus: (todoData) => apiClient.post('/api/v1/mcp/update_todo_status', todoData),
  deleteTodo: (todoData) => apiClient.post('/api/v1/mcp/delete_todo', todoData),
  searchTodos: (searchData) => apiClient.post('/api/v1/mcp/search_todos', searchData),
  setReminder: (reminderData) => apiClient.post('/api/v1/mcp/set_reminder', reminderData)
};

// Verification API
export const verificationAPI = {
  getFeatures: () => apiClient.get('/api/v1/verification/features'),
  getFeatureById: (featureId) => apiClient.get(`/api/v1/verification/features/${featureId}`),
  verifyFeature: (featureId) => apiClient.post(`/api/v1/verification/features/${featureId}/verify`),
  getVerificationReport: (featureId) => apiClient.get(`/api/v1/verification/features/${featureId}/report`)
};

// Export individual functions for backward compatibility
export const {
  getFeatures,
  getFeatureById,
  verifyFeature,
  getVerificationReport
} = verificationAPI;