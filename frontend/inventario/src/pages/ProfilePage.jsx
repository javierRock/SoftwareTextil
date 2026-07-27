import { useState } from 'react';

import { useAuth } from '../auth/AuthContext';
import { Button, Field, PageHeader, SubmitMessage, formatDate } from '../components/ui';
import { api } from '../services/api';

export function ProfilePage() {
  const { profile, updateProfile } = useAuth();
  const [profileMessage, setProfileMessage] = useState({ error: '', success: '' });
  const [passwordMessage, setPasswordMessage] = useState({ error: '', success: '' });
  async function saveProfile(event) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    try { await updateProfile({ nombre: form.get('nombre'), email: form.get('email') }); setProfileMessage({ error: '', success: 'Datos personales actualizados.' }); } catch (error) { setProfileMessage({ error: error.message, success: '' }); }
  }
  async function changePassword(event) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    try { await api.auth.changePassword({ password_actual: form.get('password_actual'), password_nuevo: form.get('password_nuevo') }); event.currentTarget.reset(); setPasswordMessage({ error: '', success: 'Contraseña actualizada.' }); } catch (error) { setPasswordMessage({ error: error.message, success: '' }); }
  }
  return <><PageHeader eyebrow="Cuenta" title="Mi perfil" description="Mantén tus datos y sesiones bajo control."/><div className="profile-layout"><aside className="card profile-card"><span className="profile-avatar">{profile?.nombre?.[0] || 'Z'}</span><h2>{profile?.nombre}</h2><p>{profile?.email}</p><span className="status status--activo">{profile?.rol_nombre}</span><dl><div><dt>Usuario</dt><dd>@{profile?.username || 'usuario'}</dd></div><div><dt>Miembro desde</dt><dd>{formatDate(profile?.fecha_creacion)}</dd></div></dl></aside><div className="profile-forms"><section className="card form-card"><p className="eyebrow">Información personal</p><h2>Datos de contacto</h2><form onSubmit={saveProfile}><Field label="Nombre"><input name="nombre" defaultValue={profile?.nombre} required/></Field><Field label="Correo"><input name="email" type="email" defaultValue={profile?.email} required/></Field><SubmitMessage {...profileMessage}/><Button type="submit">Guardar cambios</Button></form></section><section className="card form-card"><p className="eyebrow">Seguridad</p><h2>Cambiar contraseña</h2><form onSubmit={changePassword}><Field label="Contraseña actual"><input name="password_actual" type="password" required/></Field><Field label="Nueva contraseña"><input name="password_nuevo" type="password" minLength="8" required/></Field><SubmitMessage {...passwordMessage}/><Button type="submit" variant="secondary">Actualizar contraseña</Button></form><button className="text-button" onClick={() => api.auth.closeSessions().then(() => setPasswordMessage({ error: '', success: 'Las otras sesiones fueron cerradas.' })).catch((error) => setPasswordMessage({ error: error.message, success: '' }))}>Cerrar las demás sesiones</button></section></div></div></>;
}
