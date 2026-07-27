import { StockItem } from './StockItem';

export function CategoryStockCard({ category }) {
  return (
    <section className="category-card" aria-labelledby={`category-${category.categoria_id}`}>
      <header className="category-card__header">
        <div>
          <p className="eyebrow">Categoría</p>
          <h2 id={`category-${category.categoria_id}`}>{category.categoria}</h2>
        </div>
        <div className="category-card__total">
          <span>Total</span>
          <strong>{category.cantidad_total}</strong>
        </div>
      </header>

      <ul className="stock-list">
        {category.prendas.map((item) => (
          <StockItem key={item.prenda_id} item={item} />
        ))}
      </ul>
    </section>
  );
}
