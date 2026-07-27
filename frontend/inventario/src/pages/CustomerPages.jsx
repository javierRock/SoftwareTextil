import { useState } from 'react';
import { Link } from 'react-router-dom';

import { Button, Drawer, Field, PageHeader, State, Status, SubmitMessage, formatDate, formatMoney } from '../components/ui';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

function rows(data) { return Array.isArray(data) ? data : data?.resultados || []; }

export function CartPage() {
  const resource = useApi((signal) => api.carts.list(null, { signal }), []);
  const [working, setWorking] = useState('');
  const [error, setError] = useState('');
  const carts = rows(resource.data);
  const cart = carts.find((item) => item.estado === 'abierto') || carts[0];
  const items = cart?.items || [];
  const total = items.reduce((sum, item) => sum + Number(item.precio_monto || 0) * item.cantidad, 0);

  async function remove(variantId) {
    setWorking(variantId); setError('');
    try { await api.carts.remove(cart.id, variantId); resource.reload(); } catch (actionError) { setError(actionError.message); } finally { setWorking(''); }
  }
  async function checkout() {
    setWorking('checkout'); setError('');
    try { await api.orders.create({ carrito_id: cart.id }); resource.reload(); } catch (actionError) { setError(actionError.message); } finally { setWorking(''); }
  }

  return <><PageHeader eyebrow="Tu selección" title="Carrito" description="Revisa cantidades antes de convertir tu selección en pedido."/><State loading={resource.loading} error={resource.error || error} empty={!cart || !items.length} onRetry={resource.reload}><div className="split-layout"><section className="card list-card">{items.map((item) => <article className="cart-item" key={item.id || item.variante_id}><div className="item-monogram">ZR</div><div><p className="eyebrow">Variante</p><h3>{item.prenda_nombre || `Pieza ${item.variante_id.slice(0, 8)}`}</h3><p>{item.talla && `${item.talla} · `}{item.color || ''} · Cantidad {item.cantidad}</p></div><strong>{formatMoney(Number(item.precio_monto || 0) * item.cantidad, item.precio_moneda)}</strong><button className="text-button danger" disabled={working === item.variante_id} onClick={() => remove(item.variante_id)}>Quitar</button></article>)}</section><aside className="card order-summary"><p className="eyebrow">Resumen</p><h2>Tu pedido</h2><div><span>{items.length} referencias</span><strong>{formatMoney(total, items[0]?.precio_moneda)}</strong></div><p>Los precios y disponibilidad finales son validados por el servidor.</p><SubmitMessage error={error}/><Button onClick={checkout} disabled={working === 'checkout'}>{working === 'checkout' ? 'Creando pedido…' : 'Confirmar pedido'}</Button><Link to="/catalogo">Seguir comprando</Link></aside></div></State></>;
}

export function OrdersPage() {
  const resource = useApi((signal) => api.orders.list(null, { signal }), []);
  const [error, setError] = useState('');
  async function cancel(id) { setError(''); try { await api.orders.action(id, 'cancelar'); resource.reload(); } catch (actionError) { setError(actionError.message); } }
  const orders = rows(resource.data);
  return <><PageHeader eyebrow="Historial" title="Mis pedidos" description="Cada pieza, pago y estado en un solo lugar." actions={<Link className="button button--secondary" to="/catalogo">Ver colección</Link>}/><SubmitMessage error={error}/><State loading={resource.loading} error={resource.error} empty={!orders.length} onRetry={resource.reload}><div className="order-grid">{orders.map((order) => <article className="card order-card" key={order.id}><header><div><p className="eyebrow">Pedido #{order.id.slice(0, 8)}</p><h2>{formatMoney(order.total_monto, order.total_moneda)}</h2></div><Status>{order.estado}</Status></header><p>{formatDate(order.fecha_creacion)} · {(order.detalles || []).reduce((sum, item) => sum + item.cantidad, 0)} unidades</p><div className="order-lines">{(order.detalles || []).map((detail) => <span key={detail.id}>{detail.prenda_nombre || detail.variante_id.slice(0, 8)} <b>× {detail.cantidad}</b></span>)}</div><footer>{order.estado === 'creado' && <><Link className="button button--primary" to={`/pagos?pedido=${order.id}&monto=${order.total_monto}`}>Registrar pago</Link><button className="text-button danger" onClick={() => cancel(order.id)}>Cancelar</button></>}</footer></article>)}</div></State></>;
}

export function CustomerPaymentsPage() {
  const resource = useApi((signal) => api.payments.list({ pagina: 1, tamano: 100 }, { signal }), []);
  const params = new window.URLSearchParams(window.location.search);
  const [open, setOpen] = useState(Boolean(params.get('pedido')));
  const [message, setMessage] = useState({ error: '', success: '' });
  const payments = rows(resource.data);
  async function submit(event) {
    event.preventDefault(); setMessage({ error: '', success: '' });
    const form = new FormData(event.currentTarget);
    try {
      await api.payments.create({ pedido_id: form.get('pedido_id'), monto: form.get('monto'), metodo: form.get('metodo'), referencia: form.get('referencia') });
      setMessage({ error: '', success: 'Pago registrado. Lo revisaremos pronto.' }); resource.reload();
    } catch (error) { setMessage({ error: error.message, success: '' }); }
  }
  return <><PageHeader eyebrow="Finanzas" title="Mis pagos" description="Registra una operación y sigue su validación." actions={<Button icon="plus" onClick={() => setOpen(true)}>Registrar pago</Button>}/><State loading={resource.loading} error={resource.error} empty={!payments.length} onRetry={resource.reload}><div className="card table-wrap"><table><thead><tr><th>Referencia</th><th>Pedido</th><th>Método</th><th>Monto</th><th>Fecha</th><th>Estado</th></tr></thead><tbody>{payments.map((payment) => <tr key={payment.id}><td data-label="Referencia">{payment.referencia || 'Sin referencia'}</td><td data-label="Pedido">#{payment.pedido_id.slice(0, 8)}</td><td data-label="Método">{payment.metodo}</td><td data-label="Monto"><strong>{formatMoney(payment.monto_monto, payment.monto_moneda)}</strong></td><td data-label="Fecha">{formatDate(payment.fecha)}</td><td data-label="Estado"><Status>{payment.estado}</Status></td></tr>)}</tbody></table></div></State><Drawer open={open} onClose={() => setOpen(false)} title="Registrar pago" description="El equipo validará la referencia y el monto."><form className="drawer-form" onSubmit={submit}><Field label="Pedido"><input name="pedido_id" defaultValue={params.get('pedido') || ''} required/></Field><Field label="Monto pagado"><input name="monto" defaultValue={params.get('monto') || ''} type="number" min="0.01" step="0.01" required/></Field><Field label="Método"><select name="metodo"><option value="transferencia">Transferencia</option><option value="yape">Yape</option><option value="tarjeta">Tarjeta</option><option value="efectivo">Efectivo</option></select></Field><Field label="Referencia"><input name="referencia" placeholder="Código de operación"/></Field><SubmitMessage {...message}/><Button type="submit">Enviar para revisión</Button></form></Drawer></>;
}
