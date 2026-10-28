const API_BASE = typeof import.meta !== 'undefined' && import.meta.env
  ? import.meta.env.VITE_API_BASE_URL ?? ''
  : '';

export const SESSION_KEY = 'zuren_session';

function sessionToken() {
  if (typeof window === 'undefined') return '';
  try {
    return JSON.parse(window.localStorage.getItem(SESSION_KEY) || 'null')?.token || '';
  } catch {
    return '';
  }
}

export function apiUrl(path, query, baseUrl = API_BASE) {
  const origin = baseUrl || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost');
  const url = new URL(path, origin);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) url.searchParams.set(key, value);
  });
  return url;
}

function errorMessage(payload, fallback) {
  if (typeof payload === 'string' && payload.trim()) return payload.trim();
  if (!payload || typeof payload !== 'object') return fallback;
  if (typeof payload.error === 'string') return payload.error;
  if (Array.isArray(payload.error)) return payload.error.join(' ');
  if (typeof payload.detail === 'string') return payload.detail;
  if (typeof payload.detalle === 'string') return payload.detalle;
  const details = payload.detalle && typeof payload.detalle === 'object' ? payload.detalle : payload;
  const first = Object.entries(details).find(([, value]) => value !== undefined);
  if (!first) return fallback;
  const value = Array.isArray(first[1]) ? first[1].join(' ') : String(first[1]);
  return `${first[0]}: ${value}`;
}

export async function request(path, { method = 'GET', body, query, signal, auth = true, baseUrl } = {}) {
  const headers = { Accept: 'application/json' };
  const token = auth ? sessionToken() : '';
  if (token) headers.Authorization = `Bearer ${token}`;
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData;
  if (body !== undefined && !isForm) headers['Content-Type'] = 'application/json';

  const response = await fetch(apiUrl(path, query, baseUrl), {
    method,
    headers,
    body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    signal,
  });
  const contentType = response.headers.get('content-type') || '';
  const payload = response.status === 204
    ? null
    : contentType.includes('json')
      ? await response.json().catch(() => null)
      : await response.text().catch(() => '');
  if (!response.ok) {
    if (response.status === 401 && auth && typeof window !== 'undefined') {
      window.localStorage.removeItem(SESSION_KEY);
      window.dispatchEvent(new CustomEvent('zuren:session-expired'));
    }
    const error = new Error(errorMessage(payload, `La solicitud falló (${response.status})`));
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function filenameFrom(response, fallback) {
  const disposition = response.headers.get('content-disposition') || '';
  return disposition.match(/filename\*?=(?:UTF-8''|")?([^";]+)/i)?.[1] || fallback;
}

export async function download(path, { query, filename = 'descarga', baseUrl } = {}) {
  const headers = {};
  const token = sessionToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(apiUrl(path, query, baseUrl), { headers });
  if (!response.ok) {
    let payload;
    try { payload = await response.clone().json(); } catch { payload = await response.text(); }
    const error = new Error(errorMessage(payload, `No se pudo descargar el archivo (${response.status})`));
    error.status = response.status;
    throw error;
  }
  const blob = await response.blob();
  if (typeof document !== 'undefined') {
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = href;
    anchor.download = decodeURIComponent(filenameFrom(response, filename));
    anchor.click();
    URL.revokeObjectURL(href);
  }
  return { blob, filename: filenameFrom(response, filename) };
}

const endpoint = (path) => ({
  list: (query, options = {}) => request(path, { ...options, query }),
  get: (id, options = {}) => request(`${path}${id}/`, options),
  create: (body) => request(path, { method: 'POST', body }),
  update: (id, body) => request(`${path}${id}/`, { method: 'PATCH', body }),
  remove: (id) => request(`${path}${id}/`, { method: 'DELETE' }),
  action: (id, action, body) => request(`${path}${id}/${action}/`, { method: 'POST', body }),
});

export const api = {
  auth: {
    login: (body) => request('/api/auth/login/', { method: 'POST', body, auth: false }),
    register: (body) => request('/api/auth/registro/', { method: 'POST', body, auth: false }),
    logout: () => request('/api/auth/logout/', { method: 'POST' }),
    profile: () => request('/api/auth/perfil/'),
    updateProfile: (body) => request('/api/auth/perfil/', { method: 'PATCH', body }),
    changePassword: (body) => request('/api/auth/cambiar-password/', { method: 'POST', body }),
    closeSessions: () => request('/api/auth/cerrar-otras-sesiones/', { method: 'POST' }),
  },
  garments: endpoint('/api/prendas/'),
  variants: endpoint('/api/variantes/'),
  categories: endpoint('/api/categorias/'),
  types: endpoint('/api/tipos-producto/'),
  users: endpoint('/api/usuarios/'),
  roles: endpoint('/api/roles/'),
  carts: {
    ...endpoint('/api/ventas/carritos/'),
    add: (id, variante_id, cantidad) => request(`/api/ventas/carritos/${id}/items/`, { method: 'POST', body: { variante_id, cantidad } }),
    remove: (id, variante_id) => request(`/api/ventas/carritos/${id}/items/`, { method: 'DELETE', body: { variante_id } }),
  },
  orders: endpoint('/api/ventas/pedidos/'),
  payments: endpoint('/api/ventas/pagos/'),
  dispatches: endpoint('/api/ventas/despachos/'),
  stock: {
    list: (options = {}) => request('/api/stock/', options),
    get: (id, options = {}) => request(`/api/stock/${id}/`, options),
    grouped: (categoria_id, options = {}) => request('/api/stock/por-categoria/', { ...options, query: { categoria_id } }),
    low: (options = {}) => request('/api/stock/bajo-minimo/', options),
    create: (body) => request('/api/stock/', { method: 'POST', body }),
    move: (kind, body) => request(`/api/stock/${kind}/`, { method: 'POST', body }),
    report: (formato, categoria_id) => download('/api/stock/reporte/', { query: { formato, categoria_id }, filename: `inventario.${formato}` }),
  },
  movements: (stock_id, options = {}) => request('/api/movimientos/', { ...options, query: { stock_id } }),
};
