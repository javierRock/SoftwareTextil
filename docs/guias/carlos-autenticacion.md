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

## 2. Estilo de programación (a declarar)

> **Estilo elegido:** _(completa aquí: nombre del estilo, distinto al del resto del equipo — ver lista en [README.md](README.md))_
>
> **Descripción de cómo lo aplicas en tu módulo:** _(2–4 líneas)_
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/usuarios/...
> ```

Sugerencia natural para este módulo: **Things (OOP)** — `Usuario`, `Sesion`, `Rol` como objetos con estado encapsulado y comportamiento (`sesion.cerrar()`, `sesion.esta_activa()`) — o un estilo de manejo de errores (**Tantrum**: credenciales inválidas fallan rápido con excepciones específicas).

## 3. Objetivos de refactor con SOLID (evidencia 3+)

Problemas reales detectados en el código actual; cada uno resuelto es evidencia directa de un principio:

| # | Problema actual | Refactor | Principio |
| --- | --- | --- | --- |
| 1 | `ServicioAutenticacion.__init__` recibe `DjangoRepositorioUsuario` (clase concreta) como type hint (`application/services.py`) | Tipar contra los ABCs `RepositorioUsuario`, `RepositorioSesion`, `RepositorioIntentoLogin` de `domain/repositorios.py` | **DIP** |
| 2 | `DjangoRepositorioUsuario` y compañía no heredan de los contratos ABC (`infrastructure/repositories.py`) | Hacer que cada repositorio concreto implemente su ABC (`class DjangoRepositorioUsuario(RepositorioUsuario)`) | **LSP** |
| 3 | `UsuarioViewSet`/`RolViewSet` usan `queryset` + `ModelSerializer` directo, saltándose dominio y servicios | Las acciones pasan por `ServicioGestionUsuarios`; las views solo serializan | **SRP** |
| 4 | `AllowAny` en todas las views y `SessionAuthentication` en settings, pese a que el login emite token propio | Clase de autenticación DRF que valide el token de `SesionModel` + clases de permiso por rol (`EsAdministrador`, `EsCliente`) — nuevos roles = nuevas clases, sin modificar las views | **OCP** |

## 4. Prácticas de Clean Code (evidencia 5+)

Completa la tabla con tu implementación (ver lista de referencia en [README.md](README.md)):

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo) | | |
| 2 | Funciones pequeñas, una sola responsabilidad | | |
| 3 | Sin valores mágicos (p. ej. expiración de sesión `timedelta(hours=8)` → constante `DURACION_SESION`) | | |
| 4 | Manejo de errores explícito (excepciones de dominio: `CredencialesInvalidas`, `SesionExpirada`) | | |
| 5 | DRY (mappers `_usuario_from_model` reutilizados, sin lógica duplicada de conversión) | | |

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

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3).
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] Login/logout y CRUD de usuarios y roles funcionan (`uv run python manage.py check` + prueba manual de la API).
- [ ] Commits solo dentro de `apps/usuarios` (+ `config/settings` coordinado).
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
