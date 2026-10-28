import { useState } from 'react';

import {
  Button,
  Drawer,
  Field,
  PageHeader,
  State,
  Status,
  SubmitMessage,
} from '../components/ui';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

export function DispatchesPage() {
  const resource = useApi((signal) => api.dispatches.list(null, { signal }), []);
  const orders = useApi((signal) => api.orders.list(null, { signal }), []);
  const [drawer, setDrawer] = useState(null);
  const [message, setMessage] = useState({ error: '', success: '' });
  const paidOrders = (orders.data || []).filter((item) => item.estado === 'pagado');

  async function act(callback) {
    setMessage({ error: '', success: '' });
    try {
      await callback();
      setMessage({ error: '', success: 'Despacho actualizado correctamente.' });
      resource.reload();
      orders.reload();
      setDrawer(null);
    } catch (error) {
      setMessage({ error: error.message, success: '' });
    }
  }

  async function create(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await act(() => api.dispatches.create({
      pedido_id: form.get('pedido_id'),
      direccion_entrega: form.get('direccion_entrega'),
    }));
  }

  async function confirm(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await act(() => api.dispatches.action(
      drawer.item.id,
      'confirmar',
      Object.fromEntries(form.entries()),
    ));
  }

  return (
    <>
      <PageHeader
        eyebrow="Última milla"
        title="Despachos"
        description="Programa pedidos pagados, prepara la salida y emite su guía."
        actions={<Button icon="plus" onClick={() => setDrawer({ type: 'programar' })}>Programar</Button>}
      />
      <SubmitMessage {...message} />
      <State
        loading={resource.loading || orders.loading}
        error={resource.error || orders.error}
        empty={!resource.data?.length}
        onRetry={resource.reload}
      >
        <div className="dispatch-grid">
          {(resource.data || []).map((item) => (
            <article className="card dispatch-card" key={item.id}>
              <header>
                <span className="item-monogram">{item.estado === 'confirmado' ? 'OK' : 'ZR'}</span>
                <Status>{item.estado}</Status>
              </header>
              <p className="eyebrow">Pedido #{item.pedido_id.slice(0, 8)}</p>
              <h2>{item.direccion_entrega}</h2>
              {item.guia && <p>Guía {item.guia.serie}-{item.guia.numero} · {item.guia.transportista}</p>}
              <footer>
                {item.estado === 'pendiente' && (
                  <Button onClick={() => act(() => api.dispatches.action(item.id, 'preparar', {}))}>
                    Preparar
                  </Button>
                )}
                {item.estado === 'preparado' && (
                  <Button onClick={() => setDrawer({ type: 'confirmar', item })}>
                    Confirmar entrega
                  </Button>
                )}
                {!['confirmado', 'cancelado'].includes(item.estado) && (
                  <button
                    className="text-button danger"
                    onClick={() => act(() => api.dispatches.action(item.id, 'cancelar'))}
                  >
                    Cancelar
                  </button>
                )}
              </footer>
            </article>
          ))}
        </div>
      </State>
      <Drawer
        open={Boolean(drawer)}
        onClose={() => setDrawer(null)}
        title={drawer?.type === 'confirmar' ? 'Confirmar despacho' : 'Programar despacho'}
      >
        {drawer?.type === 'confirmar' ? (
          <form className="drawer-form" onSubmit={confirm}>
            <Field label="Serie de guía"><input name="serie" required maxLength="10" /></Field>
            <Field label="Número"><input name="numero" required maxLength="20" inputMode="numeric" /></Field>
            <Field label="Transportista"><input name="transportista" /></Field>
            <SubmitMessage {...message} />
            <Button type="submit">Emitir y confirmar</Button>
          </form>
        ) : (
          <form className="drawer-form" onSubmit={create}>
            <Field label="Pedido pagado">
              <select name="pedido_id" required>
                <option value="">Selecciona un pedido</option>
                {paidOrders.map((order) => (
                  <option key={order.id} value={order.id}>
                    #{order.id.slice(0, 8)} · {order.total_moneda} {order.total_monto}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Dirección de entrega">
              <textarea name="direccion_entrega" rows="4" required />
            </Field>
            {!paidOrders.length && <p className="inline-message">No hay pedidos pagados pendientes.</p>}
            <SubmitMessage {...message} />
            <Button type="submit" disabled={!paidOrders.length}>Programar despacho</Button>
          </form>
        )}
      </Drawer>
    </>
  );
}
