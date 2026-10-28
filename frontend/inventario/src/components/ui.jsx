import { useEffect } from 'react';

export function Icon({ name, size = 20 }) {
  const paths = {
    grid: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></>,
    box: <><path d="m4 7 8-4 8 4-8 4-8-4Z"/><path d="m4 7 8 4 8-4v10l-8 4-8-4V7Z"/><path d="M12 11v10"/></>,
    bag: <><path d="M6 8h12l1 13H5L6 8Z"/><path d="M9 9V6a3 3 0 0 1 6 0v3"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    truck: <><path d="M3 6h11v11H3zM14 10h4l3 3v4h-7z"/><circle cx="7" cy="19" r="2"/><circle cx="18" cy="19" r="2"/></>,
    card: <><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/></>,
    shirt: <path d="m8 3 4 2 4-2 5 3-3 5-2-1v11H8V10l-2 1-3-5 5-3Z"/>,
    chart: <><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></>,
    arrows: <><path d="M7 7h11l-3-3M17 17H6l3 3M18 7l3 3-3 3M6 17l-3-3 3-3"/></>,
    user: <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
    menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
    close: <path d="m6 6 12 12M18 6 6 18"/>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    plus: <path d="M12 5v14M5 12h14"/>,
    arrow: <path d="m9 18 6-6-6-6"/>,
    download: <><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></>,
    alert: <><path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5M12 18h.01"/></>,
    logout: <><path d="M10 17l5-5-5-5M15 12H3M15 4h5v16h-5"/></>,
    home: <><path d="m3 11 9-8 9 8"/><path d="M5 10v11h14V10M9 21v-7h6v7"/></>,
  };
  return <svg className="icon" aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name] || paths.box}</svg>;
}

export function PageHeader({ eyebrow, title, description, actions }) {
  return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{description && <p className="lede">{description}</p>}</div>{actions && <div className="page-actions">{actions}</div>}</header>;
}

export function Button({ children, variant = 'primary', icon, ...props }) {
  return <button className={`button button--${variant}`} {...props}>{icon && <Icon name={icon} size={17}/>}<span>{children}</span></button>;
}

export function Status({ children }) {
  const status = String(children || 'sin estado').toLowerCase();
  return <span className={`status status--${status}`}>{String(children || 'Sin estado').replaceAll('_', ' ')}</span>;
}

export function State({ loading, error, empty, onRetry, children }) {
  if (loading) return <div className="state-card" role="status"><span className="spinner"/><strong>Preparando información</strong><p>Un momento, estamos sincronizando con Zuren.</p></div>;
  if (error) return <div className="state-card state-card--error" role="alert"><Icon name="alert" size={28}/><strong>No pudimos cargar esta sección</strong><p>{error}</p>{onRetry && <Button variant="secondary" onClick={onRetry}>Reintentar</Button>}</div>;
  if (empty) return <div className="state-card"><span className="state-mark">Z</span><strong>Aún no hay registros</strong><p>Cuando exista actividad aparecerá organizada aquí.</p></div>;
  return children;
}

export function Field({ label, hint, children }) {
  return <label className="field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

export function Drawer({ open, title, description, onClose, children }) {
  useEffect(() => {
    if (!open) return undefined;
    function escape(event) { if (event.key === 'Escape') onClose(); }
    document.addEventListener('keydown', escape);
    return () => document.removeEventListener('keydown', escape);
  }, [open, onClose]);
  if (!open) return null;
  return <div className="drawer-layer" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><section className="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title"><header><div><p className="eyebrow">Formulario</p><h2 id="drawer-title">{title}</h2>{description && <p>{description}</p>}</div><button className="icon-button" type="button" onClick={onClose} aria-label="Cerrar"><Icon name="close"/></button></header>{children}</section></div>;
}

export function SubmitMessage({ error, success }) {
  if (!error && !success) return null;
  return <p className={`form-message ${error ? 'form-message--error' : ''}`} role="status">{error || success}</p>;
}

export function formatMoney(value, currency = 'PEN') {
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency }).format(Number(value || 0));
}

export function formatDate(value) {
  if (!value) return 'Sin fecha';
  return new Intl.DateTimeFormat('es-PE', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
}

export function valueOf(event, name) {
  const data = new FormData(event.currentTarget);
  return data.get(name)?.toString().trim() || '';
}
