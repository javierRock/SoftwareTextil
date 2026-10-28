import { useState } from 'react';

import { Button, Drawer, Field, Icon, PageHeader, State, Status, SubmitMessage, formatDate } from '../components/ui';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

export function DashboardPage() {
  const resource = useApi(async (signal) => {
    const [users, garments, stock, low, dispatches] = await Promise.all([
      api.users.list(null, { signal }).catch(() => []), api.garments.list(null, { signal }), api.stock.list({ signal }), api.stock.low({ signal }), api.dispatches.list(null, { signal }).catch(() => []),
    ]);
    return { users, garments, stock, low, dispatches };
  }, []);
  const data = resource.data;
  const units = (data?.stock || []).reduce((sum, item) => sum + item.cantidad_actual, 0);
  return <><PageHeader eyebrow="Pulso de Zuren" title="Panel de control" description="Lo esencial de la operación, actualizado en una sola vista." actions={<Button variant="secondary" onClick={resource.reload}>Actualizar</Button>}/><State loading={resource.loading} error={resource.error} onRetry={resource.reload}>{data && <><section className="metric-grid"><Metric icon="users" label="Usuarios activos" value={(data.users || []).filter((item) => item.estado === 'activo').length} note="Equipo y clientes"/><Metric icon="shirt" label="Prendas publicadas" value={(data.garments || []).length} note="Catálogo total"/><Metric icon="box" label="Unidades en almacén" value={units} note={`${data.stock.length} ubicaciones`}/><Metric icon="alert" label="Stock bajo" value={data.low.length} note="Requiere atención" danger={data.low.length > 0}/></section><section className="dashboard-grid"><div className="card dashboard-panel"><header><div><p className="eyebrow">Atención inmediata</p><h2>Reposición sugerida</h2></div></header>{data.low.length ? <div className="compact-list">{data.low.slice(0, 5).map((item) => <div key={item.variante_id}><span className="item-monogram">{item.talla || 'ZR'}</span><p><strong>{item.prenda}</strong><small>{item.color} · {item.sku}</small></p><b>−{item.faltante}</b></div>)}</div> : <p className="muted">Todo el stock se encuentra sobre el mínimo.</p>}</div><div className="card dashboard-panel dark-panel"><p className="eyebrow">Almacén</p><h2>{units} unidades listas</h2><p>La lectura agrupa disponibilidad real y reservas para evitar promesas fuera de stock.</p><div className="warehouse-line"><span style={{ width: `${Math.min(100, units)}%` }}/></div><small>Sincronización operativa</small></div><div className="card dashboard-panel"><header><div><p className="eyebrow">Logística</p><h2>Despachos recientes</h2></div></header><div className="compact-list">{(data.dispatches || []).slice(0, 4).map((item) => <div key={item.id}><Icon name="truck"/><p><strong>Pedido #{item.pedido_id.slice(0, 8)}</strong><small>{item.direccion_entrega}</small></p><Status>{item.estado}</Status></div>)}</div></div></section></>}</State></>;
}

function Metric({ icon, label, value, note, danger }) { return <article className={`metric-card ${danger ? 'metric-card--danger' : ''}`}><div><p>{label}</p><Icon name={icon}/></div><strong>{value}</strong><span>{note}</span></article>; }

export function InventoryPage() {
  const resource = useApi((signal) => api.stock.grouped('', { signal }), []);
  const categories = useApi((signal) => api.categories.list(null, { signal }), []);
  const [filter, setFilter] = useState('');
  const [downloading, setDownloading] = useState('');
  const [error, setError] = useState('');
  const groups = (resource.data || []).filter((item) => !filter || item.categoria_id === filter);
  const total = groups.reduce((sum, group) => sum + group.cantidad_total, 0);
  async function report(format) { setDownloading(format); setError(''); try { await api.stock.report(format, filter); } catch (downloadError) { setError(downloadError.message); } finally { setDownloading(''); } }
  return <><PageHeader eyebrow="Almacén" title="Inventario agrupado" description="Categorías, prendas y variantes con disponibilidad real." actions={<><Button variant="secondary" icon="download" onClick={() => report('pdf')} disabled={downloading}>PDF</Button><Button variant="secondary" icon="download" onClick={() => report('xlsx')} disabled={downloading}>XLSX</Button></>}/><section className="filter-bar"><Field label="Categoría"><select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="">Todas</option>{(categories.data || []).map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select></Field><div><span>Unidades visibles</span><strong>{total}</strong></div></section><SubmitMessage error={error}/><State loading={resource.loading} error={resource.error} empty={!groups.length} onRetry={resource.reload}><div className="inventory-groups">{groups.map((group) => <section className="card inventory-group" key={group.categoria_id}><header><div><p className="eyebrow">Categoría</p><h2>{group.categoria}</h2></div><strong>{group.cantidad_total}<small>unidades</small></strong></header><div>{group.prendas.map((garment) => <details key={garment.prenda_id}><summary><span>{garment.nombre}</span><b>{garment.cantidad}</b></summary><div className="variant-table">{garment.variantes.map((variant) => <div key={variant.variante_id}><span><strong>{variant.talla || 'Única'} · {variant.color || 'Natural'}</strong><small>{variant.sku}</small></span><span>Reservado <b>{variant.cantidad_reservada}</b></span><span>Disponible <b>{variant.cantidad_disponible}</b></span></div>)}</div></details>)}</div></section>)}</div></State></>;
}

export function LowStockPage() {
  const resource = useApi((signal) => api.stock.low({ signal }), []);
  return <><PageHeader eyebrow="Alertas" title="Stock bajo" description="Prioriza las variantes que alcanzaron su mínimo operativo."/><State loading={resource.loading} error={resource.error} empty={!resource.data?.length} onRetry={resource.reload}><div className="card table-wrap"><table><thead><tr><th>Prenda</th><th>Variante</th><th>Categoría</th><th>Actual</th><th>Mínimo</th><th>Faltante</th></tr></thead><tbody>{(resource.data || []).map((item) => <tr key={item.variante_id}><td data-label="Prenda"><strong>{item.prenda}</strong><small>{item.sku}</small></td><td data-label="Variante">{item.talla} · {item.color}</td><td data-label="Categoría">{item.categoria}</td><td data-label="Actual">{item.cantidad_actual}</td><td data-label="Mínimo">{item.nivel_minimo}</td><td data-label="Faltante"><span className="shortage">+{item.faltante}</span></td></tr>)}</tbody></table></div></State></>;
}

export function MovementsPage() {
  const stock = useApi((signal) => api.stock.list({ signal }), []);
  const variants = useApi((signal) => api.variants.list(null, { signal }), []);
  const [selected, setSelected] = useState('');
  const movements = useApi((signal) => selected ? api.movements(selected, { signal }) : Promise.resolve([]), [selected]);
  const [drawer, setDrawer] = useState('');
  const [message, setMessage] = useState({ error: '', success: '' });
  const variantMap = new Map((variants.data || []).map((item) => [item.id, item]));
  async function submit(event) {
    event.preventDefault(); setMessage({ error: '', success: '' });
    const form = new FormData(event.currentTarget);
    const body = { variante_id: form.get('variante_id'), motivo: form.get('motivo') };
    if (drawer === 'ajustes') body.nueva_cantidad = Number(form.get('cantidad')); else body.cantidad = Number(form.get('cantidad'));
    try { await api.stock.move(drawer, body); setMessage({ error: '', success: 'Movimiento registrado correctamente.' }); stock.reload(); movements.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); }
  }
  return <><PageHeader eyebrow="Trazabilidad" title="Movimientos" description="Registra y consulta cada cambio de existencias." actions={<><Button icon="plus" onClick={() => setDrawer('ingresos')}>Ingreso</Button><Button variant="secondary" onClick={() => setDrawer('salidas')}>Salida</Button><Button variant="secondary" onClick={() => setDrawer('ajustes')}>Ajuste</Button></>}/><section className="filter-bar"><Field label="Stock a consultar"><select value={selected} onChange={(event) => setSelected(event.target.value)}><option value="">Selecciona una ubicación</option>{(stock.data || []).map((item) => { const variant = variantMap.get(item.variante_id); return <option key={item.id} value={item.id}>{variant ? `${variant.sku || variant.id} · ` : ''}{item.ubicacion} · {item.cantidad_actual} unidades</option>; })}</select></Field></section><State loading={stock.loading || movements.loading} error={stock.error || variants.error || movements.error} empty={!movements.data?.length} onRetry={movements.reload}><div className="card table-wrap"><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Cantidad</th><th>Motivo</th><th>Responsable</th></tr></thead><tbody>{(movements.data || []).map((item) => <tr key={item.id}><td data-label="Fecha">{formatDate(item.fecha)}</td><td data-label="Tipo"><Status>{item.tipo}</Status></td><td data-label="Cantidad"><strong>{item.tipo === 'salida' ? '−' : '+'}{item.cantidad}</strong></td><td data-label="Motivo">{item.motivo}</td><td data-label="Responsable">{item.registrado_por.slice(0, 8)}</td></tr>)}</tbody></table></div></State><Drawer open={Boolean(drawer)} onClose={() => setDrawer('')} title={`${drawer === 'ajustes' ? 'Nuevo ajuste' : drawer === 'salidas' ? 'Registrar salida' : 'Registrar ingreso'}`} description="La sesión actual quedará registrada como responsable."><form className="drawer-form" onSubmit={submit}><Field label="Variante"><select name="variante_id" required><option value="">Selecciona una variante</option>{(variants.data || []).map((item) => <option value={item.id} key={item.id}>{item.sku || item.id} · {item.talla} · {item.color}</option>)}</select></Field><Field label={drawer === 'ajustes' ? 'Nueva cantidad total' : 'Cantidad'}><input name="cantidad" type="number" min={drawer === 'ajustes' ? 0 : 1} required/></Field><Field label="Motivo"><textarea name="motivo" rows="4" required/></Field><SubmitMessage {...message}/><Button type="submit">Confirmar movimiento</Button></form></Drawer></>;
}
