'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { authAPI } from '@/lib/api';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout, updateUserData } = useAuth();
  const [activeTab, setActiveTab] = useState('account');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(user?.two_factor_enabled || false);
  const [selectedTheme, setSelectedTheme] = useState(user?.theme || 'light');
  const [selectedLanguage, setSelectedLanguage] = useState(user?.language || 'en');
  const [notification, setNotification] = useState({ type: '', message: '' });

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification({ type: '', message: '' }), 3000);
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showNotification('error', 'New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      showNotification('error', 'New password must be at least 6 characters');
      return;
    }

    // Additional password validation
    const hasUpperCase = /[A-Z]/.test(passwordData.newPassword);
    const hasLowerCase = /[a-z]/.test(passwordData.newPassword);
    const hasDigit = /\d/.test(passwordData.newPassword);

    if (!hasUpperCase) {
      showNotification('error', 'New password must contain at least one uppercase letter');
      return;
    }

    if (!hasLowerCase) {
      showNotification('error', 'New password must contain at least one lowercase letter');
      return;
    }

    if (!hasDigit) {
      showNotification('error', 'New password must contain at least one digit');
      return;
    }

    try {
      await authAPI.changePassword({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      });

      showNotification('success', 'Password changed successfully');

      // Clear the form
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });

      // Close the modal after a delay to show the success message
      setTimeout(() => {
        setShowPasswordModal(false);
      }, 2000);
    } catch (error) {
      console.error('Error changing password:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to change password';
      showNotification('error', errorMessage);
    }
  };

  const handleToggleTwoFactor = async () => {
    try {
      const response = await authAPI.toggleTwoFactor({
        enable: !twoFactorEnabled
      });

      if (response.data.success) {
        setTwoFactorEnabled(!twoFactorEnabled);
        showNotification('success', `Two-factor authentication ${twoFactorEnabled ? 'disabled' : 'enabled'} successfully`);
      } else {
        showNotification('error', 'Failed to update two-factor authentication');
      }
    } catch (error) {
      showNotification('error', error.response?.data?.detail || 'Failed to update two-factor authentication');
    }
  };

  const handleLogoutAllDevices = async () => {
    try {
      await authAPI.logoutAllDevices();
      showNotification('success', 'Logged out from all devices successfully');
      // Optionally log out the current user too
      // logout();
      // router.push('/');
    } catch (error) {
      showNotification('error', error.response?.data?.message || 'Failed to log out from all devices');
    }
  };

  const handleUpdatePreferences = async (theme, language) => {
    try {
      const response = await authAPI.updatePreferences({
        theme: theme,
        language: language
      });

      // Update local state
      setSelectedTheme(response.data.theme);
      setSelectedLanguage(response.data.language);

      // Update the global user context to reflect the new preferences
      // This ensures consistency across the application
      // Update the user in the auth context with the new theme and language
      updateUserData({
        ...user,
        theme: response.data.theme,
        language: response.data.language
      });

      showNotification('success', 'Preferences updated successfully');
    } catch (error) {
      console.error('Error updating preferences:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to update preferences';
      showNotification('error', errorMessage);
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
      padding: '20px',
      position: 'relative'
    }}>
      {/* Notification */}
      {notification.message && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          padding: '12px 20px',
          borderRadius: '4px',
          backgroundColor: notification.type === 'success' ? '#d4edda' : '#f8d7da',
          color: notification.type === 'success' ? '#155724' : '#721c24',
          border: `1px solid ${notification.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
          zIndex: 1000,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          {notification.message}
        </div>
      )}

      {/* Password Change Modal */}
      {showPasswordModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            maxWidth: '400px',
            width: '90%'
          }}>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#333',
              marginBottom: '20px'
            }}>
              Change Password
            </h3>

            <div style={{ marginBottom: '15px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#555',
                marginBottom: '4px'
              }}>
                Current Password
              </label>
              <input
                type="password"
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '16px'
                }}
                placeholder="Enter current password"
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#555',
                marginBottom: '4px'
              }}>
                New Password
              </label>
              <input
                type="password"
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '16px'
                }}
                placeholder="Enter new password"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#555',
                marginBottom: '4px'
              }}>
                Confirm New Password
              </label>
              <input
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '16px'
                }}
                placeholder="Confirm new password"
              />
            </div>

            <div style={{
              display: 'flex',
              gap: '10px',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={() => setShowPasswordModal(false)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  transition: 'background-color 0.2s'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = '#5a6268'}
                onMouseOut={(e) => e.target.style.backgroundColor = '#6c757d'}
              >
                Cancel
              </button>
              <button
                onClick={handleChangePassword}
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
                Change Password
              </button>
            </div>
          </div>
        </div>
      )}

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
                    value={selectedTheme}
                    onChange={(e) => {
                      const newTheme = e.target.value;
                      const newLanguage = selectedLanguage; // Capture current language value
                      setSelectedTheme(newTheme);
                      handleUpdatePreferences(newTheme, newLanguage);
                    }}
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
                    value={selectedLanguage}
                    onChange={(e) => {
                      const newLanguage = e.target.value;
                      const newTheme = selectedTheme; // Capture current theme value
                      setSelectedLanguage(newLanguage);
                      handleUpdatePreferences(newTheme, newLanguage);
                    }}
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
                    onClick={() => setShowPasswordModal(true)}
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
                    onClick={handleLogoutAllDevices}
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
                    {twoFactorEnabled
                      ? 'Two-factor authentication is currently enabled on your account.'
                      : 'Two-factor authentication is not enabled on your account.'}
                  </p>
                  <button
                    onClick={handleToggleTwoFactor}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: twoFactorEnabled ? '#dc3545' : '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = twoFactorEnabled ? '#c82333' : '#218838'}
                    onMouseOut={(e) => e.target.style.backgroundColor = twoFactorEnabled ? '#dc3545' : '#28a745'}
                  >
                    {twoFactorEnabled ? 'Disable 2FA' : 'Enable 2FA'}
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