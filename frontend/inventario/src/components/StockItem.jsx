import { VariantList } from './VariantList';

export function StockItem({ item }) {
  return (
    <li className="stock-item">
      <div className="stock-item__header">
        <div>
          <strong>{item.nombre}</strong>
          <span>{item.variantes.length} variante(s)</span>
        </div>
        <output aria-label={`Cantidad total de ${item.nombre}`}>{item.cantidad}</output>
      </div>

      <VariantList variantes={item.variantes} prenda={item.nombre} />
    </li>
  );
}
