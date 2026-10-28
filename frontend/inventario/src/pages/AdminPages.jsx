import { useState } from 'react';

import { Button, Drawer, Field, PageHeader, State, Status, SubmitMessage, formatDate, formatMoney } from '../components/ui';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

const resources = {
  prendas: { api: api.garments, title: 'Prendas' },
  variantes: { api: api.variants, title: 'Variantes' },
  categorias: { api: api.categories, title: 'Categorías' },
  tipos: { api: api.types, title: 'Tipos de producto' },
};

export function CatalogAdminPage() {
  const [tab, setTab] = useState('prendas');
  const current = resources[tab];
  const resource = useApi((signal) => current.api.list(null, { signal }), [tab]);
  const categories = useApi((signal) => api.categories.list(null, { signal }), []);
  const types = useApi((signal) => api.types.list(null, { signal }), []);
  const garments = useApi((signal) => api.garments.list(null, { signal }), []);
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState({ error: '', success: '' });
  async function submit(event) {
    event.preventDefault(); setMessage({ error: '', success: '' });
    const form = new FormData(event.currentTarget);
    let body;
    if (tab === 'categorias') body = { nombre: form.get('nombre'), descripcion: form.get('descripcion') };
    if (tab === 'tipos') body = { nombre: form.get('nombre'), atributos_base: {} };
    if (tab === 'prendas') {
      body = form;
      const sizes = body.get('tallas_texto').split(',').map((value) => value.trim()).filter(Boolean);
      body.set('precio_moneda', 'PEN');
      body.delete('tallas_texto');
      sizes.forEach((size) => body.append('tallas', size));
      if (!body.get('tipo_producto_id')) body.delete('tipo_producto_id');
      if (!body.get('imagen')?.size) body.delete('imagen');
    }
    if (tab === 'variantes') body = { prenda_id: form.get('prenda_id'), sku: form.get('sku'), talla: form.get('talla'), color: form.get('color') };
    try { await current.api.create(body); setMessage({ error: '', success: 'Registro creado correctamente.' }); resource.reload(); garments.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); }
  }
  async function toggle(item) {
    if (tab === 'variantes') {
      try { await current.api.update(item.id, { activa: !item.activa }); resource.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); }
      return;
    }
    const action = ['activa', 'activo'].includes(item.estado || (item.activo ? 'activo' : '')) ? 'desactivar' : 'activar';
    try { await current.api.action(item.id, action); resource.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); }
  }
  async function removeVariant(item) {
    if (!window.confirm(`¿Eliminar la variante ${item.sku}?`)) return;
    try { await api.variants.remove(item.id); resource.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); }
  }
  return <><PageHeader eyebrow="Maestros" title="Catálogo" description="Estructura la colección desde la categoría hasta cada variante." actions={<Button icon="plus" onClick={() => { setMessage({ error: '', success: '' }); setOpen(true); }}>Nuevo registro</Button>}/><div className="tabs" role="tablist">{Object.entries(resources).map(([key, value]) => <button role="tab" aria-selected={tab === key} className={tab === key ? 'is-active' : ''} key={key} onClick={() => setTab(key)}>{value.title}</button>)}</div><SubmitMessage {...message}/><State loading={resource.loading} error={resource.error} empty={!resource.data?.length} onRetry={resource.reload}><div className="card table-wrap"><table><CatalogHead tab={tab}/><tbody>{(resource.data || []).map((item) => <CatalogRow key={item.id} tab={tab} item={item} categories={categories.data || []} garments={garments.data || []} onToggle={toggle} onRemove={removeVariant}/>)}</tbody></table></div></State><Drawer open={open} onClose={() => setOpen(false)} title={`Nueva ${current.title.toLowerCase()}`} description="Completa los datos para incorporarla al catálogo."><form className="drawer-form" onSubmit={submit}>{tab === 'prendas' && <><Field label="Nombre"><input name="nombre" required/></Field><Field label="Descripción"><textarea name="descripcion" rows="3"/></Field><div className="form-row"><Field label="Precio"><input name="precio_monto" type="number" min="0.01" step="0.01" required/></Field><Field label="Tallas" hint="Separadas por coma"><input name="tallas_texto" placeholder="S, M, L"/></Field></div><Field label="Categoría"><select name="categoria_id" required><option value="">Selecciona</option>{(categories.data || []).map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select></Field><Field label="Tipo de producto"><select name="tipo_producto_id"><option value="">Sin tipo</option>{(types.data || []).map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select></Field><Field label="Imagen de la prenda" hint="JPG, PNG o WebP"><input name="imagen" type="file" accept="image/png,image/jpeg,image/webp"/></Field></>}{tab === 'variantes' && <><Field label="Prenda"><select name="prenda_id" required><option value="">Selecciona</option>{(garments.data || []).map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select></Field><Field label="SKU"><input name="sku" required/></Field><div className="form-row"><Field label="Talla"><input name="talla" required/></Field><Field label="Color"><input name="color" required/></Field></div></>}{tab === 'categorias' && <><Field label="Nombre"><input name="nombre" required/></Field><Field label="Descripción"><textarea name="descripcion" rows="4"/></Field></>}{tab === 'tipos' && <Field label="Nombre"><input name="nombre" required/></Field>}<SubmitMessage {...message}/><Button type="submit">Guardar registro</Button></form></Drawer></>;
}

function CatalogHead({ tab }) { return <thead><tr>{tab === 'prendas' && <><th>Prenda</th><th>Categoría</th><th>Precio</th><th>Estado</th><th>Acción</th></>}{tab === 'variantes' && <><th>SKU</th><th>Prenda</th><th>Talla</th><th>Color</th><th>Estado</th><th>Acción</th></>}{tab === 'categorias' && <><th>Nombre</th><th>Descripción</th></>}{tab === 'tipos' && <><th>Nombre</th><th>Atributos</th><th>Estado</th><th>Acción</th></>}</tr></thead>; }
function CatalogRow({ tab, item, categories, garments, onToggle, onRemove }) {
  if (tab === 'prendas') return <tr><td data-label="Prenda"><strong>{item.nombre}</strong><small>{item.descripcion}</small></td><td data-label="Categoría">{item.categoria_nombre || categories.find((value) => value.id === item.categoria_id)?.nombre || 'Sin categoría'}</td><td data-label="Precio">{formatMoney(item.precio_monto, item.precio_moneda)}</td><td data-label="Estado"><Status>{item.estado}</Status></td><td data-label="Acción"><button className="text-button" onClick={() => onToggle(item)}>{item.estado === 'activa' ? 'Desactivar' : 'Activar'}</button></td></tr>;
  if (tab === 'variantes') return <tr><td data-label="SKU"><strong>{item.sku}</strong></td><td data-label="Prenda">{item.prenda_nombre || garments.find((value) => value.id === (item.prenda_id || item.prenda))?.nombre}</td><td data-label="Talla">{item.talla}</td><td data-label="Color">{item.color}</td><td data-label="Estado"><Status>{item.activa ? 'activa' : 'inactiva'}</Status></td><td data-label="Acción"><div className="table-actions"><button className="text-button" onClick={() => onToggle(item)}>{item.activa ? 'Desactivar' : 'Activar'}</button><button className="text-button danger" onClick={() => onRemove(item)}>Eliminar</button></div></td></tr>;
  if (tab === 'categorias') return <tr><td data-label="Nombre"><strong>{item.nombre}</strong></td><td data-label="Descripción">{item.descripcion || 'Sin descripción'}</td></tr>;
  return <tr><td data-label="Nombre"><strong>{item.nombre}</strong></td><td data-label="Atributos">{Object.keys(item.atributos_base || {}).join(', ') || 'Sin atributos'}</td><td data-label="Estado"><Status>{item.activo ? 'activo' : 'inactivo'}</Status></td><td data-label="Acción"><button className="text-button" onClick={() => onToggle(item)}>{item.activo ? 'Desactivar' : 'Activar'}</button></td></tr>;
}

export function UsersPage() {
  const users = useApi((signal) => api.users.list(null, { signal }), []);
  const roles = useApi((signal) => api.roles.list(null, { signal }), []);
  const [drawer, setDrawer] = useState('');
  const [message, setMessage] = useState({ error: '', success: '' });
  async function submit(event) {
    event.preventDefault(); setMessage({ error: '', success: '' }); const form = new FormData(event.currentTarget);
    try {
      if (drawer === 'usuario') await api.users.create(Object.fromEntries(form.entries()));
      else await api.roles.create({ nombre: form.get('nombre'), descripcion: form.get('descripcion') });
      setMessage({ error: '', success: 'Registro creado correctamente.' }); users.reload(); roles.reload();
    } catch (error) { setMessage({ error: error.message, success: '' }); }
  }
  async function toggle(user) { try { await api.users.action(user.id, user.estado === 'activo' ? 'desactivar' : 'activar'); users.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); } }
  return <><PageHeader eyebrow="Accesos" title="Usuarios y roles" description="Administra quién entra y qué responsabilidad ocupa." actions={<><Button icon="plus" onClick={() => setDrawer('usuario')}>Nuevo usuario</Button><Button variant="secondary" onClick={() => setDrawer('rol')}>Nuevo rol</Button></>}/><section className="role-strip">{(roles.data || []).map((role) => <article key={role.id}><span>{role.nombre[0]}</span><div><strong>{role.nombre}</strong><small>{role.descripcion || 'Rol de Zuren'}</small></div></article>)}</section><SubmitMessage {...message}/><State loading={users.loading || roles.loading} error={users.error || roles.error} empty={!users.data?.length} onRetry={users.reload}><div className="card table-wrap"><table><thead><tr><th>Usuario</th><th>Username</th><th>Rol</th><th>Creación</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{(users.data || []).map((user) => <tr key={user.id}><td data-label="Usuario"><strong>{user.nombre}</strong><small>{user.email}</small></td><td data-label="Username">@{user.username}</td><td data-label="Rol">{user.rol_nombre}</td><td data-label="Creación">{formatDate(user.fecha_creacion)}</td><td data-label="Estado"><Status>{user.estado}</Status></td><td data-label="Acción"><button className="text-button" onClick={() => toggle(user)}>{user.estado === 'activo' ? 'Desactivar' : 'Activar'}</button></td></tr>)}</tbody></table></div></State><Drawer open={Boolean(drawer)} onClose={() => setDrawer('')} title={drawer === 'rol' ? 'Nuevo rol' : 'Nuevo usuario'}><form className="drawer-form" onSubmit={submit}>{drawer === 'rol' ? <><Field label="Nombre"><input name="nombre" required/></Field><Field label="Descripción"><textarea name="descripcion" rows="4"/></Field></> : <><Field label="Nombre"><input name="nombre" required/></Field><Field label="Correo"><input name="email" type="email" required/></Field><Field label="Usuario"><input name="username" required/></Field><Field label="Contraseña"><input name="password" type="password" minLength="8" required/></Field><Field label="Rol"><select name="rol_id" required><option value="">Selecciona</option>{(roles.data || []).map((role) => <option value={role.id} key={role.id}>{role.nombre}</option>)}</select></Field></>}<SubmitMessage {...message}/><Button type="submit">Guardar</Button></form></Drawer></>;
}

export function AdminPaymentsPage() {
  const resource = useApi((signal) => api.payments.list({ pagina: 1, tamano: 100 }, { signal }), []);
  const [error, setError] = useState('');
  const payments = resource.data?.resultados || resource.data || [];
  async function process(id, action) { setError(''); try { await api.payments.action(id, action); resource.reload(); } catch (actionError) { setError(actionError.message); } }
  return <><PageHeader eyebrow="Conciliación" title="Validación de pagos" description="Aprueba solo las operaciones comprobadas."/><SubmitMessage error={error}/><State loading={resource.loading} error={resource.error} empty={!payments.length} onRetry={resource.reload}><div className="card table-wrap"><table><thead><tr><th>Operación</th><th>Pedido</th><th>Método</th><th>Monto</th><th>Estado</th><th>Decisión</th></tr></thead><tbody>{payments.map((item) => <tr key={item.id}><td data-label="Operación"><strong>{item.referencia || 'Sin referencia'}</strong><small>{formatDate(item.fecha)}</small></td><td data-label="Pedido">#{item.pedido_id.slice(0, 8)}</td><td data-label="Método">{item.metodo}</td><td data-label="Monto"><strong>{formatMoney(item.monto_monto, item.monto_moneda)}</strong></td><td data-label="Estado"><Status>{item.estado}</Status></td><td data-label="Decisión">{item.estado === 'pendiente' ? <div className="table-actions"><button className="text-button success" onClick={() => process(item.id, 'aprobar')}>Aprobar</button><button className="text-button danger" onClick={() => process(item.id, 'rechazar')}>Rechazar</button></div> : 'Procesado'}</td></tr>)}</tbody></table></div></State></>;
}

export function DispatchesPage() {
  const resource = useApi((signal) => api.dispatches.list(null, { signal }), []);
  const [drawer, setDrawer] = useState(null);
  const [message, setMessage] = useState({ error: '', success: '' });
  async function create(event) { event.preventDefault(); const form = new FormData(event.currentTarget); await act(() => api.dispatches.create({ pedido_id: form.get('pedido_id'), direccion_entrega: form.get('direccion_entrega') })); }
  async function confirm(event) { event.preventDefault(); const form = new FormData(event.currentTarget); await act(() => api.dispatches.action(drawer.item.id, 'confirmar', Object.fromEntries(form.entries()))); }
  async function act(callback) { setMessage({ error: '', success: '' }); try { await callback(); setMessage({ error: '', success: 'Despacho actualizado correctamente.' }); resource.reload(); } catch (error) { setMessage({ error: error.message, success: '' }); } }
  return <><PageHeader eyebrow="Última milla" title="Despachos" description="Programa, prepara y confirma cada entrega." actions={<Button icon="plus" onClick={() => setDrawer({ type: 'programar' })}>Programar</Button>}/><SubmitMessage {...message}/><State loading={resource.loading} error={resource.error} empty={!resource.data?.length} onRetry={resource.reload}><div className="dispatch-grid">{(resource.data || []).map((item) => <article className="card dispatch-card" key={item.id}><header><span className="item-monogram">{item.estado === 'confirmado' ? '✓' : 'ZR'}</span><Status>{item.estado}</Status></header><p className="eyebrow">Pedido #{item.pedido_id.slice(0, 8)}</p><h2>{item.direccion_entrega}</h2>{item.guia && <p>Guía {item.guia.serie}-{item.guia.numero} · {item.guia.transportista}</p>}<footer>{item.estado === 'pendiente' && <Button onClick={() => act(() => api.dispatches.action(item.id, 'preparar', {}))}>Preparar</Button>}{item.estado === 'preparado' && <Button onClick={() => setDrawer({ type: 'confirmar', item })}>Confirmar entrega</Button>}{!['confirmado', 'cancelado'].includes(item.estado) && <button className="text-button danger" onClick={() => act(() => api.dispatches.action(item.id, 'cancelar'))}>Cancelar</button>}</footer></article>)}</div></State><Drawer open={Boolean(drawer)} onClose={() => setDrawer(null)} title={drawer?.type === 'confirmar' ? 'Confirmar despacho' : 'Programar despacho'}>{drawer?.type === 'confirmar' ? <form className="drawer-form" onSubmit={confirm}><Field label="Serie de guía"><input name="serie" required maxLength="10"/></Field><Field label="Número"><input name="numero" required maxLength="20"/></Field><Field label="Transportista"><input name="transportista"/></Field><SubmitMessage {...message}/><Button type="submit">Emitir y confirmar</Button></form> : <form className="drawer-form" onSubmit={create}><Field label="ID del pedido"><input name="pedido_id" required/></Field><Field label="Dirección de entrega"><textarea name="direccion_entrega" rows="4" required/></Field><SubmitMessage {...message}/><Button type="submit">Programar despacho</Button></form>}</Drawer></>;
}
