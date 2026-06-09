import React, { useState } from 'react';
import { useLinks } from '../hooks/useLinks';
import { FREE_TIER_LIMITS } from '../config';
import styles from './LinkForm.module.css';

export const LinkForm: React.FC<{ isPremium: boolean; linksThisMonth: number }> = ({
  isPremium,
  linksThisMonth,
}) => {
  const [target, setTarget] = useState('');
  const [customCode, setCustomCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { createLink } = useLinks();

  const canCreateLink =
    isPremium || linksThisMonth < FREE_TIER_LIMITS.LINKS_PER_MONTH;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!target.trim()) {
      setError('Please enter a URL');
      return;
    }

    if (!target.startsWith('http://') && !target.startsWith('https://')) {
      setError('URL must start with http:// or https://');
      return;
    }

    if (!canCreateLink) {
      setError(
        `Free tier limit reached (${FREE_TIER_LIMITS.LINKS_PER_MONTH} links/month). Upgrade to Premium.`
      );
      return;
    }

    try {
      setLoading(true);
      const newLink = await createLink({
        target_url: target,
        custom_code: customCode || undefined,
      });
      setSuccess(`Link created: /${newLink.code}`);
      setTarget('');
      setCustomCode('');
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to create link';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.formContainer}>
      <h2>Create a new short link</h2>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label htmlFor="target">Long URL *</label>
          <input
            id="target"
            type="url"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="https://example.com/very/long/url"
            required
            disabled={loading}
            className={styles.input}
          />
        </div>

        {isPremium && (
          <div className={styles.formGroup}>
            <label htmlFor="customCode">Custom short code (optional)</label>
            <input
              id="customCode"
              type="text"
              value={customCode}
              onChange={(e) => setCustomCode(e.target.value)}
              placeholder="my-link"
              disabled={loading}
              className={styles.input}
            />
          </div>
        )}

        {!isPremium && (
          <div className={styles.tierInfo}>
            <span>
              {linksThisMonth}/{FREE_TIER_LIMITS.LINKS_PER_MONTH} links created
              this month
            </span>
          </div>
        )}

        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}

        <button
          type="submit"
          disabled={loading || !canCreateLink}
          className={styles.submitBtn}
        >
          {loading ? 'Creating...' : 'Shorten URL'}
        </button>
      </form>
    </div>
  );
};

export default LinkForm;
