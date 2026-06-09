import React, { useState } from 'react';
import { useLinks } from '../hooks/useLinks';
import { ShortLink } from '../types';
import styles from './LinkTable.module.css';

export const LinkTable: React.FC = () => {
  const { links, deleteLink, isLoading } = useLinks();
  const [deletingCode, setDeletingCode] = useState<string | null>(null);

  const handleDelete = async (code: string) => {
    if (window.confirm('Are you sure you want to delete this link?')) {
      try {
        setDeletingCode(code);
        await deleteLink(code);
      } finally {
        setDeletingCode(null);
      }
    }
  };

  const handleCopy = (code: string) => {
    const shortUrl = `${window.location.origin}/${code}`;
    navigator.clipboard.writeText(shortUrl);
    alert('Copied to clipboard!');
  };

  if (isLoading && links.length === 0) {
    return <div className={styles.loading}>Loading links...</div>;
  }

  if (links.length === 0) {
    return (
      <div className={styles.empty}>
        <p>No short links yet. Create your first one above!</p>
      </div>
    );
  }

  return (
    <div className={styles.tableContainer}>
      <h2>Your Links</h2>
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Short URL</th>
              <th>Target URL</th>
              <th>Clicks</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {links.map((link: ShortLink) => (
              <tr key={link.id}>
                <td className={styles.codeCell}>
                  <code>{link.code}</code>
                </td>
                <td className={styles.targetCell}>
                  <a href={link.target_url} target="_blank" rel="noreferrer">
                    {link.target_url.length > 50
                      ? link.target_url.substring(0, 50) + '...'
                      : link.target_url}
                  </a>
                </td>
                <td className={styles.clicksCell}>{link.click_count}</td>
                <td>{new Date(link.created_at).toLocaleDateString()}</td>
                <td className={styles.actionsCell}>
                  <button
                    onClick={() => handleCopy(link.code)}
                    className={styles.copyBtn}
                    title="Copy to clipboard"
                  >
                    📋
                  </button>
                  <button
                    onClick={() => handleDelete(link.code)}
                    disabled={deletingCode === link.code}
                    className={styles.deleteBtn}
                    title="Delete link"
                  >
                    {deletingCode === link.code ? '⏳' : '🗑️'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LinkTable;
