// hooks/useFilters.ts
import { useState, useCallback } from 'react';

export function useFilters<T extends Record<string, any>>(initialValues: T) {
  const [filters, setFilters] = useState<T>(initialValues);

  const updateFilter = useCallback((key: keyof T, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters(initialValues);
  }, [initialValues]);

  const hasActiveFilters = useCallback(() => {
    return Object.values(filters).some(v => v !== '' && v !== 'all');
  }, [filters]);

  return { filters, updateFilter, clearFilters, hasActiveFilters: hasActiveFilters() };
}