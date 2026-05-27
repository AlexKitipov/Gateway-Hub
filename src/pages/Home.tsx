import React from 'react';
import { useAuth } from '../hooks/useAuth';

const Home: React.FC = () => {
  const { user } = useAuth();

  return (
    <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔗 MiniURL</h1>
      <p style={{ fontSize: '1.3rem', color: '#666', marginBottom: '2rem' }}>
        Simple, fast, and reliable URL shortening service
      </p>

      {user ? (
        <div>
          <p style={{ fontSize: '1.1rem', marginBottom: '2rem' }}>
            Welcome back, {user.email}!
          </p>
          <a
            href="/dashboard"
            style={{
              display: 'inline-block',
              padding: '0.75rem 2rem',
              backgroundColor: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '600',
            }}
          >
            Go to Dashboard
          </a>
        </div>
      ) : (
        <div style={{ marginBottom: '2rem' }}>
          <a
            href="/login"
            style={{
              display: 'inline-block',
              padding: '0.75rem 2rem',
              backgroundColor: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '600',
              marginRight: '1rem',
            }}
          >
            Log In
          </a>
          <a
            href="/register"
            style={{
              display: 'inline-block',
              padding: '0.75rem 2rem',
              backgroundColor: '#764ba2',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '600',
            }}
          >
            Sign Up
          </a>
        </div>
      )}

      <div style={{ marginTop: '4rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
        <div>
          <h3 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>⚡ Fast</h3>
          <p>Generate short links in seconds</p>
        </div>
        <div>
          <h3 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>📊 Analytics</h3>
          <p>Track clicks and measure performance</p>
        </div>
        <div>
          <h3 style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>🔒 Secure</h3>
          <p>Your links are safe and private</p>
        </div>
      </div>
    </div>
  );
};

export default Home;
