import React from 'react';
import { Link } from 'react-router-dom';
import './NotFound.css';

export const NotFound: React.FC = () => {
  return (
    <div className="not-found">
      <div className="not-found-content">
        <h1>404</h1>
        <p className="not-found-message">Page not found</p>
        <p className="not-found-description">
          Sorry, the page you are looking for does not exist.
        </p>
        <Link to="/" className="not-found-link">
          Go back home
        </Link>
      </div>
    </div>
  );
};
