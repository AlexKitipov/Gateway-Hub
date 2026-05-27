import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import styles from './Header.module.css';

export const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          <span className={styles.logoIcon}>🔗</span>
          <span className={styles.logoText}>MiniURL</span>
        </Link>

        <nav className={styles.nav}>
          {isAuthenticated ? (
            <>
              <Link
                to="/dashboard"
                className={`${styles.navLink} ${
                  isActive('/dashboard') ? styles.active : ''
                }`}
              >
                Dashboard
              </Link>
              <div className={styles.userSection}>
                <span className={styles.userEmail}>{user?.email}</span>
                <span className={styles.userPlan}>
                  {user?.is_premium ? '⭐ Premium' : 'Free'}
                </span>
                <button
                  onClick={logout}
                  className={styles.logoutBtn}
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className={`${styles.navLink} ${
                  isActive('/login') ? styles.active : ''
                }`}
              >
                Login
              </Link>
              <Link
                to="/register"
                className={`${styles.navLink} ${styles.registerLink} ${
                  isActive('/register') ? styles.active : ''
                }`}
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};
