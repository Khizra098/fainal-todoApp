'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { chatAPI, todoAPI, mcpAPI } from '@/lib/api';

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', content: 'Hello! I\'m your AI assistant for managing todos. How can I help you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [todos, setTodos] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated && !authLoading) {
      router.push('/login');
    } else if (isAuthenticated) {
      fetchTodos();
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchTodos = async () => {
    try {
      const response = await todoAPI.getTodos();
      setTodos(response.data);
    } catch (err) {
      console.error('Failed to fetch todos:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send message to backend AI agent
      const response = await chatAPI.sendMessage({
        message: userMessage.content
      });

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update todos if the response includes todo data
      if (response.data.action === 'list_todos' && response.data.tasks) {
        setTodos(response.data.tasks);
      } else if (response.data.action === 'create_todo' && response.data.task) {
        fetchTodos(); // Refresh todos after creating a new one
      } else if (['update_status', 'delete_todo'].includes(response.data.action)) {
        fetchTodos(); // Refresh todos after updates
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTodoAction = async (action, todoId) => {
    try {
      let response;

      switch (action) {
        case 'complete':
          response = await mcpAPI.updateTodoStatus({
            task_id: todoId,
            status: 'completed'
          });
          break;
        case 'pending':
          response = await mcpAPI.updateTodoStatus({
            task_id: todoId,
            status: 'pending'
          });
          break;
        case 'delete':
          response = await mcpAPI.deleteTodo({
            task_id: todoId
          });
          break;
        default:
          return;
      }

      if (response.data.success) {
        // Refresh todos after the action
        fetchTodos();

        // Add confirmation message
        let actionText = '';
        switch (action) {
          case 'complete':
            actionText = 'marked as completed';
            break;
          case 'pending':
            actionText = 'marked as pending';
            break;
          case 'delete':
            actionText = 'deleted';
            break;
        }

        const confirmationMessage = {
          id: Date.now(),
          role: 'assistant',
          content: `Todo #${todoId} has been ${actionText}.`
        };

        setMessages(prev => [...prev, confirmationMessage]);
      }
    } catch (error) {
      console.error(`Error performing ${action} on todo ${todoId}:`, error);

      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `Sorry, I couldn't ${action} the todo. Please try again.`
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (authLoading || (!isAuthenticated && !authLoading)) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
        padding: '20px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <p>Loading your chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{
        display: 'flex',
        height: '100vh',
        maxWidth: '1200px',
        margin: '0 auto',
        width: '100%'
      }}>
        {/* Todo Panel */}
        <div style={{
          flex: '0 0 300px',
          backgroundColor: 'white',
          borderRight: '1px solid #eee',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#333',
            marginBottom: '16px'
          }}>
            Your Tasks
          </h2>

          <div style={{
            marginBottom: '16px',
            fontSize: '14px',
            color: '#666'
          }}>
            Active: {todos.filter(t => t.status !== 'completed').length} | Completed: {todos.filter(t => t.status === 'completed').length}
          </div>

          <div style={{
            flex: 1,
            overflowY: 'auto'
          }}>
            {todos.length === 0 ? (
              <div style={{
                padding: '20px',
                textAlign: 'center',
                color: '#666',
                fontStyle: 'italic'
              }}>
                <p>No tasks yet</p>
              </div>
            ) : (
              <ul style={{
                listStyle: 'none',
                padding: 0,
                margin: 0
              }}>
                {todos.map((todo) => (
                  <li
                    key={todo.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      padding: '12px',
                      marginBottom: '8px',
                      backgroundColor: '#fafafa',
                      borderRadius: '4px',
                      border: '1px solid #eee'
                    }}
                  >
                    <span
                      style={{
                        textDecoration: todo.status === 'completed' ? 'line-through' : 'none',
                        color: todo.status === 'completed' ? '#888' : '#333',
                        fontWeight: todo.status === 'completed' ? 'normal' : '500',
                        fontSize: '14px'
                      }}
                    >
                      {todo.description}
                    </span>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '10px',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        backgroundColor: todo.status === 'completed' ? '#d4edda' : '#fff3cd',
                        color: todo.status === 'completed' ? '#155724' : '#856404',
                        alignSelf: 'flex-start',
                        display: 'inline-block'
                      }}
                    >
                      {todo.status}
                    </span>
                    <div style={{
                      display: 'flex',
                      gap: '4px',
                      marginTop: '8px'
                    }}>
                      <button
                        onClick={() => handleTodoAction('complete', todo.id)}
                        style={{
                          flex: 1,
                          padding: '6px 8px',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#218838'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#28a745'}
                      >
                        Complete
                      </button>
                      <button
                        onClick={() => handleTodoAction('pending', todo.id)}
                        style={{
                          flex: 1,
                          padding: '6px 8px',
                          backgroundColor: '#ffc107',
                          color: '#856404',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#e0a800'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#ffc107'}
                      >
                        Pending
                      </button>
                      <button
                        onClick={() => handleTodoAction('delete', todo.id)}
                        style={{
                          flex: 1,
                          padding: '6px 8px',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          transition: 'background-color 0.2s'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#c82333'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#dc3545'}
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Chat Panel */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderBottom: '1px solid #eee',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#333',
              margin: 0
            }}>
              AI Assistant Chat
            </h2>
            <button
              onClick={handleLogout}
              style={{
                padding: '8px 16px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#c82333'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#dc3545'}
            >
              Logout
            </button>
          </div>

          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px',
            backgroundColor: '#fafafa'
          }}>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  style={{
                    maxWidth: '80%',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    backgroundColor: message.role === 'user' ? '#007acc' : '#e9ecef',
                    color: message.role === 'user' ? 'white' : '#333',
                    alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                    marginLeft: message.role === 'assistant' ? '0' : 'auto',
                    marginRight: message.role === 'user' ? '0' : 'auto',
                    wordWrap: 'break-word'
                  }}
                >
                  <div style={{
                    fontWeight: '500',
                    marginBottom: '4px',
                    fontSize: '12px',
                    opacity: 0.8
                  }}>
                    {message.role === 'user' ? 'You' : 'AI Assistant'}:
                  </div>
                  <div style={{
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.5'
                  }}>
                    {message.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div
                  style={{
                    maxWidth: '80%',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    backgroundColor: '#e9ecef',
                    color: '#333',
                    alignSelf: 'flex-start',
                    wordWrap: 'break-word'
                  }}
                >
                  <div style={{
                    fontWeight: '500',
                    marginBottom: '4px',
                    fontSize: '12px',
                    opacity: 0.8
                  }}>
                    AI Assistant:
                  </div>
                  <div>Thinking...</div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderTop: '1px solid #eee'
          }}>
            <form
              onSubmit={handleSendMessage}
              style={{
                display: 'flex',
                gap: '10px'
              }}
            >
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '24px',
                  fontSize: '16px',
                  outline: 'none'
                }}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                style={{
                  padding: '12px 24px',
                  backgroundColor: isLoading ? '#ccc' : '#007acc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '24px',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontSize: '16px',
                  transition: 'background-color 0.2s'
                }}
                onMouseOver={(e) => {
                  if (!isLoading) {
                    e.target.style.backgroundColor = '#0056b3';
                  }
                }}
                onMouseOut={(e) => {
                  if (!isLoading) {
                    e.target.style.backgroundColor = '#007acc';
                  }
                }}
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}