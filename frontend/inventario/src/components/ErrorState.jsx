export function ErrorState({ message, onRetry }) {
  return (
    <section className="state state-error" role="alert" aria-live="assertive">
      <h2>Error al cargar el inventario</h2>
      <p>{message}</p>
      <button type="button" className="primary-button" onClick={onRetry}>
        Reintentar
      </button>
    </section>
  );
}
