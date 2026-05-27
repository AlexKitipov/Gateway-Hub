import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Home.css';

export const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home">
      <div className="hero">
        <h1>MiniURL 🔗</h1>
        <p className="subtitle">
          Simple, Fast & Reliable URL Shortening Service
        </p>
        <p className="description">
          Shorten your long URLs and track clicks with our powerful URL
          shortener. Free tier available, with premium features for power users.
        </p>

        {!isAuthenticated && (
          <div className="cta-buttons">
            <Link to="/register" className="btn btn-primary">
              Get Started Free
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Sign In
            </Link>
          </div>
        )}

        {isAuthenticated && (
          <div className="cta-buttons">
            <Link to="/dashboard" className="btn btn-primary">
              Go to Dashboard
            </Link>
          </div>
        )}
      </div>

      <div className="features">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <span className="feature-icon">⚡</span>
            <h3>Lightning Fast</h3>
            <p>Shorten URLs instantly with our optimized system</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">📊</span>
            <h3>Analytics</h3>
            <p>Track clicks and monitor performance of your links</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🔒</span>
            <h3>Secure</h3>
            <p>Your data is encrypted and stored securely</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">💰</span>
            <h3>Affordable</h3>
            <p>Free tier available, premium plans starting at $9/month</p>
          </div>
        </div>
      </div>

      <div className="pricing">
        <h2>Simple Pricing</h2>
        <div className="pricing-grid">
          <div className="pricing-card">
            <h3>Free</h3>
            <p className="price">$0/month</p>
            <ul>
              <li>✓ 5 links per month</li>
              <li>✓ 100 clicks per link</li>
              <li>✓ Basic analytics</li>
              <li>✗ No custom domains</li>
            </ul>
          </div>
          <div className="pricing-card premium">
            <div className="badge">Most Popular</div>
            <h3>Premium</h3>
            <p className="price">$9/month</p>
            <ul>
              <li>✓ Unlimited links</li>
              <li>✓ Unlimited clicks</li>
              <li>✓ Advanced analytics</li>
              <li>✓ Custom domains</li>
              <li>✓ API access</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
