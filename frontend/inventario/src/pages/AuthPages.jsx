import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { Button, Field, SubmitMessage } from '../components/ui';

function AuthFrame({ mode }) {
  const isLogin = mode === 'login';
  const { session, role, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  if (session) return <Navigate to={role === 'cliente' ? '/catalogo' : '/panel'} replace/>;

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    const form = new FormData(event.currentTarget);
    const data = Object.fromEntries(form.entries());
    try {
      const result = isLogin ? await login(data) : await register(data);
      const destination = location.state?.from || (result.rol?.toLowerCase() === 'cliente' ? '/catalogo' : '/panel');
      navigate(destination, { replace: true });
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return <div className="auth-page">
    <section className="auth-story" aria-label="Presentación de Zuren"><Link className="wordmark wordmark--light" to="/catalogo"><span>Z</span>ZUREN</Link><div><p className="eyebrow">Diseñado para durar</p><h1>Textiles honestos.<br/>Control preciso.</h1><p>Una experiencia integrada desde la primera prenda hasta el último despacho.</p></div><small>© 2026 Zuren · Lima, Perú</small></section>
    <main className="auth-main"><div className="auth-card"><p className="eyebrow">{isLogin ? 'Bienvenido de vuelta' : 'Únete a Zuren'}</p><h2>{isLogin ? 'Inicia sesión' : 'Crea tu cuenta'}</h2><p>{isLogin ? 'Accede a tu espacio de compra u operaciones.' : 'Compra la colección y sigue cada pedido.'}</p><form onSubmit={submit}>
      {!isLogin && <><Field label="Nombre completo"><input name="nombre" autoComplete="name" required/></Field><Field label="Correo electrónico"><input name="email" type="email" autoComplete="email" required/></Field></>}
      <Field label="Usuario"><input name="username" autoComplete="username" required/></Field>
      <Field label="Contraseña" hint={!isLogin ? 'Usa al menos 8 caracteres.' : ''}><input name="password" type="password" minLength={isLogin ? undefined : 8} autoComplete={isLogin ? 'current-password' : 'new-password'} required/></Field>
      <SubmitMessage error={error}/><Button type="submit" disabled={submitting}>{submitting ? 'Procesando…' : isLogin ? 'Ingresar' : 'Crear cuenta'}</Button>
    </form><p className="auth-switch">{isLogin ? '¿Primera vez en Zuren?' : '¿Ya tienes una cuenta?'} <Link to={isLogin ? '/registro' : '/login'}>{isLogin ? 'Crear cuenta' : 'Iniciar sesión'}</Link></p></div></main>
  </div>;
}

export function LoginPage() { return <AuthFrame mode="login"/>; }
export function RegisterPage() { return <AuthFrame mode="register"/>; }
