export function LoadingState() {
  return (
    <section className="state state-loading" aria-label="Cargando inventario">
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-line" />
      <div className="skeleton skeleton-line" />
      <div className="skeleton skeleton-line" />
    </section>
  );
}
