import assert from 'node:assert/strict';
import test from 'node:test';

import { apiUrl, download, request } from './api.js';

test('apiUrl conserva ruta y omite filtros vacíos', () => {
  const url = apiUrl('/api/stock/por-categoria/', { categoria_id: 'cat-1', texto: '' }, 'http://localhost:8000');
  assert.equal(url.toString(), 'http://localhost:8000/api/stock/por-categoria/?categoria_id=cat-1');
});

test('request serializa JSON y devuelve la respuesta', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async (url, options) => {
    assert.equal(url.toString(), 'http://localhost:8000/api/prendas/');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers['Content-Type'], 'application/json');
    assert.equal(options.body, '{"nombre":"Lino"}');
    return new Response('{"id":"1"}', { status: 201, headers: { 'content-type': 'application/json' } });
  };
  assert.deepEqual(await request('/api/prendas/', { method: 'POST', body: { nombre: 'Lino' }, baseUrl: 'http://localhost:8000' }), { id: '1' });
});

test('request normaliza errores de validación', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async () => new Response('{"detalle":{"monto":["Valor inválido"]}}', { status: 400, headers: { 'content-type': 'application/json' } });
  await assert.rejects(
    request('/api/pagos/', { baseUrl: 'http://localhost:8000' }),
    (error) => error.status === 400 && error.message === 'monto: Valor inválido',
  );
});

test('download devuelve blob y nombre de Content-Disposition', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => { globalThis.fetch = originalFetch; });
  globalThis.fetch = async () => new Response('archivo', {
    headers: { 'content-disposition': 'attachment; filename="reporte.xlsx"' },
  });
  const result = await download('/api/stock/reporte/', { baseUrl: 'http://localhost:8000' });
  assert.equal(result.filename, 'reporte.xlsx');
  assert.equal(await result.blob.text(), 'archivo');
});
