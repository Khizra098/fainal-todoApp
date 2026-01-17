'use client';

import { useAuth } from '@/lib/auth';
import { useState } from 'react';

export default function TestAuthPage() {
  const { user, isLoading, login, register, logout, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await login(email, password);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await register(name, email, password);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSignOut = async () => {
    try {
      await logout();
    } catch (err) {
      setError(err.message);
    }
  };

  if (isLoading) {
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
          <p>Loading...</p>
        </div>
      </div>
    );
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
        <h1 style={{
          fontSize: '28px',
          fontWeight: 'bold',
          color: '#333',
          marginBottom: '24px',
          textAlign: 'center'
        }}>
          Authentication Test Page
        </h1>

        {error && (
          <div style={{
            backgroundColor: '#fee',
            color: '#c33',
            padding: '12px',
            borderRadius: '4px',
            marginBottom: '20px',
            border: '1px solid #fcc'
          }}>
            Error: {error}
          </div>
        )}

        {user ? (
          <div style={{
            marginBottom: '24px',
            padding: '20px',
            backgroundColor: '#d4edda',
            borderRadius: '8px',
            border: '1px solid #c3e6cb'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#155724',
              marginBottom: '12px'
            }}>
              Authenticated User
            </h2>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <p style={{ margin: 0 }}><strong>ID:</strong> {user.id}</p>
              <p style={{ margin: 0 }}><strong>Email:</strong> {user.email}</p>
              <p style={{ margin: 0 }}><strong>Name:</strong> {user.name}</p>
              <p style={{ margin: 0 }}><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
            </div>
            <button
              onClick={handleSignOut}
              style={{
                marginTop: '16px',
                padding: '10px 20px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#c82333'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#dc3545'}
            >
              Sign Out
            </button>
          </div>
        ) : (
          <div style={{
            marginBottom: '24px',
            padding: '24px',
            backgroundColor: '#e7f3ff',
            borderRadius: '8px',
            border: '1px solid #b8daff'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#004085',
              marginBottom: '16px',
              textAlign: 'center'
            }}>
              Not Authenticated
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px'
            }}>
              {/* Sign In Form */}
              <div style={{
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '6px',
                border: '1px solid #b8daff'
              }}>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '500',
                  color: '#004085',
                  marginBottom: '16px',
                  textAlign: 'center'
                }}>
                  Sign In
                </h3>
                <form onSubmit={handleSignIn}>
                  <div style={{ marginBottom: '16px' }}>
                    <input
                      type="email"
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '16px'
                      }}
                      required
                    />
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <input
                      type="password"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '16px'
                      }}
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    style={{
                      width: '100%',
                      padding: '12px',
                      backgroundColor: '#007acc',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '16px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#0056b3'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#007acc'}
                  >
                    Sign In
                  </button>
                </form>
              </div>

              {/* Sign Up Form */}
              <div style={{
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '6px',
                border: '1px solid #b8daff'
              }}>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '500',
                  color: '#004085',
                  marginBottom: '16px',
                  textAlign: 'center'
                }}>
                  Sign Up
                </h3>
                <form onSubmit={handleSignUp}>
                  <div style={{ marginBottom: '16px' }}>
                    <input
                      type="text"
                      placeholder="Name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '16px'
                      }}
                      required
                    />
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <input
                      type="email"
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '16px'
                      }}
                      required
                    />
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <input
                      type="password"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '16px'
                      }}
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    style={{
                      width: '100%',
                      padding: '12px',
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
                    Sign Up
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        <div style={{
          marginTop: '24px',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#495057',
            marginBottom: '12px'
          }}>
            Debug Info
          </h3>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <p style={{ margin: 0 }}><strong>Loading:</strong> {isLoading ? 'Yes' : 'No'}</p>
            <p style={{ margin: 0 }}><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
            <p style={{ margin: 0 }}><strong>User Object:</strong> {user ? JSON.stringify(user, null, 2) : 'null'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}