import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { Icon } from './ui';

const customerNav = [
  ['/catalogo', 'shirt', 'Tienda'], ['/carrito', 'bag', 'Carrito'], ['/pedidos', 'box', 'Mis pedidos'], ['/pagos', 'card', 'Mis pagos'],
];
const staffNav = [
  ['/panel', 'grid', 'Resumen'], ['/inventario', 'box', 'Inventario'], ['/stock-bajo', 'alert', 'Stock bajo'], ['/movimientos', 'arrows', 'Movimientos'], ['/catalogo-admin', 'shirt', 'Catálogo'], ['/pagos-admin', 'card', 'Pagos'], ['/despachos', 'truck', 'Despachos'], ['/usuarios', 'users', 'Usuarios'],
];

export function AppShell() {
  const { profile, role, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const isCustomer = role === 'cliente';
  const isAdmin = role === 'administrador';
  const navigation = (isCustomer ? customerNav : staffNav).filter(([path]) => isAdmin || path !== '/usuarios' && path !== '/pagos-admin' && path !== '/catalogo-admin');

  return <div className="app-shell">
    <button className={`nav-scrim ${open ? 'is-open' : ''}`} aria-label="Cerrar menú" onClick={() => setOpen(false)}/>
    <aside className={`sidebar ${open ? 'is-open' : ''}`}>
      <div className="brand"><span className="brand-mark">Z</span><div><strong>ZUREN</strong><small>Gestión textil</small></div><button className="icon-button mobile-only" onClick={() => setOpen(false)} aria-label="Cerrar menú"><Icon name="close"/></button></div>
      <nav aria-label="Navegación principal">
        <p className="nav-label">{isCustomer ? 'Mi cuenta' : 'Operaciones'}</p>
        {navigation.map(([path, icon, label]) => <NavLink key={path} to={path} onClick={() => setOpen(false)}><Icon name={icon}/><span>{label}</span></NavLink>)}
      </nav>
      <div className="sidebar-footer">
        <NavLink to="/perfil" onClick={() => setOpen(false)}><span className="avatar">{profile?.nombre?.[0] || 'Z'}</span><span><strong>{profile?.nombre || 'Mi perfil'}</strong><small>{profile?.rol_nombre || role}</small></span></NavLink>
        <button type="button" onClick={logout} aria-label="Cerrar sesión"><Icon name="logout"/></button>
      </div>
    </aside>
    <div className="app-main">
      <header className="mobile-bar"><button className="icon-button" onClick={() => setOpen(true)} aria-label="Abrir menú"><Icon name="menu"/></button><strong>ZUREN</strong><NavLink to="/perfil" aria-label="Perfil"><Icon name="user"/></NavLink></header>
      <main><Outlet/></main>
    </div>
  </div>;
}
