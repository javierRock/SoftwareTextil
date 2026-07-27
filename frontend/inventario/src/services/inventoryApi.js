const DEFAULT_API_BASE_URL = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env.VITE_API_BASE_URL ?? '' : '';

export function buildInventoryUrl(categoryId = '', baseUrl = DEFAULT_API_BASE_URL) {
  const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost';
  const resolvedBase = baseUrl || origin;
  const url = new URL('/api/stock/por-categoria/', resolvedBase);

  if (categoryId) {
    url.searchParams.set('categoria_id', categoryId);
  }

  return url;
}

async function parseErrorResponse(response) {
  const fallbackMessage = `Error HTTP ${response.status}`;
  const cloned = response.clone();

  try {
    const payload = await cloned.json();
    if (typeof payload?.error === 'string' && payload.error.trim()) {
      return new Error(payload.error);
    }
    if (typeof payload?.detail === 'string' && payload.detail.trim()) {
      return new Error(payload.detail);
    }
  } catch {
    const text = await cloned.text().catch(() => '');
    if (text.trim()) {
      return new Error(text.trim());
    }
  }

  return new Error(fallbackMessage);
}

export async function fetchGroupedStockByCategory({ categoryId = '', signal, baseUrl } = {}) {
  const response = await fetch(buildInventoryUrl(categoryId, baseUrl), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
    signal,
  });

  if (!response.ok) {
    const error = await parseErrorResponse(response);
    error.status = response.status;
    throw error;
  }

  const payload = await response.json();
  if (!Array.isArray(payload)) {
    throw new Error('La respuesta del inventario no tiene el formato esperado');
  }

  return payload;
}
