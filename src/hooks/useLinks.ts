import { useContext } from 'react';
import { LinksContext } from '../context/LinksContext';

export function useLinks() {
  const context = useContext(LinksContext);
  if (!context) {
    throw new Error('useLinks must be used within LinksProvider');
  }
  return context;
}
