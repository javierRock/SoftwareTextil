import { useCallback, useEffect, useMemo, useState } from 'react';

import { fetchGroupedStockByCategory } from '../services/inventoryApi';
import { INVENTORY_CHANGED_EVENT } from '../utils/inventoryEvents';

export function useInventory() {
  const [data, setData] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdatedAt, setLastUpdatedAt] = useState('');

  const loadInventory = useCallback(async (filterValue) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetchGroupedStockByCategory({
        categoryId: filterValue === 'all' ? '' : filterValue,
      });

      setData(response);
      setCategories((current) => {
        if (filterValue === 'all') {
          return response;
        }

        return current.length > 0 || response.length === 0 ? current : response;
      });
      setLastUpdatedAt(new Intl.DateTimeFormat('es-PE', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(new Date()));
    } catch (loadError) {
      setError(loadError.message);
      setData([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refresh = useCallback(() => loadInventory(categoryFilter), [categoryFilter, loadInventory]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const handleInventoryChanged = () => {
      refresh();
    };

    window.addEventListener(INVENTORY_CHANGED_EVENT, handleInventoryChanged);
    return () => window.removeEventListener(INVENTORY_CHANGED_EVENT, handleInventoryChanged);
  }, [refresh]);

  const selectedData = useMemo(() => data, [data]);

  return {
    categories,
    categoryFilter,
    data: selectedData,
    error,
    isLoading,
    lastUpdatedAt,
    refresh,
    setCategoryFilter,
  };
}
