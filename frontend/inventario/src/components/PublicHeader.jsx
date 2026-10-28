import { Link, NavLink } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { Icon } from './ui';

export function PublicHeader() {
  const { session, role } = useAuth();
  const target = role === 'cliente' ? '/pedidos' : '/panel';
  return <header className="public-header"><Link className="wordmark" to="/catalogo"><span>Z</span>ZUREN</Link><nav><NavLink to="/catalogo">Colección</NavLink>{session ? <><NavLink to={target}>Mi cuenta</NavLink>{role === 'cliente' && <NavLink className="cart-link" to="/carrito"><Icon name="bag"/>Carrito</NavLink>}</> : <><NavLink to="/login">Ingresar</NavLink><NavLink className="nav-cta" to="/registro">Crear cuenta</NavLink></>}</nav></header>;
}
