'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { todoAPI } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingTodoId, setEditingTodoId] = useState(null);
  const [editingText, setEditingText] = useState('');

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      router.push('/login');
    } else if (isAuthenticated) {
      fetchTodos();
    }
  }, [isAuthenticated, isLoading, router]);

  const fetchTodos = async () => {
    try {
      const response = await todoAPI.getTodos(user?.id || 1);
      setTodos(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch todos. Please try again.');
      setLoading(false);
    }
  };

  const handleAddTodo = async (e) => {
    e.preventDefault();
    if (!newTodo.trim()) return;

    try {
      await todoAPI.createTodo({
        description: newTodo,
        user_id: user?.id || 1  // Use the authenticated user's ID, fallback to 1
      });
      setNewTodo('');
      fetchTodos(); // Refresh the list
    } catch (err) {
      setError('Failed to add todo. Please try again.');
    }
  };

  const handleToggleStatus = async (id, currentStatus) => {
    try {
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
      await todoAPI.updateTodoStatus(id, {
        status: newStatus
      }, user?.id || 1); // Pass the user ID
      fetchTodos(); // Refresh the list
    } catch (err) {
      setError('Failed to update todo. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    try {
      await todoAPI.deleteTodo(id, user?.id || 1); // Pass the user ID
      fetchTodos(); // Refresh the list
    } catch (err) {
      setError('Failed to delete todo. Please try again.');
    }
  };

  const startEditing = (todo) => {
    setEditingTodoId(todo.id);
    setEditingText(todo.description);
  };

  const handleEdit = async (id) => {
    try {
      await todoAPI.editTodo(id, {
        description: editingText
      }, user?.id || 1); // Pass the user ID
      setEditingTodoId(null);
      setEditingText('');
      fetchTodos(); // Refresh the list
    } catch (err) {
      setError('Failed to edit todo. Please try again.');
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (isLoading || loading) {
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
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Redirect handled by useEffect
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        padding: '30px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
          paddingBottom: '20px',
          borderBottom: '1px solid #eee'
        }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#333',
            margin: 0
          }}>
            Todo Dashboard
          </h1>
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

        <form
          onSubmit={handleAddTodo}
          style={{
            display: 'flex',
            gap: '10px',
            marginBottom: '30px'
          }}
        >
          <input
            type="text"
            value={newTodo}
            onChange={(e) => setNewTodo(e.target.value)}
            placeholder="What needs to be done?"
            style={{
              flex: 1,
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
          <button
            type="submit"
            style={{
              padding: '12px 20px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#218838'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#28a745'}
          >
            Add Todo
          </button>
        </form>

        {error && (
          <div style={{
            backgroundColor: '#fee',
            color: '#c33',
            padding: '12px',
            borderRadius: '4px',
            marginBottom: '20px',
            border: '1px solid #fcc'
          }}>
            {error}
          </div>
        )}

        <h2 style={{
          fontSize: '20px',
          fontWeight: '600',
          color: '#333',
          marginBottom: '16px'
        }}>
          Your Tasks
        </h2>

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
                  alignItems: 'center',
                  padding: '12px',
                  marginBottom: '8px',
                  backgroundColor: '#fafafa',
                  borderRadius: '4px',
                  border: '1px solid #eee'
                }}
              >
                <input
                  type="checkbox"
                  checked={todo.status === 'completed'}
                  onChange={() => handleToggleStatus(todo.id, todo.status)}
                  style={{
                    marginRight: '12px',
                    transform: 'scale(1.2)'
                  }}
                />
                {editingTodoId === todo.id ? (
                  <>
                    <input
                      type="text"
                      value={editingText}
                      onChange={(e) => setEditingText(e.target.value)}
                      style={{
                        flex: 1,
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '16px',
                        marginRight: '8px'
                      }}
                      autoFocus
                    />
                    <button
                      onClick={() => handleEdit(todo.id)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        transition: 'background-color 0.2s',
                        marginRight: '4px'
                      }}
                      onMouseOver={(e) => e.target.style.backgroundColor = '#218838'}
                      onMouseOut={(e) => e.target.style.backgroundColor = '#28a745'}
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setEditingTodoId(null)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        transition: 'background-color 0.2s',
                        marginRight: '4px'
                      }}
                      onMouseOver={(e) => e.target.style.backgroundColor = '#5a6268'}
                      onMouseOut={(e) => e.target.style.backgroundColor = '#6c757d'}
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <span
                      style={{
                        flex: 1,
                        textDecoration: todo.status === 'completed' ? 'line-through' : 'none',
                        color: todo.status === 'completed' ? '#888' : '#333',
                        fontWeight: todo.status === 'completed' ? 'normal' : '500'
                      }}
                      onDoubleClick={() => startEditing(todo)}
                    >
                      {todo.description}
                    </span>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        backgroundColor: todo.status === 'completed' ? '#d4edda' : '#fff3cd',
                        color: todo.status === 'completed' ? '#155724' : '#856404',
                        marginLeft: '12px'
                      }}
                    >
                      {todo.status}
                    </span>
                    <button
                      onClick={() => startEditing(todo)}
                      style={{
                        marginLeft: '12px',
                        padding: '6px 12px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        transition: 'background-color 0.2s',
                        marginRight: '4px'
                      }}
                      onMouseOver={(e) => e.target.style.backgroundColor = '#005cbf'}
                      onMouseOut={(e) => e.target.style.backgroundColor = '#007bff'}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(todo.id)}
                      style={{
                        padding: '6px 12px',
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
                      Delete
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}