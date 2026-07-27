export function CategoryFilter({ categories, value, onChange }) {
  return (
    <label className="filter-field" htmlFor="category-filter">
      <span className="filter-label">Filtrar por categoría</span>
      <select
        id="category-filter"
        className="filter-select"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        aria-label="Filtrar inventario por categoría"
      >
        <option value="all">Todas las categorías</option>
        {categories.map((category) => (
          <option key={category.categoria_id} value={category.categoria_id}>
            {category.categoria} ({category.cantidad_total})
          </option>
        ))}
      </select>
    </label>
  );
}
