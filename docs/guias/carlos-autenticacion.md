# Guía de Trabajo — Carlos · Autenticación y Roles

- **Integrante:** Gutierrez Castilla, Carlos Enrique
- **Rama:** `feature/autenticacion-carlos`
- **Módulo:** `apps/usuarios` (autenticación, usuarios, roles, sesiones)

## 1. Alcance y archivos del módulo

| Capa | Archivos |
| --- | --- |
| Dominio | `apps/usuarios/domain/usuario.py`, `apps/usuarios/domain/repositorios.py` |
| Aplicación | `apps/usuarios/application/services.py` |
| Infraestructura | `apps/usuarios/models.py`, `apps/usuarios/infrastructure/models.py`, `apps/usuarios/infrastructure/repositories.py` |
| Presentación | `apps/usuarios/presentation/serializers.py`, `views.py`, `urls.py` |
| Config compartida | `config/settings/base.py` (bloque `REST_FRAMEWORK` — coordinar con el equipo antes de tocarlo) |

## 2. Estilos de programación aplicados

| Estilo | Aplicación | Evidencia |
| --- | --- | --- |
| Things | Entidades del dominio con estado y comportamiento | `Sesion.cerrar()`, `Sesion.esta_activa()`, `Usuario.desactivar()` |
| Restful | API DRF por recursos y acciones HTTP | `/api/usuarios/`, `/api/roles/`, `/api/auth/login/`, `/api/auth/logout/` |
| Persistent-Tables | Tablas separadas para usuarios, roles, sesiones e intentos | `UsuarioModel`, `RolModel`, `SesionModel`, `IntentoLoginModel` |
| Error/Exception Handling | Excepciones propias para errores del caso de uso | `CredencialesInvalidas`, `UsuarioInactivo`, `RecursoDuplicado` |

## 3. Objetivos de refactor con SOLID (evidencia 3+)

Problemas reales detectados en el código actual; cada uno resuelto es evidencia directa de un principio:

| # | Problema actual | Refactor | Principio |
| --- | --- | --- | --- |
| 1 | `ServicioAutenticacion.__init__` recibía `DjangoRepositorioUsuario` como type hint | Se tipó contra `RepositorioUsuario`, `RepositorioSesion`, `RepositorioIntentoLogin` | **DIP** |
| 2 | Repositorios concretos no implementaban contratos ABC | Ahora heredan de `RepositorioUsuario`, `RepositorioRol`, `RepositorioSesion`, `RepositorioIntentoLogin` | **LSP** |
| 3 | Registro de usuario mezclaba servicio de aplicación con import directo del ORM | El `username` entra por la fábrica y se persiste vía repositorio | **SRP** |
| 4 | El login emitía token propio sin autenticador DRF | Se agregó `SesionTokenAuthentication` y permisos `EsAdministrador`, `EsCliente` | **OCP** |

## 4. Prácticas de Clean Code (evidencia 5+)

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo) | Servicios y dominio | `apps/usuarios/application/services.py:34`, `apps/usuarios/domain/usuario.py:40` |
| 2 | Funciones pequeñas, una sola responsabilidad | Login, logout, registro de intento y creación de usuario | `apps/usuarios/application/services.py:45`, `apps/usuarios/application/services.py:79`, `apps/usuarios/application/services.py:82` |
| 3 | Sin valores mágicos | Duración de sesión extraída a constante | `apps/usuarios/application/services.py:31` |
| 4 | Manejo de errores explícito | Excepciones propias del módulo | `apps/usuarios/domain/exceptions.py:4` |
| 5 | DRY | Mappers reutilizados para transformar ORM a dominio | `apps/usuarios/infrastructure/repositories.py:19`, `apps/usuarios/infrastructure/repositories.py:23` |
| 6 | Fechas timezone-aware | Dominio y servicios usan `datetime.now(UTC)` / `timezone.now()` | `apps/usuarios/domain/usuario.py:36`, `apps/usuarios/application/services.py:64` |

## 5. Mapa DDD del módulo (evidencia para la rúbrica)

| Elemento DDD | Clase(s) | Archivo |
| --- | --- | --- |
| Entidades | `Usuario`, `Rol`, `Sesion`, `IntentoLogin` | `apps/usuarios/domain/usuario.py` |
| Objetos de Valor | `Credencial`, `Permiso` | `apps/usuarios/domain/usuario.py` |
| Agregado | `Usuario` (raíz, con `Credencial` y `Rol`) | `apps/usuarios/domain/usuario.py` |
| Fábrica | `UsuarioSistemaFabrica` | `apps/usuarios/domain/usuario.py` |
| Repositorios (contratos) | `RepositorioUsuario`, `RepositorioRol`, `RepositorioSesion`, `RepositorioIntentoLogin` | `apps/usuarios/domain/repositorios.py` |
| Repositorios (implementación) | `DjangoRepositorioUsuario`, `DjangoRepositorioRol`, `DjangoRepositorioSesion`, `DjangoRepositorioIntentoLogin` | `apps/usuarios/infrastructure/repositories.py` |
| Servicios | `ServicioAutenticacion`, `ServicioGestionUsuarios` | `apps/usuarios/application/services.py` |
| Módulo | App `usuarios` con 4 capas | `apps/usuarios/` |

## 6. Definición de hecho

- [x] Estilos de programación declarados y evidenciados (sección 2).
- [x] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [x] 5+ prácticas Clean Code evidenciadas (sección 4).
- [x] Login/logout y CRUD de usuarios y roles funcionan (`.venv/bin/python manage.py check` + pruebas automatizadas).
- [x] Pruebas automatizadas agregadas en `tests/test_usuarios_auth.py`.
- [x] Cambios dentro de `apps/usuarios`, `tests`, `docs` y `config/settings/base.py` por autenticación DRF.
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).

## 7. Funcionalidades implementadas

### 7.1. Registro de clientes

El registro público se realiza con `POST /api/auth/registro/`. El usuario envía
su nombre, correo, nombre de usuario y contraseña. El rol no forma parte de la
solicitud: el sistema asigna siempre el rol `Cliente`.

Antes de guardar la cuenta se aplican estas reglas:

- El correo y el nombre de usuario deben ser únicos, incluso si cambian las
  mayúsculas.
- El nombre de usuario solo acepta letras, números, punto, guion y guion bajo.
- La contraseña pasa por los validadores configurados en Django.
- La contraseña se almacena como hash; nunca se guarda el texto original.

El rol `Cliente` se crea con la migración
`apps/usuarios/migrations/0003_crear_roles_base.py`.

### 7.2. Inicio y cierre de sesión

`POST /api/auth/login/` valida las credenciales y comprueba que la cuenta esté
activa. Cuando el acceso es correcto, crea una sesión con un token aleatorio y
una expiración de ocho horas. El frontend envía este token en
`Authorization: Bearer <token>`.

Cada intento queda registrado en `IntentoLoginModel`, indicando usuario, IP,
resultado y motivo del fallo. Esto permite revisar accesos incorrectos sin
guardar la contraseña ingresada.

`POST /api/auth/logout/` cierra la sesión asociada al token actual. Un token
cerrado, vencido o perteneciente a un usuario inactivo ya no permite acceder a
los endpoints protegidos.

### 7.3. Perfil y contraseña

El usuario autenticado puede consultar y editar sus datos desde
`GET/PATCH /api/auth/perfil/`. Solo se permite cambiar el nombre y el correo; el
rol y el nombre de usuario no pueden modificarse desde esta pantalla.

`POST /api/auth/cambiar-password/` solicita la contraseña actual antes de
aceptar una nueva. Después del cambio se cierran las otras sesiones del usuario
y se conserva únicamente la sesión desde la que realizó la operación.

También se agregó `POST /api/auth/cerrar-otras-sesiones/` para cerrar accesos
abiertos en otros navegadores o dispositivos sin cambiar la contraseña.

### 7.4. Administración de usuarios

Los endpoints `/api/usuarios/` y `/api/roles/` requieren el rol
`Administrador`. Desde ellos se puede:

- Consultar usuarios y roles.
- Crear usuarios indicando el rol correspondiente.
- Activar una cuenta inactiva.
- Desactivar una cuenta y cerrar sus sesiones abiertas.

El sistema no permite que un administrador desactive su propia cuenta. Esta
regla evita dejar la aplicación sin una sesión administrativa durante la
gestión de usuarios.

Después de aplicar las migraciones, el primer administrador se crea con:

```bash
uv run python manage.py crear_admin \
  --nombre "Administrador" \
  --email "admin@empresa.com" \
  --username admin
```

El comando solicita la contraseña de forma interactiva para que no quede escrita
en el historial del terminal.

### 7.5. Interfaz web

La página principal (`/`) incluye las pantallas de inicio de sesión, registro,
perfil y seguridad. El contenido se adapta al rol autenticado:

- Un cliente puede editar su perfil, cambiar la contraseña y cerrar sesiones.
- Un administrador dispone además del listado y formulario de usuarios.
- Las acciones muestran mensajes de confirmación o error sin recargar la página.
- La sesión se conserva en el navegador hasta cerrar sesión o hasta que el token
  deje de ser válido.

La interfaz fue revisada en escritorio y móvil. No presenta desplazamiento
horizontal y mantiene accesibles los formularios en ambos tamaños.

### 7.6. Pruebas

`tests/test_usuarios_auth.py` contiene 13 pruebas que cubren:

- Registro y almacenamiento seguro de la contraseña.
- Detección de usuarios duplicados.
- Login correcto, credenciales incorrectas y usuario inactivo.
- Consulta y modificación del perfil.
- Cambio de contraseña y cierre de sesiones.
- Restricción de las operaciones administrativas.
- Creación y desactivación de usuarios.
- Protección de la cuenta del administrador actual.
- Comando de creación del primer administrador.
