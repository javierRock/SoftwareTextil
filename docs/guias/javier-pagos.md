# Guía de Trabajo - Javier - Pagos

- **Integrante:** Peñalva Humire, Javier Alonzo
- **Rama:** `feature/pagos-javier`
- **Módulo:** `apps/ventas/pagos`
- **Alcance:** registro, consulta, aprobación y rechazo académico de pagos; no incluye pasarelas externas ni datos de tarjetas.

## Arquitectura del módulo

| Capa | Responsabilidad | Archivos principales |
| --- | --- | --- |
| Presentación | Adaptar HTTP, validar entrada y traducir errores | `presentation/serializers.py`, `presentation/views.py`, `presentation/urls.py` |
| Aplicación | Coordinar los casos de uso | `application/services.py` |
| Dominio | Proteger invariantes, transiciones, políticas y contratos | `domain/pago.py`, `domain/excepciones.py`, `domain/politicas.py`, `domain/repositorios.py` |
| Infraestructura | Mapear el agregado y persistirlo con Django ORM | `infrastructure/models.py`, `infrastructure/repositories.py` |

La dirección principal es `presentation -> application -> domain`; el adaptador `infrastructure` implementa un puerto de `domain`. El dominio no importa Django, DRF ni infraestructura.

## Laboratorio 9 - Convenciones de codificación

| Convención | Explicación | Archivo | Líneas | Fragmento real |
| --- | --- | --- | --- | --- |
| PEP 8 | Ruff valida imports, espaciado y longitud; el módulo fue formateado con Ruff. | `domain/pago.py` | 20-22 | `@dataclass` / `class Pago:` |
| Nombres | Se usa `PascalCase` en clases, `snake_case` en operaciones y lenguaje ubicuo. | `application/services.py` | 17-29 | `class ServicioPagos` y `def registrar_pago(...) -> Pago` |
| Type hints | Parámetros y retornos públicos declaran tipos, incluido `Decimal`. | `application/services.py` | 23-29 | `monto: Decimal`, `metodo: MetodoPago | str`, `-> Pago` |
| Imports explícitos | La reexportación expone únicamente el modelo necesario y declara `__all__`. | `infrastructure/models.py` | 1-5 | `from apps.ventas.models import PagoModel` y `__all__ = ["PagoModel"]` |
| Docstrings útiles | Los módulos y clases públicas describen responsabilidad, no pasos obvios. | `domain/repositorios.py` | 1-13 | `"""Puerto de persistencia requerido por los casos de uso de pagos."""` |
| Enums y ausencia de valores mágicos | Las transiciones comparan y asignan miembros de `EstadoPago`. | `domain/pago.py` | 51-59 | `self.estado = EstadoPago.APROBADO` |
| Organización por capas | El servicio importa el contrato de dominio y no el adaptador Django. | `application/services.py` | 13-21 | `RepositorioPago` se recibe por constructor. |
| Errores consistentes | Cada fallo esperado hereda de `ErrorPago` y tiene un código estable. | `domain/excepciones.py` | 4-34 | `PagoNoEncontrado`, `PagoYaProcesado`, `MontoPagoInvalido` |
| Funciones pequeñas | La obtención común se concentra en una función privada con una sola salida válida. | `application/services.py` | 64-71 | `_obtener_existente(...) -> Pago` |
| Constantes | Los nombres de campos sensibles se centralizan en una constante inmutable. | `presentation/serializers.py` | 5-12 | `DATOS_SENSIBLES_PROHIBIDOS = frozenset(...)` |

Las validaciones del agregado comprueban identificadores, `Decimal`, monto positivo, método soportado y referencia en `domain/pago.py:37-49`. La conversión de un texto a `MetodoPago` intercepta únicamente los errores esperados de Python y los traduce a `MetodoPagoNoSoportado`; no se usa `ValueError` para expresar una regla del pago.

## Laboratorio 10 - Estilos de programación

| Estilo | Definición breve | Cómo se aplicó | Archivo y líneas | Fragmento real |
| --- | --- | --- | --- | --- |
| Things | Objetos que reúnen estado y comportamiento. | `Pago` es raíz del agregado y controla sus transiciones. | `domain/pago.py:20-59` | `def aprobar(self) -> None:` / `def rechazar(self) -> None:` |
| Error/Exception Handling | Los errores esperados se modelan, propagan y traducen explícitamente. | El dominio lanza `ErrorPago`; presentación centraliza códigos HTTP y JSON. | `domain/excepciones.py:4-70`, `presentation/views.py:24-58` | `except ErrorPago as error: return _respuesta_error(error)` |
| Persistent-Tables | Las entidades se almacenan en tablas mediante un adaptador. | `DjangoRepositorioPago` implementa el puerto y encierra consultas/conversiones ORM. | `infrastructure/repositories.py:10-55` | `class DjangoRepositorioPago(RepositorioPago):` |
| RESTful | El pago se expone como recurso y las transiciones como acciones. | ViewSet ofrece listar, crear, obtener, aprobar y rechazar con estados 200/201/400/404/409. | `presentation/views.py:61-99` | `@action(detail=True, methods=["post"], url_path="aprobar")` |

### Contrato REST

| Método y ruta | Caso de uso | Éxito |
| --- | --- | --- |
| `GET /api/ventas/pagos/` | Listar pagos | `200 OK` |
| `GET /api/ventas/pagos/?pedido_id=<id>` | Listar por pedido | `200 OK` |
| `POST /api/ventas/pagos/` | Registrar un pago pendiente | `201 Created` |
| `GET /api/ventas/pagos/<id>/` | Obtener un pago | `200 OK` |
| `POST /api/ventas/pagos/<id>/aprobar/` | Aprobar un pago pendiente | `200 OK` |
| `POST /api/ventas/pagos/<id>/rechazar/` | Rechazar un pago pendiente | `200 OK` |

Los errores controlados usan `{"codigo": "...", "detalle": "..."}`. Una entrada inválida devuelve 400, un pago inexistente 404 y una transición sobre un estado final 409.

## Laboratorio 11 - Clean Code

| Categoría | Práctica aplicada | Archivo y líneas | Fragmento real |
| --- | --- | --- | --- |
| Nombres | Lenguaje ubicuo sin abreviaturas públicas ambiguas. | `application/services.py:17-71` | `ServicioPagos`, `repositorio_pago`, `listar_por_pedido` |
| Funciones | Métodos breves y enfocados; la búsqueda común se extrae una vez. | `application/services.py:41-71` | `obtener`, `listar`, `aprobar`, `rechazar`, `_obtener_existente` |
| Comentarios | Se prefieren nombres y docstrings de decisión; no hay comentarios que repitan el código. | `domain/politicas.py:13-60` | `"""Exige una referencia para medios de pago trazables."""` |
| Estructura | Dominio independiente; servicio sobre un puerto; ORM aislado. | `application/services.py:5-14` | No hay imports de Django, DRF ni infraestructura. |
| Objetos y datos | `Pago` usa `Dinero`, `EstadoPago` y `MetodoPago`; el ORM no sale de infraestructura. | `domain/pago.py:20-35`, `presentation/serializers.py:48-63` | `monto: Dinero`, `metodo: MetodoPago` |
| Errores | Jerarquía específica y traducción HTTP en un solo punto. | `domain/excepciones.py:4-70`, `presentation/views.py:24-58` | `ESTADOS_HTTP_ERROR` y `_ejecutar_caso_uso` |
| Clases | Cada clase tiene una responsabilidad: agregado, política, servicio, repositorio o adaptador HTTP. | `domain/politicas.py:13-83`, `infrastructure/repositories.py:24-55` | `PoliticaReferenciaPago`, `ValidadorMetodoPago`, `DjangoRepositorioPago` |

Otras correcciones incluyen orden determinista por `fecha` e `id`, uso monetario exclusivo de `Decimal`, rechazo de campos de tarjeta/CVV/PIN y eliminación de acceso ORM desde las vistas.

## SOLID

| Principio | Aplicación real | Archivo y líneas | Fragmento real |
| --- | --- | --- | --- |
| SRP | ViewSet adapta HTTP, servicio coordina, agregado decide y repositorio persiste. | `presentation/views.py:61-99`, `application/services.py:17-71` | `PagoViewSet` delega en `ServicioPagos`. |
| OCP | Las reglas de referencia son estrategias registrables; una nueva política no modifica el agregado ni el servicio. | `domain/politicas.py:13-83` | `ValidadorMetodoPago(politicas: Iterable[PoliticaReferenciaPago] | None)` |
| LSP | El repositorio Django implementa todos los métodos del contrato y puede sustituir un fake. | `domain/repositorios.py:8-29`, `infrastructure/repositories.py:24-55` | `class DjangoRepositorioPago(RepositorioPago):` |
| DIP | El caso de uso recibe la abstracción por constructor. | `application/services.py:17-21` | `def __init__(self, repositorio_pago: RepositorioPago) -> None:` |

## DDD

| Elemento DDD | Implementación | Archivo y líneas |
| --- | --- | --- |
| Entidad y raíz de agregado | `Pago`, con identidad, invariantes y transiciones | `domain/pago.py:20-59` |
| Objetos de valor | `Dinero`, `EstadoPago`, `MetodoPago` | `domain/pago.py:8-9, 24-30` |
| Servicio/política de dominio | `ValidadorMetodoPago` y políticas de referencia | `domain/politicas.py:13-83` |
| Fábrica | `PagoFactory` crea identidad y estado inicial | `domain/pago.py:62-82` |
| Repositorio abstracto | `RepositorioPago` | `domain/repositorios.py:8-29` |
| Repositorio concreto | `DjangoRepositorioPago` | `infrastructure/repositories.py:24-55` |
| Módulo | Contexto de pagos separado en cuatro capas | `apps/ventas/pagos/` |

## Pruebas automatizadas

| Nivel | Archivo | Cobertura funcional |
| --- | --- | --- |
| Dominio | `tests/pagos/test_pago_dominio.py` | Creación, estados, transiciones, monto, métodos, referencias e identificadores |
| Aplicación | `tests/pagos/test_servicio_pagos.py` | Casos de uso con `RepositorioPagoMemoria`, sin Django ORM |
| Infraestructura | `tests/pagos/test_repositorio_pagos.py` | Alta, recuperación, actualización, filtro, orden y conversión |
| API | `tests/pagos/test_api_pagos.py` | 201, 200, 400, 404, 409, filtro y rechazo de datos sensibles |

## Verificación

Resultados reales obtenidos el 20 de julio de 2026:

| Comando | Resultado verificable |
| --- | --- |
| `uv sync` | Correcto con `uv 0.11.30` instalado temporalmente en `/tmp/opencode/uv`; 11 paquetes instalados en `.venv`. |
| `uv run python manage.py check` | `System check identified no issues (0 silenced).` |
| `uv run pytest -q` | `46 passed in 0.28s` en la ejecución previa a la documentación. |
| `uv run python manage.py makemigrations --check --dry-run` | `No changes detected`. |
| `uvx ruff check apps/ventas/pagos tests/pagos apps/ventas/models.py` | `All checks passed!` |
| `uvx ruff format --check apps/ventas/pagos tests/pagos apps/ventas/models.py` | Detectó inicialmente 3 archivos; se aplicó formato y se vuelve a verificar al cierre. |
| SonarLint/SonarQube for IDE | No ejecutado: no hay CLI ni integración IDE accesible en este entorno. Véase [`../reportes/sonarlint-pagos.md`](../reportes/sonarlint-pagos.md). |

No se modificó el esquema de `PagoModel`; la limpieza de `apps/ventas/models.py` consolidó imports y docstring. Por ello no se generó una migración y Django confirmó que no hay cambios pendientes.

## Checklist de entrega

- [x] Cuatro estilos implementados y documentados.
- [x] Siete categorías de Clean Code evidenciadas.
- [x] SRP, OCP, LSP y DIP aplicados con utilidad real.
- [x] Entidad/agregado, objetos de valor, política, fábrica y repositorios DDD.
- [x] Pruebas de dominio, aplicación, infraestructura y API.
- [x] `manage.py check`, pytest, migraciones y Ruff verificados.
- [ ] Ejecutar SonarLint en el IDE y adjuntar evidencia real.
- [ ] Abrir Pull Request hacia `dev` después de revisión; no se hizo push, merge ni rebase.
