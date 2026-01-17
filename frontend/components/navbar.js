'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';

export default function Navbar() {
  const router = useRouter();
  const { user, logout, loading } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return (
      <nav style={{
        display: 'flex',
        alignItems: 'center',
        padding: '1rem',
        backgroundColor: '#007acc',
        color: 'white',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ margin: '0 1rem' }}>
          <p>Loading...</p>
        </div>
      </nav>
    );
  }

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      padding: '1rem',
      backgroundColor: '#007acc',
      color: 'white',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <Link
        href="/"
        style={{
          color: 'white',
          textDecoration: 'none',
          fontWeight: 'bold',
          fontSize: '1.2rem',
          margin: '0 1rem'
        }}
      >
        Todo Chatbot
      </Link>

      {user ? (
        <>
          <Link
            href="/dashboard"
            style={{
              color: 'white',
              textDecoration: 'none',
              margin: '0 1rem',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Dashboard
          </Link>
          <Link
            href="/chat"
            style={{
              color: 'white',
              textDecoration: 'none',
              margin: '0 1rem',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Chat
          </Link>
          <Link
            href="/profile"
            style={{
              color: 'white',
              textDecoration: 'none',
              margin: '0 1rem',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Profile
          </Link>
          <Link
            href="/settings"
            style={{
              color: 'white',
              textDecoration: 'none',
              margin: '0 1rem',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Settings
          </Link>
          <span style={{ margin: '0 1rem' }}>
            Welcome, {user.name}
          </span>
          <button
            onClick={handleLogout}
            style={{
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
              margin: '0 1rem',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c82333'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#dc3545'}
          >
            Logout
          </button>
        </>
      ) : (
        <>
          <Link
            href="/login"
            style={{
              color: 'white',
              textDecoration: 'none',
              margin: '0 1rem',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Sign In
          </Link>
          <Link
            href="/register"
            style={{
              color: 'white',
              textDecoration: 'none',
              margin: '0 1rem',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Sign Up
          </Link>
        </>
      )}
    </nav>
  );
}