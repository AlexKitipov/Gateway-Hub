import React, { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useLinks } from '../hooks/useLinks';
import LinkForm from '../components/LinkForm';
import LinkTable from '../components/LinkTable';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { stats, isLoading, fetchLinks, upgradeAccount } = useLinks();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchLinks();
  }, [user, fetchLinks, navigate]);

  const handleUpgrade = async () => {
    try {
      await upgradeAccount();
    } catch (err) {
      console.error('Upgrade failed:', err);
    }
  };

  if (!user) {
    return <div>Redirecting...</div>;
  }

  const isPremium = stats?.is_premium ?? user.is_premium;
  const linksThisMonth = stats?.links_this_month ?? 0;

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Dashboard</h1>
        {!isPremium && (
          <button
            onClick={handleUpgrade}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#764ba2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            Upgrade to Premium
          </button>
        )}
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div style={{ backgroundColor: '#f3f4f6', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>Plan</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{isPremium ? 'Premium' : 'Free'}</div>
          </div>
          <div style={{ backgroundColor: '#f3f4f6', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>Total Links</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.total_links}</div>
          </div>
          <div style={{ backgroundColor: '#f3f4f6', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>Total Clicks</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.total_clicks}</div>
          </div>
          <div style={{ backgroundColor: '#f3f4f6', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.9rem', color: '#666' }}>This Month</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.links_this_month}</div>
          </div>
        </div>
      )}

      {/* Create Link Form */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>Create New Short Link</h2>
        <LinkForm isPremium={isPremium} linksThisMonth={linksThisMonth} />
      </div>

      {/* Links Table */}
      <div>
        <h2 style={{ marginBottom: '1rem' }}>Your Links</h2>
        {isLoading ? <p>Loading...</p> : <LinkTable />}
      </div>
    </div>
  );
};

export default Dashboard;
