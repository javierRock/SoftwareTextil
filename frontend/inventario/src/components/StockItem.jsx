export function StockItem({ item }) {
  return (
    <li className="stock-item">
      <div>
        <strong>{item.nombre}</strong>
        <span>ID {item.prenda_id}</span>
      </div>
      <output aria-label={`Cantidad disponible para ${item.nombre}`}>{item.cantidad}</output>
    </li>
  );
}
