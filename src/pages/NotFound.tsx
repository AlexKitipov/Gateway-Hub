import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>404</h1>
      <p style={{ fontSize: '1.3rem', color: '#666', marginBottom: '2rem' }}>
        Page not found
      </p>
      <Link
        to="/"
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
        Back to Home
      </Link>
    </div>
  );
};

export default NotFound;
