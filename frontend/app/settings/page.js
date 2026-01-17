'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('account');

  const handleLogout = () => {
    logout();
    router.push('/');
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
          <p>Loading settings...</p>
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
            Settings
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

        <div style={{
          display: 'flex',
          marginBottom: '20px',
          borderBottom: '1px solid #eee'
        }}>
          <button
            onClick={() => setActiveTab('account')}
            style={{
              padding: '12px 20px',
              backgroundColor: activeTab === 'account' ? '#007acc' : '#f8f9fa',
              color: activeTab === 'account' ? 'white' : '#495057',
              border: '1px solid #dee2e6',
              borderBottom: activeTab === 'account' ? 'none' : '1px solid #dee2e6',
              borderRadius: '4px 4px 0 0',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'account' ? 'bold' : 'normal',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => {
              if (activeTab !== 'account') {
                e.target.style.backgroundColor = '#e9ecef';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== 'account') {
                e.target.style.backgroundColor = '#f8f9fa';
              }
            }}
          >
            Account Settings
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            style={{
              padding: '12px 20px',
              backgroundColor: activeTab === 'preferences' ? '#007acc' : '#f8f9fa',
              color: activeTab === 'preferences' ? 'white' : '#495057',
              border: '1px solid #dee2e6',
              borderLeft: 'none',
              borderBottom: activeTab === 'preferences' ? 'none' : '1px solid #dee2e6',
              borderRadius: '4px 4px 0 0',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'preferences' ? 'bold' : 'normal',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => {
              if (activeTab !== 'preferences') {
                e.target.style.backgroundColor = '#e9ecef';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== 'preferences') {
                e.target.style.backgroundColor = '#f8f9fa';
              }
            }}
          >
            Preferences
          </button>
          <button
            onClick={() => setActiveTab('security')}
            style={{
              padding: '12px 20px',
              backgroundColor: activeTab === 'security' ? '#007acc' : '#f8f9fa',
              color: activeTab === 'security' ? 'white' : '#495057',
              border: '1px solid #dee2e6',
              borderLeft: 'none',
              borderBottom: activeTab === 'security' ? 'none' : '1px solid #dee2e6',
              borderRadius: '4px 4px 0 0',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'security' ? 'bold' : 'normal',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => {
              if (activeTab !== 'security') {
                e.target.style.backgroundColor = '#e9ecef';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== 'security') {
                e.target.style.backgroundColor = '#f8f9fa';
              }
            }}
          >
            Security
          </button>
        </div>

        <div style={{
          padding: '20px 0'
        }}>
          {activeTab === 'account' && (
            <div>
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#333',
                marginBottom: '20px'
              }}>
                Account Information
              </h2>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#555',
                    marginBottom: '4px'
                  }}>
                    User ID
                  </label>
                  <div style={{
                    padding: '12px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #eee',
                    borderRadius: '4px',
                    fontSize: '16px',
                    color: '#666'
                  }}>
                    {user?.id || 'N/A'}
                  </div>
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#555',
                    marginBottom: '4px'
                  }}>
                    Full Name
                  </label>
                  <div style={{
                    padding: '12px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #eee',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}>
                    {user?.name || 'N/A'}
                  </div>
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#555',
                    marginBottom: '4px'
                  }}>
                    Email Address
                  </label>
                  <div style={{
                    padding: '12px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #eee',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}>
                    {user?.email || 'N/A'}
                  </div>
                </div>

                <div style={{
                  marginTop: '20px',
                  padding: '16px',
                  backgroundColor: '#fff3cd',
                  border: '1px solid #ffeaa7',
                  borderRadius: '4px'
                }}>
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#856404',
                    marginBottom: '8px'
                  }}>
                    Account Actions
                  </h3>
                  <p style={{
                    color: '#856404',
                    marginBottom: '12px'
                  }}>
                    Manage your account settings and preferences.
                  </p>
                  <button
                    onClick={() => router.push('/profile')}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#ffc107',
                      color: '#856404',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#e0a800'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#ffc107'}
                  >
                    Edit Profile
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div>
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#333',
                marginBottom: '20px'
              }}>
                User Preferences
              </h2>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#555',
                    marginBottom: '4px'
                  }}>
                    Theme
                  </label>
                  <select
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '16px',
                      backgroundColor: 'white'
                    }}
                    defaultValue="light"
                  >
                    <option value="light">Light Theme</option>
                    <option value="dark">Dark Theme</option>
                    <option value="auto">System Default</option>
                  </select>
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#555',
                    marginBottom: '4px'
                  }}>
                    Language
                  </label>
                  <select
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '16px',
                      backgroundColor: 'white'
                    }}
                    defaultValue="en"
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                  </select>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <input
                    type="checkbox"
                    id="notifications"
                    style={{
                      transform: 'scale(1.2)'
                    }}
                    defaultChecked
                  />
                  <label htmlFor="notifications" style={{
                    fontSize: '16px',
                    color: '#333',
                    margin: 0
                  }}>
                    Enable notifications
                  </label>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <input
                    type="checkbox"
                    id="emailUpdates"
                    style={{
                      transform: 'scale(1.2)'
                    }}
                    defaultChecked
                  />
                  <label htmlFor="emailUpdates" style={{
                    fontSize: '16px',
                    color: '#333',
                    margin: 0
                  }}>
                    Receive email updates
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div>
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#333',
                marginBottom: '20px'
              }}>
                Security Settings
              </h2>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}>
                <div style={{
                  padding: '16px',
                  backgroundColor: '#d1ecf1',
                  border: '1px solid #bee5eb',
                  borderRadius: '4px'
                }}>
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#0c5460',
                    marginBottom: '8px'
                  }}>
                    Password Security
                  </h3>
                  <p style={{
                    color: '#0c5460',
                    marginBottom: '12px'
                  }}>
                    Your password is currently set and secure.
                  </p>
                  <button
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#17a2b8',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#138496'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#17a2b8'}
                  >
                    Change Password
                  </button>
                </div>

                <div style={{
                  padding: '16px',
                  backgroundColor: '#f8d7da',
                  border: '1px solid #f5c6cb',
                  borderRadius: '4px'
                }}>
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#721c24',
                    marginBottom: '8px'
                  }}>
                    Session Management
                  </h3>
                  <p style={{
                    color: '#721c24',
                    marginBottom: '12px'
                  }}>
                    You are currently logged in from this device.
                  </p>
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
                    Log out of all devices
                  </button>
                </div>

                <div style={{
                  padding: '16px',
                  backgroundColor: '#d4edda',
                  border: '1px solid #c3e6cb',
                  borderRadius: '4px'
                }}>
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#155724',
                    marginBottom: '8px'
                  }}>
                    Two-Factor Authentication
                  </h3>
                  <p style={{
                    color: '#155724',
                    marginBottom: '12px'
                  }}>
                    Two-factor authentication is not enabled on your account.
                  </p>
                  <button
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#218838'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#28a745'}
                  >
                    Enable 2FA
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}