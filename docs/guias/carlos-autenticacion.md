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

Documentos separados de laboratorios:

- [`../laboratorios/carlos-lab09-coding-conventions.md`](../laboratorios/carlos-lab09-coding-conventions.md)
- [`../laboratorios/carlos-lab10-estilos-codificacion.md`](../laboratorios/carlos-lab10-estilos-codificacion.md)
- [`../laboratorios/carlos-lab11-clean-code.md`](../laboratorios/carlos-lab11-clean-code.md)
