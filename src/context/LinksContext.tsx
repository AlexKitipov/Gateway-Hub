import React, { createContext, useCallback, useState } from 'react';
import { linksAPI, userAPI } from '../services/api';
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
      const [linksResponse, statsResponse] = await Promise.all([
        linksAPI.getAll(),
        userAPI.getStats(),
      ]);
      setLinks(linksResponse.data.links);
      setStats(statsResponse.data);
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
        const response = await linksAPI.create(data);
        const newLink = response.data;
        setLinks((prev) => [newLink, ...prev]);
        setStats((prev) =>
          prev
            ? {
                ...prev,
                total_links: prev.total_links + 1,
                links_this_month: prev.links_this_month + 1,
              }
            : prev
        );
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
      await linksAPI.delete(code);
      setLinks((prev) => prev.filter((link) => link.code !== code));
      setStats((prev) =>
        prev ? { ...prev, total_links: Math.max(prev.total_links - 1, 0) } : prev
      );
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
      const response = await userAPI.upgrade();
      setStats((prev) =>
        prev
          ? {
              ...prev,
              is_premium: true,
              premium_until: response.data.premium_until,
            }
          : prev
      );
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to upgrade account';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value: LinksContextType = {
    links,
    stats,
    isLoading,
    error,
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
