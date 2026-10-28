import { createContext, useContext, useEffect, useState } from 'react';

import { api, SESSION_KEY } from '../services/api';

const AuthContext = createContext(null);

function storedSession() {
  try { return JSON.parse(window.localStorage.getItem(SESSION_KEY) || 'null'); } catch { return null; }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(storedSession);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(Boolean(session?.token));

  useEffect(() => {
    if (!session?.token) return;
    api.auth.profile()
      .then(setProfile)
      .catch(() => {
        window.localStorage.removeItem(SESSION_KEY);
        setSession(null);
      })
      .finally(() => setLoading(false));
  }, [session?.token]);

  useEffect(() => {
    function clearExpiredSession() {
      setSession(null);
      setProfile(null);
      setLoading(false);
    }
    window.addEventListener('zuren:session-expired', clearExpiredSession);
    return () => window.removeEventListener('zuren:session-expired', clearExpiredSession);
  }, []);

  async function login(credentials) {
    const next = await api.auth.login(credentials);
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(next));
    setSession(next);
    setProfile({
      id: next.usuario_id,
      nombre: next.nombre,
      email: next.email,
      rol_nombre: next.rol,
    });
    return next;
  }

  async function register(data) {
    await api.auth.register(data);
    return login({ username: data.username, password: data.password });
  }

  async function logout() {
    try { await api.auth.logout(); } finally {
      window.localStorage.removeItem(SESSION_KEY);
      setSession(null);
      setProfile(null);
    }
  }

  async function updateProfile(data) {
    const next = await api.auth.updateProfile(data);
    setProfile(next);
    return next;
  }

  const role = (profile?.rol_nombre || session?.rol || '').toLocaleLowerCase('es');
  return (
    <AuthContext.Provider value={{ session, profile, role, loading, login, register, logout, updateProfile, refreshProfile: () => api.auth.profile().then(setProfile) }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return context;
}
