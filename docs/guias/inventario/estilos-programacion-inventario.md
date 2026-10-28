# Estilos de programación aplicados al módulo de inventario

## 1. Contexto del módulo

El módulo `apps/inventario` controla stock, movimientos y alertas de prendas. Sigue una arquitectura en capas con dominio, aplicación, infraestructura y presentación, y se integra con el catálogo para validar la existencia de prendas.

Archivos principales:
- `apps/inventario/domain/stock_prenda.py`
- `apps/inventario/domain/excepciones.py`
- `apps/inventario/application/services.py`
- `apps/inventario/infrastructure/models.py`
- `apps/inventario/infrastructure/repositories.py`
- `apps/inventario/presentation/serializers.py`
- `apps/inventario/presentation/views.py`

## 2. Estilos seleccionados

| Estilo | Concepto | Aplicación en inventario | Evidencia |
|---|---|---|---|
| Things | Objetos con estado y comportamiento | `StockPrenda` encapsula ingresos, salidas y alertas | `apps/inventario/domain/stock_prenda.py` |
| Pipeline | Flujo explícito por etapas | Serializer → servicio → dominio → repositorio → respuesta | `apps/inventario/presentation/views.py` |
| Error/Exception Handling | Fallar con excepciones específicas | `CantidadInvalida`, `StockInsuficiente`, `StockNoEncontrado` | `apps/inventario/domain/excepciones.py` |
| Persistent-Tables | Reglas sobre tablas relacionales | Models con FK, `select_for_update`, constraints y consultas ORM | `apps/inventario/models.py`, `infrastructure/repositories.py` |

## 3. Descripción de cada estilo

### Things

Las entidades no son contenedores planos: concentran reglas de negocio.

Restricción tomada del estilo: los datos internos no se modifican arbitrariamente desde fuera.

Componente: `StockPrenda`.

Motivo: el stock debe impedir cantidades negativas y producir movimientos coherentes.

Ventaja: las reglas quedan en el dominio y no en la vista.

Limitación: requiere disciplina para no “escapar” atributos mutables fuera del agregado.

Fragmento:
```python
def registrar_ingreso(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
    self._validar_cantidad(cantidad)
    self.cantidad_actual += cantidad
    self.ultima_actualizacion = datetime.utcnow()
    return self._crear_movimiento(TipoMovimiento.INGRESO, cantidad, motivo, usuario_id)
```
Ruta: `apps/inventario/domain/stock_prenda.py`

### Pipeline

El caso de uso se entiende como una cadena de transformación.

Restricción tomada del estilo: cada etapa recibe una entrada definida y devuelve una salida definida.

Componente: `StockViewSet` + `ServicioInventario`.

Motivo: el flujo de ingreso/salida debe ser visible y testeable por etapas.

Ventaja: reduce acoplamiento entre validación, dominio y persistencia.

Limitación: si la vista crece, el pipeline debe seguir dividido en funciones pequeñas.

Fragmento:
```python
serializer = MovimientoStockSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
movimiento = servicio.registrar_salida(
    prenda_id=serializer.validated_data["prenda_id"],
    cantidad=serializer.validated_data["cantidad"],
    motivo=serializer.validated_data["motivo"],
    usuario_id=_usuario_responsable_desde_solicitud(request, serializer.validated_data.get("usuario_id")),
)
```
Ruta: `apps/inventario/presentation/views.py`

### Error/Exception Handling

Las reglas de negocio fallan con excepciones específicas y se traducen a HTTP en la presentación.

Restricción tomada del estilo: no ocultar errores con un `except Exception` genérico.

Componente: `excepciones.py` + `_manejar_error`.

Motivo: cantidad inválida, prenda inexistente y stock insuficiente no significan lo mismo.

Ventaja: errores más claros y respuestas HTTP coherentes.

Limitación: hay que mantener alineación entre dominio y mapeo HTTP.

Fragmento:
```python
class StockInsuficiente(ErrorInventario):
    """El stock disponible no alcanza para la operación solicitada."""


def _manejar_error(exc: Exception) -> tuple[dict[str, str], int]:
    if isinstance(exc, (CantidadInvalida, StockInsuficiente, UsuarioResponsableRequerido)):
        return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST
```
Ruta: `apps/inventario/domain/excepciones.py`, `apps/inventario/presentation/views.py`

### Persistent-Tables

La persistencia se apoya en tablas relacionales con restricciones e integridad referencial.

Restricción tomada del estilo: consultar relaciones reales del ORM en lugar de filtrar todo en memoria.

Componente: `StockPrendaModel`, `MovimientoInventarioModel`, repositorios Django.

Motivo: stock, movimientos y alertas viven en tablas separadas con FK.

Ventaja: integridad referencial y soporte para bloqueo transaccional.

Limitación: algunas pruebas de bloqueo no son confiables en SQLite.

Fragmento:
```python
class MovimientoInventarioModel(models.Model):
    stock = models.ForeignKey(StockPrendaModel, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=30)
    cantidad = models.IntegerField()
    motivo = models.TextField()
    registrado_por = models.CharField(max_length=36)
```
Ruta: `apps/inventario/models.py`

## 4. Flujo de ingreso

HTTP → Serializer → Servicio → Dominio → Repositorio → Movimiento → Respuesta

## 5. Flujo de salida

HTTP → Serializer → Servicio → `select_for_update()` → Dominio valida stock → Repositorio persiste → Movimiento → Respuesta

Si el stock es insuficiente, el dominio lanza `StockInsuficiente` y la vista responde sin persistir cambios.

## 6. Análisis de calidad

| Archivo / componente | Herramienta | Rule ID | Severidad | Problema real | Corrección | Estado |
|---|---|---|---|---|---|---|
| `apps/inventario/domain/repositorios.py` | Revisión manual | Revisión manual — Rule ID no verificado | Media | El contrato no declaraba `listar()` aunque el servicio lo invoca | Agregar el método abstracto | Corregido |
| `apps/inventario/presentation/views.py` | Revisión manual | Revisión manual — Rule ID no verificado | Media | Se hacía una consulta extra a `MovimientoInventarioModel` para responder | Responder con el movimiento ya creado | Corregido |
| `apps/inventario/infrastructure/repositories.py` | Revisión manual | Revisión manual — Rule ID no verificado | Baja | Falta de `select_related` al listar movimientos | Agregar `select_related("stock")` | Corregido |

> SonarLint/SonarQube: no hay integración visible en el repositorio ni acceso a diagnósticos del IDE desde este entorno.

## 7. Pruebas

Casos cubiertos:
- ingreso válido y acumulación;
- salida válida y salida exacta a cero;
- stock inexistente;
- stock insuficiente;
- reversión cuando falla el guardado del movimiento;
- bloqueo/concurrencia documentada para SQLite.

Comandos ejecutados:
- `uv run pytest apps/inventario`
- `uv run python manage.py check`

Resultados reales:
- `23 passed, 1 skipped`
- `System check identified no issues (0 silenced)`

Limitación:
- la prueba de bloqueo de filas se omite en SQLite porque no garantiza concurrencia real.

## 8. Conclusiones

Los estilos aplicados mejoran la separación de responsabilidades: el dominio modela el comportamiento, la aplicación orquesta, la infraestructura persiste y la presentación traduce errores a HTTP. Eso hace el módulo más mantenible, más testeable y más seguro frente a stock negativo o salidas sin existencias.
