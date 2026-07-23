# Prácticas de Clean Code aplicadas al módulo de inventario

## 1. Contexto

El módulo `apps/inventario/` controla el stock de prendas, sus movimientos, alertas y la consulta de existencias. Sigue una arquitectura en capas con dominio puro, servicios de aplicación, repositorios y una presentación DRF que traduce HTTP a casos de uso.

## 2. Resumen de prácticas

| Categoría                      | Práctica aplicada                                                          | Archivo                                   | Beneficio                                                                   |
| ------------------------------ | -------------------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------------------------------------- |
| Nombres                        | Excepción de dominio explícita para stock duplicado (`StockYaExiste`)      | `apps/inventario/domain/excepciones.py`   | Hace visible la regla de negocio y evita errores genéricos.                 |
| Funciones                      | `crear_stock()` con guard clause y transacción atómica                     | `apps/inventario/application/services.py` | Reduce anidamiento, evita errores de persistencia y mejora la consistencia. |
| Comentarios                    | Sustitución de un TODO genérico por una nota útil sobre el fallback SQLite | `config/settings/dev.py`                  | El comentario describe por qué existe la decisión, no repite código.        |
| Estructura de código fuente    | Separación vertical de helpers y endpoints en presentación                 | `apps/inventario/presentation/views.py`   | Mejora legibilidad y deja el flujo HTTP arriba, detalles abajo.             |
| Objetos y estructuras de datos | El agregado `StockPrenda` encapsula ingreso/salida/ajuste                  | `apps/inventario/domain/stock_prenda.py`  | Evita mutaciones externas del stock y concentra invariantes del dominio.    |
| Tratamiento de errores         | Traducción explícita de errores de dominio a HTTP 404/409                  | `apps/inventario/presentation/views.py`   | Evita fugas de errores internos y devuelve respuestas coherentes.           |
| Clases                         | `ServicioInventario` queda como orquestador del caso de uso                | `apps/inventario/application/services.py` | Mantiene una sola responsabilidad principal por clase.                      |

## 3. Evidencias

### Categoría: Nombres

**Práctica aplicada:**
Uso de un nombre de excepción que expresa la regla del negocio.

**Problema encontrado:**
No existía una forma explícita de representar el caso “ya hay un stock para esta prenda”, por lo que la violación terminaba en una excepción técnica de base de datos.

**Archivo o componente:**
`apps/inventario/domain/excepciones.py` — `StockYaExiste`.

**Corrección realizada:**
Se agregó una excepción de dominio con un nombre que revela intención y dominio.

**Fragmento de código:**

```python
class StockInsuficiente(ErrorInventario):
    """El stock disponible no alcanza para la operación solicitada."""


class StockYaExiste(ErrorInventario):
    """Ya existe un stock registrado para la prenda indicada."""


class UsuarioResponsableRequerido(ErrorInventario):
    """No fue posible determinar el usuario responsable."""
```

**Beneficio:**
El nombre comunica la regla sin necesidad de comentarios extra y facilita búsquedas, pruebas y manejo de errores.

### Categoría: Funciones

**Práctica aplicada:**
Guard clause y una sola responsabilidad en `crear_stock()`.

**Problema encontrado:**
La creación de stock podía terminar en un error de base de datos si la prenda ya tenía stock, sin una traducción de negocio clara.

**Archivo o componente:**
`apps/inventario/application/services.py` — `ServicioInventario.crear_stock()`.

**Corrección realizada:**
Se validó la existencia previa del stock antes de persistir y se protegió la operación con `transaction.atomic()`.

**Fragmento de código:**

```python
def crear_stock(self, prenda_id: str, stock_inicial: int, stock_minimo: int, ubicacion: str = "almacen") -> StockPrenda:
    with transaction.atomic():
        self._validar_prenda_existente(prenda_id)

        if self.repo_inventario.buscar_por_prenda(prenda_id) is not None:
            raise StockYaExiste("Ya existe stock para la prenda")

        stock = InventarioFabrica.crear(prenda_id, stock_inicial, stock_minimo, ubicacion)
```

**Beneficio:**
La función queda más corta, legible y resistente a duplicados y carreras de persistencia.

### Categoría: Comentarios

**Práctica aplicada:**
Reemplazo de un TODO genérico por una nota descriptiva y útil.

**Problema encontrado:**
El comentario anterior solo decía que había que cambiar a PostgreSQL, sin explicar el contexto de desarrollo local.

**Archivo o componente:**
`config/settings/dev.py` — comentario sobre el fallback de base de datos.

**Corrección realizada:**
Se reescribió el comentario para explicar que SQLite es un respaldo temporal para desarrollo local.

**Fragmento de código:**

```python
"""Settings de desarrollo. Usa SQLite como fallback temporal hasta tener PostgreSQL."""

from config.settings.base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# SQLite queda como respaldo temporal para desarrollo local hasta disponer de PostgreSQL.
DATABASES = {
```

**Beneficio:**
El comentario justifica la decisión y evita ruido documental innecesario.

### Categoría: Estructura de código fuente

**Práctica aplicada:**
Agrupación vertical de helpers antes de las vistas y separación clara de responsabilidades.

**Problema encontrado:**
La presentación necesitaba más orden para distinguir helpers internos, mapeo de errores y endpoints HTTP.

**Archivo o componente:**
`apps/inventario/presentation/views.py` — helpers y `StockViewSet`.

**Corrección realizada:**
Se dejó el bloque de utilidades arriba y la lógica HTTP debajo, con un flujo lineal.

**Fragmento de código:**

```python
def _servicio() -> ServicioInventario:
    return ServicioInventario(
        DjangoRepositorioInventario(),
        DjangoRepositorioMovimiento(),
        DjangoRepositorioAlertaStock(),
        DjangoRepositorioPrenda(),
    )


def _usuario_responsable_desde_solicitud(request) -> str:
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        return str(request.user.id)
    raise UsuarioResponsableRequerido("Usuario responsable requerido")
```

**Beneficio:**
La estructura facilita escaneo visual, mantenimiento y extracción de responsabilidades cuando crezca el módulo.

### Categoría: Objetos y estructuras de datos

**Práctica aplicada:**
El agregado `StockPrenda` encapsula el estado y expone operaciones de negocio.

**Problema encontrado:**
El stock no debería mutarse desde capas externas con asignaciones directas porque eso rompe invariantes del dominio.

**Archivo o componente:**
`apps/inventario/domain/stock_prenda.py` — `StockPrenda`.

**Corrección realizada:**
Se mantiene el cambio de estado dentro de métodos del agregado como `registrar_ingreso()` y `registrar_salida()`.

**Fragmento de código:**

```python
def registrar_ingreso(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
    self._validar_cantidad(cantidad)
    self.cantidad_actual += cantidad
    self.ultima_actualizacion = datetime.utcnow()
    return self._crear_movimiento(TipoMovimiento.INGRESO, cantidad, motivo, usuario_id)

def registrar_salida(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
    self._validar_cantidad(cantidad)
    if cantidad > self.cantidad_actual:
        raise StockInsuficiente("No hay stock suficiente para la salida")
    self.cantidad_actual -= cantidad
```

**Beneficio:**
Las reglas del stock viven en el agregado y no se dispersan por serializadores, vistas o repositorios.

### Categoría: Tratamiento de errores y excepciones

**Práctica aplicada:**
Traducción explícita de errores de dominio a respuestas HTTP precisas.

**Problema encontrado:**
La creación de stock sin prenda o con duplicado podía terminar como error técnico o 500 implícito.

**Archivo o componente:**
`apps/inventario/presentation/views.py` — `_manejar_error()` y `StockViewSet.create()`.

**Corrección realizada:**
Se mapean `PrendaNoEncontrada` a 404 y `StockYaExiste` a 409.

**Fragmento de código:**

```python
def _manejar_error(exc: Exception) -> tuple[dict[str, str], int]:
    if isinstance(exc, (CantidadInvalida, StockInsuficiente, UsuarioResponsableRequerido)):
        return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST
    if isinstance(exc, (PrendaNoEncontrada, StockNoEncontrado)):
        return {"error": str(exc)}, status.HTTP_404_NOT_FOUND
    if isinstance(exc, StockYaExiste):
        return {"error": str(exc)}, status.HTTP_409_CONFLICT
    return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST
```

**Beneficio:**
El cliente recibe errores consistentes y el sistema evita exponer detalles internos de persistencia.

### Categoría: Clases

**Práctica aplicada:**
`ServicioInventario` queda como orquestador del caso de uso, mientras la vista solo traduce HTTP.

**Problema encontrado:**
La capa de presentación estaba demasiado cerca del dato del usuario y podía decidir la identidad del responsable.

**Archivo o componente:**
`apps/inventario/presentation/views.py` y `apps/inventario/application/services.py`.

**Corrección realizada:**
La vista deja de confiar en el cliente para el usuario responsable y el servicio concentra la orquestación de reglas y repositorios.

**Fragmento de código:**

```python
class StockViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = CrearStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            stock = servicio.crear_stock(
                prenda_id=serializer.validated_data["prenda_id"],
                stock_inicial=serializer.validated_data["stock_inicial"],
                stock_minimo=serializer.validated_data["stock_minimo"],
                ubicacion=serializer.validated_data["ubicacion"],
            )
```

**Beneficio:**
Cada clase tiene una razón principal para cambiar y la frontera entre HTTP y negocio queda más limpia.

## 4. Hallazgos de SonarLint

### SonarLint / SonarQube

No se pudieron recuperar diagnósticos reales desde OpenCode. El servidor LSP configurado no está instalado aquí (`basedpyright-langserver` ausente), así que no hay Rule ID verificable para citar.

| Archivo / componente | Herramienta | Rule ID       | Tipo | Problema                        | Corrección          | Estado    |
| -------------------- | ----------- | ------------- | ---- | ------------------------------- | ------------------- | --------- |
| N/A                  | SonarLint   | No verificado | N/A  | No accesible desde este entorno | Verificar en el IDE | Pendiente |

### Resultados de otras herramientas

| Archivo / componente                       | Herramienta     | Rule ID       | Tipo                          | Problema                                                                                 | Corrección                                                                    | Estado    |
| ------------------------------------------ | --------------- | ------------- | ----------------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------- |
| `apps/inventario/*`                        | Revisión manual | No verificado | Mantenibilidad / Arquitectura | `create_stock()` no traducía duplicados ni prenda inexistente a errores de dominio/HTTP. | Se añadió `StockYaExiste`, se devolvió 404/409 y se protegió con transacción. | Corregido |
| `apps/inventario/presentation/views.py`    | Revisión manual | No verificado | Vulnerabilidad                | El usuario responsable podía depender del payload del cliente.                           | Ahora se deriva de `request.user`.                                            | Corregido |
| `apps/inventario/infrastructure/models.py` | Revisión manual | No verificado | Code Smell                    | Wildcard import con `# noqa`.                                                            | Se cambiaron a imports explícitos.                                            | Corregido |

### Revisión manual

Hallazgos confirmados manualmente: falta de nombre de dominio para stock duplicado, traducción incompleta de errores en creación de stock, y spoofing potencial del usuario responsable.

## 5. Bugs, code smells y vulnerabilidades corregidos

| Situación anterior                                                      | Riesgo                                                | Corrección                                               | Archivo                                                                            | Estado final |
| ----------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------ |
| Crear stock duplicado terminaba en error técnico de base de datos.      | 500, mala UX, posible inconsistencia en la capa HTTP. | Se agregó `StockYaExiste` y se tradujo a `409 Conflict`. | `apps/inventario/application/services.py`, `apps/inventario/presentation/views.py` | Corregido    |
| Crear stock con prenda inexistente no se traducía correctamente a HTTP. | 500 inesperado.                                       | `PrendaNoEncontrada` ahora retorna `404`.                | `apps/inventario/presentation/views.py`                                            | Corregido    |
| El usuario responsable podía depender del campo enviado por el cliente. | Spoofing del auditor / trazabilidad incorrecta.       | Se fuerza `request.user.id` como fuente real.            | `apps/inventario/presentation/views.py`                                            | Corregido    |
| `infrastructure/models.py` usaba wildcard import.                       | Mantenibilidad baja y análisis estático más débil.    | Imports explícitos.                                      | `apps/inventario/infrastructure/models.py`                                         | Corregido    |

## 6. Pruebas y validación

### Comandos ejecutados

| Comando                                          | ¿Pudo ejecutarse? | Resultado | Error encontrado                                | ¿Fue causado por los cambios? |
| ------------------------------------------------ | ----------------- | --------- | ----------------------------------------------- | ----------------------------- |
| `python manage.py check`                         | No                | Falló     | `ModuleNotFoundError: No module named 'django'` | No                            |
| `python manage.py makemigrations --check`        | No                | Falló     | `ModuleNotFoundError: No module named 'django'` | No                            |
| `python -m pytest apps/inventario -v`            | No                | Falló     | `No module named pytest`                        | No                            |
| `uv run python manage.py check`                  | Sí                | OK        | Ninguno                                         | No                            |
| `uv run python manage.py makemigrations --check` | Sí                | OK        | Ninguno                                         | No                            |
| `uv run pytest apps/inventario -v`               | Sí                | OK        | Ninguno                                         | No                            |

### Pruebas ejecutadas

- `apps/inventario/tests/test_domain.py`
- `apps/inventario/tests/test_service.py`
- `apps/inventario/tests/test_api.py`
- `apps/inventario/tests/test_concurrency.py`

### Resultados reales

- `29 passed, 1 skipped`
- El caso de concurrencia se salta en SQLite porque no ofrece bloqueo de filas real.

### Limitaciones

- No se pudo usar SonarLint desde OpenCode porque el LSP configurado no está instalado.
- No hay configuración visible de Ruff, Flake8, Pylint, Bandit o MyPy en este repositorio.
