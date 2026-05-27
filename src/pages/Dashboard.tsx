import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useLinks } from '../hooks/useLinks';
import { LinkForm } from '../components/LinkForm';
import { LinkTable } from '../components/LinkTable';
import { FREE_TIER_LIMITS } from '../config';
import './Dashboard.css';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { stats, fetchLinks, upgradeAccount, isLoading } = useLinks();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchLinks();
  }, [isAuthenticated, navigate, fetchLinks]);

  if (!user) {
    return <div className="loading">Loading...</div>;
  }

  const linksThisMonth = stats?.links_this_month || 0;
  const isPremium = user.is_premium;

  return (
    <div className="dashboard">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h1>Dashboard</h1>
            <p className="user-info">
              {isPremium ? '⭐ Premium User' : '📦 Free Plan'}
            </p>
          </div>

          {!isPremium && (
            <button
              onClick={upgradeAccount}
              disabled={isLoading}
              className="upgrade-btn"
            >
              {isLoading ? 'Processing...' : 'Upgrade to Premium'}
            </button>
          )}
        </div>

        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Total Links</div>
              <div className="stat-value">{stats.total_links}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Total Clicks</div>
              <div className="stat-value">{stats.total_clicks}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">This Month</div>
              <div className="stat-value">
                {linksThisMonth}
                {!isPremium && `/${FREE_TIER_LIMITS.LINKS_PER_MONTH}`}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Plan</div>
              <div className="stat-value">
                {isPremium ? 'Premium ⭐' : 'Free'}
              </div>
            </div>
          </div>
        )}

        {!isPremium && (
          <div className="tier-warning">
            <span className="warning-icon">⚠️</span>
            <div className="warning-content">
              <p>
                <strong>Free tier limit:</strong> You can create{' '}
                {FREE_TIER_LIMITS.LINKS_PER_MONTH} links per month. Each link
                can receive up to {FREE_TIER_LIMITS.CLICKS_PER_LINK} clicks.
              </p>
              <p>
                Upgrade to Premium for unlimited links, custom domains, and
                advanced analytics.
              </p>
            </div>
          </div>
        )}

        <LinkForm isPremium={isPremium} linksThisMonth={linksThisMonth} />
        <LinkTable />
      </div>
    </div>
  );
};
