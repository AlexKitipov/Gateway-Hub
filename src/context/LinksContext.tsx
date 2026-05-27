import React, { createContext, useCallback, useState } from 'react';
import { apiClient } from '../services/api';
import {
  LinksContextType,
  ShortLink,
  CreateLinkRequest,
  UserStats,
} from '../types';

export const LinksContext = createContext<LinksContextType | undefined>(
  undefined
);

interface LinksProviderProps {
  children: React.ReactNode;
}

export const LinksProvider: React.FC<LinksProviderProps> = ({ children }) => {
  const [links, setLinks] = useState<ShortLink[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLinks = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      const [linksData, statsData] = await Promise.all([
        apiClient.getLinks(),
        apiClient.getUserStats(),
      ]);
      setLinks(linksData);
      setStats(statsData);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch links';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createLink = useCallback(
    async (data: CreateLinkRequest): Promise<ShortLink> => {
      try {
        setError(null);
        setIsLoading(true);
        const newLink = await apiClient.createLink(data);
        setLinks((prev) => [newLink, ...prev]);
        return newLink;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to create link';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const deleteLink = useCallback(async (code: string) => {
    try {
      setError(null);
      setIsLoading(true);
      await apiClient.deleteLink(code);
      setLinks((prev) => prev.filter((link) => link.code !== code));
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to delete link';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const upgradeAccount = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      await apiClient.upgradeAccount();
      if (stats) {
        setStats({ ...stats, plan: 'premium' });
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to upgrade account';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [stats]);

  const value: LinksContextType = {
    links,
    isLoading,
    error,
    stats,
    fetchLinks,
    createLink,
    deleteLink,
    upgradeAccount,
  };

  return (
    <LinksContext.Provider value={value}>
      {children}
    </LinksContext.Provider>
  );
};
