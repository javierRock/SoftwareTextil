import { useMemo } from 'react';

import { CategoryFilter } from './components/CategoryFilter';
import { CategoryStockCard } from './components/CategoryStockCard';
import { EmptyState } from './components/EmptyState';
import { ErrorState } from './components/ErrorState';
import { LoadingState } from './components/LoadingState';
import { useInventory } from './hooks/useInventory';

export default function App() {
  const {
    categories,
    categoryFilter,
    data,
    error,
    isLoading,
    refresh,
    setCategoryFilter,
    lastUpdatedAt,
  } = useInventory();

  const totals = useMemo(() => {
    const totalItems = data.reduce((sum, category) => sum + category.cantidad_total, 0);
    const totalPrendas = data.reduce((sum, category) => sum + category.prendas.length, 0);
    return { totalItems, totalPrendas, totalCategories: data.length };
  }, [data]);

  return (
    <div className="inventory-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">SoftwareTextil / inventario</p>
          <h1>Panel de inventario</h1>
        </div>
        <button className="ghost-button" type="button" onClick={refresh}>
          Reintentar consulta
        </button>
      </header>

      <div className="inventory-layout">
        <aside className="sidebar" aria-label="Filtros de inventario">
          <section className="panel panel-hero">
            <p className="eyebrow">Estado general</p>
            <strong>{totals.totalItems} prendas</strong>
            <span>{totals.totalCategories} categorías con stock visible</span>
          </section>

          <section className="panel">
            <CategoryFilter
              categories={categories}
              value={categoryFilter}
              onChange={setCategoryFilter}
            />
          </section>

          <section className="panel panel-metrics" aria-label="Resumen del inventario">
            <div>
              <span>Total prendas</span>
              <strong>{totals.totalItems}</strong>
            </div>
            <div>
              <span>Prendas agrupadas</span>
              <strong>{totals.totalPrendas}</strong>
            </div>
            <div>
              <span>Última carga</span>
              <strong>{lastUpdatedAt ?? 'Pendiente'}</strong>
            </div>
          </section>
        </aside>

        <main className="content" aria-live="polite">
          {isLoading ? <LoadingState /> : null}
          {!isLoading && error ? <ErrorState message={error} onRetry={refresh} /> : null}
          {!isLoading && !error && data.length === 0 ? <EmptyState /> : null}
          {!isLoading && !error && data.length > 0 ? (
            <div className="category-grid">
              {data.map((category) => (
                <CategoryStockCard key={category.categoria_id} category={category} />
              ))}
            </div>
          ) : null}
        </main>
      </div>
    </div>
  );
}
