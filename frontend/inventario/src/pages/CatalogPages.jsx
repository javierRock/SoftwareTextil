import { useDeferredValue, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { PublicHeader } from '../components/PublicHeader';
import { Button, Field, Icon, State, formatMoney } from '../components/ui';
import { useApi } from '../hooks/useApi';
import { api } from '../services/api';

const placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 700"%3E%3Crect width="600" height="700" fill="%23e4e9e6"/%3E%3Cpath d="M190 180l110 55 110-55 90 75-60 110-55-30v220H215V335l-55 30-60-110 90-75z" fill="%23c5cec9"/%3E%3C/svg%3E';

function imageOf(item) { return item.imagen || item.imagen_url || placeholder; }
function variantsOf(item) { return item.variantes || []; }

export function CatalogPage() {
  const garments = useApi((signal) => api.garments.list({ estado: 'activa' }, { signal }), []);
  const categories = useApi((signal) => api.categories.list(null, { signal }), []);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const deferredSearch = useDeferredValue(search.toLowerCase());
  const items = (garments.data || []).filter((item) => (!category || (item.categoria_id || item.categoria) === category) && (!deferredSearch || `${item.nombre} ${item.descripcion}`.toLowerCase().includes(deferredSearch)));
  return <div className="public-page"><PublicHeader/><section className="catalog-hero"><div><p className="eyebrow">Colección 2026</p><h1>Forma, oficio<br/><em>y materia.</em></h1></div><p>Prendas esenciales hechas para acompañar el movimiento cotidiano, en colores que permanecen.</p></section><section className="catalog-tools"><div className="search-box"><Icon name="search"/><input aria-label="Buscar prendas" placeholder="Buscar en la colección" value={search} onChange={(event) => setSearch(event.target.value)}/></div><select aria-label="Filtrar por categoría" value={category} onChange={(event) => setCategory(event.target.value)}><option value="">Todas las categorías</option>{(categories.data || []).map((item) => <option value={item.id} key={item.id}>{item.nombre}</option>)}</select><span>{items.length} piezas</span></section><main className="catalog-content"><State loading={garments.loading} error={garments.error} empty={!items.length} onRetry={garments.reload}><div className="product-grid">{items.map((item, index) => <Link className="product-card" to={`/catalogo/${item.id}`} key={item.id}><div className="product-image"><img src={imageOf(item)} alt=""/><span>0{index + 1}</span></div><div><p>{categories.data?.find((value) => value.id === item.categoria_id)?.nombre || 'Colección Zuren'}</p><h2>{item.nombre}</h2><strong>{formatMoney(item.precio_monto, item.precio_moneda)}</strong></div></Link>)}</div></State></main><footer className="public-footer"><strong>ZUREN</strong><span>Hecho con criterio en Perú.</span></footer></div>;
}

export function ProductPage() {
  const { id } = useParams();
  const { session } = useAuth();
  const navigate = useNavigate();
  const garment = useApi((signal) => api.garments.get(id, { signal }), [id]);
  const fallbackVariants = useApi((signal) => api.variants.list({ prenda_id: id }, { signal }), [id]);
  const [variantId, setVariantId] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState('');
  const [adding, setAdding] = useState(false);
  const item = garment.data;
  const variants = item ? variantsOf(item).length ? variantsOf(item) : fallbackVariants.data || [] : [];
  const selectedVariant = variants.find((variant) => variant.id === variantId);

  async function add() {
    if (!session) return navigate('/login', { state: { from: `/catalogo/${id}` } });
    if (!variantId) return setMessage('Selecciona talla y color antes de continuar.');
    setAdding(true); setMessage('');
    try {
      const carts = await api.carts.list();
      let cart = (Array.isArray(carts) ? carts : carts?.resultados || []).find((candidate) => candidate.estado === 'abierto');
      if (!cart) cart = await api.carts.create({});
      await api.carts.add(cart.id, variantId, quantity);
      setMessage('Añadido al carrito. Ya puedes revisar tu selección.');
    } catch (error) { setMessage(error.message); } finally { setAdding(false); }
  }

  return <div className="public-page"><PublicHeader/><main className="product-detail"><State loading={garment.loading} error={garment.error} onRetry={garment.reload}>{item && <><div className="detail-image"><Link to="/catalogo">← Volver a la colección</Link><img src={imageOf(item)} alt={item.nombre}/></div><section className="detail-copy"><p className="eyebrow">Zuren esencial</p><h1>{item.nombre}</h1><strong className="detail-price">{formatMoney(selectedVariant?.precio_efectivo || item.precio_monto, selectedVariant?.moneda || item.precio_moneda)}</strong><p className="detail-description">{item.descripcion || 'Una pieza versátil de nuestra colección permanente.'}</p><div className="detail-rule"/><Field label="Variante"><select value={variantId} onChange={(event) => setVariantId(event.target.value)}><option value="">Selecciona talla y color</option>{variants.map((variant) => <option key={variant.id} value={variant.id} disabled={variant.stock_disponible === 0}>{variant.talla || 'Única'} · {variant.color || 'Natural'} {variant.sku ? `· ${variant.sku}` : ''}{variant.stock_disponible === 0 ? ' · Agotada' : ''}</option>)}</select></Field><Field label="Cantidad"><div className="quantity"><button onClick={() => setQuantity(Math.max(1, quantity - 1))} aria-label="Reducir cantidad">−</button><output>{quantity}</output><button onClick={() => setQuantity(Math.min(selectedVariant?.stock_disponible ?? quantity + 1, quantity + 1))} aria-label="Aumentar cantidad">+</button></div></Field>{message && <p className="inline-message" role="status">{message}</p>}<Button onClick={add} disabled={adding || selectedVariant?.stock_disponible === 0}>{adding ? 'Añadiendo…' : 'Añadir al carrito'}</Button><ul className="product-notes"><li>Despacho coordinado</li><li>Cambios simples</li><li>Stock actualizado</li></ul></section></>}</State></main></div>;
}
