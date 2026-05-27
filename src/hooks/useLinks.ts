import { useContext } from 'react';
import { LinksContext } from '../context/LinksContext';
import { LinksContextType } from '../types';

export const useLinks = (): LinksContextType => {
  const context = useContext(LinksContext);
  if (!context) {
    throw new Error('useLinks must be used within LinksProvider');
  }
  return context;
};
