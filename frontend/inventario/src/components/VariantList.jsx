function etiquetaVariante(variante) {
  return variante.color ? `${variante.talla} · ${variante.color}` : variante.talla;
}

export function VariantList({ variantes, prenda }) {
  if (!variantes?.length) {
    return null;
  }

  return (
    <ul className="variant-list" aria-label={`Variantes de ${prenda}`}>
      {variantes.map((variante) => (
        <li className="variant-item" key={variante.variante_id}>
          <div>
            <strong>{etiquetaVariante(variante)}</strong>
            <span className="variant-item__sku">{variante.sku}</span>
          </div>
          <div className="variant-item__cantidades">
            <output aria-label={`Disponible de ${etiquetaVariante(variante)}`}>
              {variante.cantidad_disponible}
            </output>
            {variante.cantidad_reservada > 0 && (
              <span className="variant-item__reservado">
                {variante.cantidad_reservada} reservada(s)
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
