import assert from 'node:assert/strict';
import test from 'node:test';

import { buildInventoryUrl, fetchGroupedStockByCategory } from './inventoryApi.js';

test('buildInventoryUrl arma la ruta del endpoint', () => {
  const url = buildInventoryUrl('categoria-1', 'http://localhost:8000');

  assert.equal(url.toString(), 'http://localhost:8000/api/stock/por-categoria/?categoria_id=categoria-1');
});

test('fetchGroupedStockByCategory devuelve los datos del backend', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () =>
    new Response(JSON.stringify([{ categoria_id: '1', categoria: 'Camisas', cantidad_total: 2, prendas: [] }]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  try {
    const data = await fetchGroupedStockByCategory({ baseUrl: 'http://localhost:8000' });
    assert.deepEqual(data, [{ categoria_id: '1', categoria: 'Camisas', cantidad_total: 2, prendas: [] }]);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
