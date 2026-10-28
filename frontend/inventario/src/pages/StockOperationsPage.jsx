import { useState } from 'react';

import {
  Button,
  Drawer,
  Field,
  PageHeader,
  State,
  Status,
  SubmitMessage,
  formatDate,
} from '../components/ui';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

export function StockOperationsPage() {
  const stock = useApi((signal) => api.stock.list({ signal }), []);
  const variants = useApi((signal) => api.variants.list(null, { signal }), []);
  const [selected, setSelected] = useState('');
  const movements = useApi(
    (signal) => (selected ? api.movements(selected, { signal }) : Promise.resolve([])),
    [selected],
  );
  const [drawer, setDrawer] = useState('');
  const [message, setMessage] = useState({ error: '', success: '' });
  const variantMap = new Map((variants.data || []).map((item) => [item.id, item]));
  const variantsWithStock = new Set((stock.data || []).map((item) => item.variante_id));

  async function submit(event) {
    event.preventDefault();
    setMessage({ error: '', success: '' });
    const form = new FormData(event.currentTarget);
    try {
      if (drawer === 'inicializar') {
        await api.stock.create({
          variante_id: form.get('variante_id'),
          stock_inicial: Number(form.get('cantidad')),
          stock_minimo: Number(form.get('stock_minimo')),
          ubicacion: form.get('ubicacion'),
        });
      } else {
        const body = {
          variante_id: form.get('variante_id'),
          motivo: form.get('motivo'),
        };
        if (drawer === 'ajustes') body.nueva_cantidad = Number(form.get('cantidad'));
        else body.cantidad = Number(form.get('cantidad'));
        await api.stock.move(drawer, body);
      }
      setMessage({ error: '', success: 'Inventario actualizado correctamente.' });
      stock.reload();
      movements.reload();
    } catch (error) {
      setMessage({ error: error.message, success: '' });
    }
  }

  const isInitial = drawer === 'inicializar';
  return (
    <>
      <PageHeader
        eyebrow="Trazabilidad"
        title="Movimientos"
        description="Inicializa existencias y registra cada cambio de almacén."
        actions={(
          <>
            <Button icon="plus" onClick={() => setDrawer('ingresos')}>Ingreso</Button>
            <Button variant="secondary" onClick={() => setDrawer('salidas')}>Salida</Button>
            <Button variant="secondary" onClick={() => setDrawer('ajustes')}>Ajuste</Button>
            <Button variant="secondary" onClick={() => setDrawer('inicializar')}>Nuevo stock</Button>
          </>
        )}
      />
      <section className="filter-bar">
        <Field label="Stock a consultar">
          <select value={selected} onChange={(event) => setSelected(event.target.value)}>
            <option value="">Selecciona una ubicación</option>
            {(stock.data || []).map((item) => {
              const variant = variantMap.get(item.variante_id);
              return (
                <option key={item.id} value={item.id}>
                  {variant ? `${variant.sku} · ` : ''}{item.ubicacion} · {item.cantidad_actual} unidades
                </option>
              );
            })}
          </select>
        </Field>
      </section>
      <State
        loading={stock.loading || movements.loading}
        error={stock.error || variants.error || movements.error}
        empty={!movements.data?.length}
        onRetry={movements.reload}
      >
        <div className="card table-wrap">
          <table>
            <thead><tr><th>Fecha</th><th>Tipo</th><th>Cantidad</th><th>Motivo</th><th>Responsable</th></tr></thead>
            <tbody>
              {(movements.data || []).map((item) => (
                <tr key={item.id}>
                  <td data-label="Fecha">{formatDate(item.fecha)}</td>
                  <td data-label="Tipo"><Status>{item.tipo}</Status></td>
                  <td data-label="Cantidad"><strong>{item.tipo === 'salida' ? '-' : '+'}{item.cantidad}</strong></td>
                  <td data-label="Motivo">{item.motivo}</td>
                  <td data-label="Responsable">{item.registrado_por.slice(0, 8)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </State>
      <Drawer
        open={Boolean(drawer)}
        onClose={() => setDrawer('')}
        title={isInitial ? 'Inicializar stock' : drawer === 'ajustes' ? 'Nuevo ajuste' : drawer === 'salidas' ? 'Registrar salida' : 'Registrar ingreso'}
        description="La sesión actual quedará registrada como responsable."
      >
        <form className="drawer-form" onSubmit={submit}>
          <Field label="Variante">
            <select name="variante_id" required>
              <option value="">Selecciona una variante</option>
              {(variants.data || [])
                .filter((item) => (isInitial ? !variantsWithStock.has(item.id) : variantsWithStock.has(item.id)))
                .map((item) => <option key={item.id} value={item.id}>{item.sku} · {item.talla} · {item.color}</option>)}
            </select>
          </Field>
          <Field label={isInitial ? 'Stock inicial' : drawer === 'ajustes' ? 'Nueva cantidad' : 'Cantidad'}>
            <input name="cantidad" type="number" min={isInitial || drawer === 'ajustes' ? '0' : '1'} required />
          </Field>
          {isInitial ? (
            <>
              <Field label="Stock mínimo"><input name="stock_minimo" type="number" min="0" required /></Field>
              <Field label="Ubicación"><input name="ubicacion" defaultValue="almacen" required /></Field>
            </>
          ) : (
            <Field label="Motivo"><textarea name="motivo" rows="4" required /></Field>
          )}
          <SubmitMessage {...message} />
          <Button type="submit">Guardar operación</Button>
        </form>
      </Drawer>
    </>
  );
}
