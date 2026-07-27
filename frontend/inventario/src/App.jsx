import { Navigate, Route, Routes, useLocation } from 'react-router-dom';

import { useAuth } from './auth/AuthContext';
import { AppShell } from './components/AppShell';
import { State } from './components/ui';
import { AdminPaymentsPage, CatalogAdminPage, UsersPage } from './pages/AdminPages';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import { CatalogPage, ProductPage } from './pages/CatalogPages';
import { CartPage, CustomerPaymentsPage, OrdersPage } from './pages/CustomerPages';
import { DashboardPage, InventoryPage, LowStockPage } from './pages/InventoryPages';
import { ProfilePage } from './pages/ProfilePage';
import { DispatchesPage } from './pages/DispatchesPage';
import { StockOperationsPage } from './pages/StockOperationsPage';

const STAFF = ['administrador', 'encargado de inventario'];

function Protected({ roles, children }) {
  const { session, role, loading } = useAuth();
  const location = useLocation();
  if (loading) return <div className="route-loading"><State loading/></div>;
  if (!session) return <Navigate to="/login" state={{ from: location.pathname }} replace/>;
  if (roles && !roles.includes(role)) return <Navigate to={role === 'cliente' ? '/catalogo' : '/panel'} replace/>;
  return children;
}

function Home() {
  const { session, role } = useAuth();
  if (!session || role === 'cliente') return <Navigate to="/catalogo" replace/>;
  return <Navigate to="/panel" replace/>;
}

export default function App() {
  return <Routes>
    <Route path="/" element={<Home/>}/>
    <Route path="/login" element={<LoginPage/>}/>
    <Route path="/registro" element={<RegisterPage/>}/>
    <Route path="/catalogo" element={<CatalogPage/>}/>
    <Route path="/catalogo/:id" element={<ProductPage/>}/>
    <Route element={<Protected><AppShell/></Protected>}>
      <Route path="/perfil" element={<ProfilePage/>}/>
      <Route path="/carrito" element={<Protected roles={['cliente']}><CartPage/></Protected>}/>
      <Route path="/pedidos" element={<Protected roles={['cliente']}><OrdersPage/></Protected>}/>
      <Route path="/pagos" element={<Protected roles={['cliente']}><CustomerPaymentsPage/></Protected>}/>
      <Route path="/panel" element={<Protected roles={STAFF}><DashboardPage/></Protected>}/>
      <Route path="/inventario" element={<Protected roles={STAFF}><InventoryPage/></Protected>}/>
      <Route path="/stock-bajo" element={<Protected roles={STAFF}><LowStockPage/></Protected>}/>
      <Route path="/movimientos" element={<Protected roles={STAFF}><StockOperationsPage/></Protected>}/>
      <Route path="/despachos" element={<Protected roles={STAFF}><DispatchesPage/></Protected>}/>
      <Route path="/catalogo-admin" element={<Protected roles={['administrador']}><CatalogAdminPage/></Protected>}/>
      <Route path="/usuarios" element={<Protected roles={['administrador']}><UsersPage/></Protected>}/>
      <Route path="/pagos-admin" element={<Protected roles={['administrador']}><AdminPaymentsPage/></Protected>}/>
    </Route>
    <Route path="*" element={<Navigate to="/" replace/>}/>
  </Routes>;
}
