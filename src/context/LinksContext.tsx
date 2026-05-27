import { createContext, ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { linksApi } from '../services/api';
import { ShortLink } from '../types';

interface LinksContextValue {
  links: ShortLink[];
  loading: boolean;
  refresh: () => Promise<void>;
  createLink: (originalUrl: string) => Promise<void>;
  deleteLink: (id: string) => Promise<void>;
}

export const LinksContext = createContext<LinksContextValue | undefined>(undefined);

export function LinksProvider({ children }: { children: ReactNode }) {
  const [links, setLinks] = useState<ShortLink[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await linksApi.getAll();
      setLinks(res.data.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const value = useMemo<LinksContextValue>(
    () => ({
      links,
      loading,
      refresh,
      createLink: async (originalUrl) => {
        const res = await linksApi.create({ originalUrl });
        setLinks((prev) => [res.data.data, ...prev]);
      },
      deleteLink: async (id) => {
        await linksApi.remove(id);
        setLinks((prev) => prev.filter((item) => item.id !== id));
      },
    }),
    [links, loading, refresh],
  );

  return <LinksContext.Provider value={value}>{children}</LinksContext.Provider>;
}
