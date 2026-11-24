# Guía de Trabajo — Lizzy · Catálogo

- **Integrante:** Huayhua Perez, Lizzy Arlette
- **Rama:** `feature/catalogo-lizzy`
- **Módulo:** `apps/catalogo` (prendas, categorías, tipos de producto)

## 1. Alcance y archivos del módulo

| Capa | Archivos |
| --- | --- |
| Dominio | `apps/catalogo/domain/prenda.py`, `apps/catalogo/domain/repositorios.py` |
| Aplicación | `apps/catalogo/application/services.py` |
| Infraestructura | `apps/catalogo/models.py`, `apps/catalogo/infrastructure/models.py`, `apps/catalogo/infrastructure/repositories.py` |
| Presentación | `apps/catalogo/presentation/serializers.py`, `views.py`, `urls.py` |

## 2. Estilo de programación (a declarar)

> **Estilo elegido:** _(completa aquí: nombre del estilo, distinto al del resto del equipo — ver lista en [README.md](README.md))_
>
> **Descripción de cómo lo aplicas en tu módulo:** _(2–4 líneas)_
>
> **Evidencia (fragmento de código con ruta y líneas):**
>
> ```python
> # apps/catalogo/...
> ```

Sugerencia natural para este módulo: **Pipeline** — el listado/búsqueda de prendas como cadena de funciones puras (filtrar por categoría → filtrar por estado → mapear a DTO), sin estado compartido.

## 3. Objetivos de refactor con SOLID (evidencia 3+)

| # | Problema o responsabilidad | Refactoring aplicado / pendiente | Principio | Estrategia de Refactoring |
| --- | --- | --- | --- | --- |
| 1 | El servicio de aplicación no debe depender de repositorios Django concretos. | Se extrajeron los contratos `RepositorioPrenda` y `RepositorioCatalogo` en `domain/repositorios.py` a partir de las operaciones que `ServicioCatalogo` necesita, y el constructor del servicio pasó a recibirlos. **Aplicado**; commit `739aab7`. | **DIP** | **Extract Interface** (Extraer Interfaz / Contrato Abstracto). |
| 2 | Los adaptadores concretos deben cumplir los contratos y poder sustituirse sin cambiar el servicio. | `DjangoRepositorioPrenda` y `DjangoRepositorioCatalogo` implementan explícitamente los ABC. Las pruebas de servicio usan repositorios en memoria y las pruebas de integración ejercitan los adaptadores Django. **Aplicado**; commit `739aab7`. | **LSP** | **Implement Contract** (Implementar el Contrato) usando las interfaces extraídas. |
| 3 | Las vistas no deben contener reglas de negocio de prendas, categorías y tipos. | Las operaciones de alta/edición de prendas y CRUD de categoría/tipo delegan al servicio. **Parcial**: `PrendaViewSet` conserva consultas ORM para listados/detalles y persiste imágenes directamente. | **SRP** | **Extract Method** (Extraer Método) y **Move Method** (Mover Método a la capa de Aplicación). |
| 4 | Los contratos deben ser pequeños y específicos por agregado. | Hoy `RepositorioCatalogo` combina operaciones de categorías y tipos de producto. Separarlo en `RepositorioCategoria` y `RepositorioTipoProducto` sigue **pendiente**; no se identificó todavía código muerto que justifique eliminar métodos. | **ISP** | **Extract Interface** (Segregar/Extraer contratos) y **Remove Dead Code** (solo tras confirmar métodos sin uso). |

### Registro de smells y evidencias de refactoring

| Smell | Módulo o componente | Responsable | Estrategia de Refactoring |
| --- | --- | --- | --- |
| **Q-06 · Duplicación (DRY)** | Catálogo · `ServicioCatalogo` | Lizzy | **Extract Method** (Extraer Método) |
| **Q-07 · Lista larga de parámetros** | Catálogo · `ServicioCatalogo` y adaptador `PrendaViewSet` | Lizzy | **Extract Class** (Extraer Clase / Objeto de Valor), materializada con el patrón **Introduce Parameter Object** |

Verificación registrada para el estado actual: `22` pruebas de servicio/registro aprobadas y Ruff sin hallazgos en los archivos modificados.

### Estrategias aplicadas: antes y después

#### Q-06 · Duplicación (DRY) — Extract Method (Extraer Método)

Antes, los dos métodos contenían la misma validación:

```python
# Fragmento repetido en crear_prenda y actualizar_prenda
if self.repo_catalogo.buscar_categoria(categoria_id) is None:
    raise RecursoNoEncontradoError("La categoria no existe")
if (
    tipo_producto_id is not None
    and self.repo_catalogo.buscar_tipo(tipo_producto_id) is None
):
    raise RecursoNoEncontradoError("El tipo de producto no existe")
```

Después, ambos métodos llaman al método extraído y la regla queda en un solo lugar:

```python
def crear_prenda(...):
    self._validar_categoria_y_tipo(datos.categoria_id, datos.tipo_producto_id)
    ...

def actualizar_prenda(...):
    self._validar_categoria_y_tipo(datos.categoria_id, datos.tipo_producto_id)
    ...

def _validar_categoria_y_tipo(
    self,
    categoria_id: str,
    tipo_producto_id: str | None,
) -> None:
    if self.repo_catalogo.buscar_categoria(categoria_id) is None:
        raise RecursoNoEncontradoError("La categoria no existe")
    if (
        tipo_producto_id is not None
        and self.repo_catalogo.buscar_tipo(tipo_producto_id) is None
    ):
        raise RecursoNoEncontradoError("El tipo de producto no existe")
```

La variante aplicada de **Extract Method** toma el fragmento común de alta y edición y lo concentra en `_validar_categoria_y_tipo`. Evidencia de pruebas y cambios: commits `cd40049` y `8b5b1fb`.

#### Q-07 · Lista larga de parámetros — Extract Class

Antes, el servicio recibía cada dato comercial por separado:

```python
def crear_prenda(
    self,
    nombre: str,
    descripcion: str,
    precio_monto: str,
    precio_moneda: str,
    categoria_id: str,
    registrado_por: str | None,
    tipo_producto_id: str | None = None,
    tallas: list[str] | None = None,
) -> Prenda:
    ...
```

Después, esos campos cohesivos viajan agrupados en un objeto inmutable y la vista mantiene el serializer/HTTP como adaptador:

```python
@dataclass(frozen=True)
class DatosComercialesPrenda:
    nombre: str
    descripcion: str
    precio_monto: str
    precio_moneda: str
    categoria_id: str
    tipo_producto_id: str | None = None

def crear_prenda(
    self,
    datos: DatosComercialesPrenda,
    registrado_por: str | None,
    tallas: list[str] | None = None,
) -> Prenda:
    ...

prenda = servicio.crear_prenda(
    datos=DatosComercialesPrenda(
        nombre=serializer.validated_data["nombre"],
        descripcion=serializer.validated_data["descripcion"],
        precio_monto=serializer.validated_data["precio_monto"],
        precio_moneda=serializer.validated_data["precio_moneda"],
        categoria_id=serializer.validated_data["categoria_id"],
        tipo_producto_id=serializer.validated_data.get("tipo_producto_id"),
    ),
    registrado_por=str(request.user.id),
    tallas=serializer.validated_data["tallas"],
)
```

**Cómo se aplicó:** la estrategia es **Extract Class**: los atributos cohesivos que viajaban como parámetros sueltos se agrupan en una nueva clase, `DatosComercialesPrenda`, inmutable (objeto de valor). El patrón concreto que materializa esta extracción es **Introduce Parameter Object**, que resuelve la lista larga de parámetros. No se trasladan reglas de negocio: la clase solo transporta datos. El adaptador de presentación conserva el contrato de entrada HTTP. Evidencia: commit `8232d49` y pruebas unitarias actualizadas.

### Refactorings SOLID 1 y 2: contratos y sustitución — antes y después

#### 1 · DIP — Extract Interface (Extraer Interfaz)

**Antes:** el servicio tipaba sus dependencias con las implementaciones Django, por lo que la capa de aplicación conocía la infraestructura:

```python
from apps.catalogo.infrastructure.repositories import (
    DjangoRepositorioCatalogo,
    DjangoRepositorioPrenda,
)

class ServicioCatalogo:
    def __init__(
        self,
        repo_prenda: DjangoRepositorioPrenda,
        repo_catalogo: DjangoRepositorioCatalogo,
    ) -> None:
        self.repo_prenda = repo_prenda
        self.repo_catalogo = repo_catalogo
```

**Después:** los contratos se declaran en el dominio y el servicio depende de esas abstracciones. Las instancias Django se conectan en el borde de presentación, en `_servicio()`:

```python
from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioPrenda

class ServicioCatalogo:
    def __init__(
        self,
        repo_prenda: RepositorioPrenda,
        repo_catalogo: RepositorioCatalogo,
    ) -> None:
        self.repo_prenda = repo_prenda
        self.repo_catalogo = repo_catalogo
```

**Cómo se aplicó:** la interfaz se extrajo de los métodos que `ServicioCatalogo` ya utilizaba sobre los adaptadores Django. Esos métodos se declararon como contratos ABC (`RepositorioPrenda` y `RepositorioCatalogo`) en `domain/repositorios.py`, y el constructor del servicio pasó a tipar sus dependencias con ellos. Así, la capa de aplicación ya no importa clases de infraestructura, las instancias Django se conectan en el borde de presentación (`_servicio()`), y el servicio puede probarse con repositorios en memoria. Evidencia: commit `739aab7`.

#### 2 · LSP — implementar y sustituir contratos

**Antes:** los repositorios concretos exponían sus operaciones sin declarar que cumplían un contrato común; el servicio solo aceptaba los tipos Django concretos.

**Después:** los contratos declaran las firmas como métodos abstractos y cada adaptador las implementa:

```python
class RepositorioPrenda(ABC):
    @abstractmethod
    def guardar(self, prenda: Prenda) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        raise NotImplementedError


class DjangoRepositorioPrenda(RepositorioPrenda):
    def guardar(self, prenda: Prenda) -> None:
        ...
```

**Cómo se aplicó:** primero se definieron los contratos abstractos con **Extract Interface**; después, `DjangoRepositorioPrenda` y `DjangoRepositorioCatalogo` los implementaron mediante herencia explícita. No se movió lógica de persistencia al contrato. Las pruebas de servicio usan repositorios en memoria y las de integración ejercitan los adaptadores Django; en conjunto aportan evidencia de que el servicio puede trabajar con ambas implementaciones. Evidencia: commit `739aab7`, dobles en `apps/catalogo/tests/test_services.py` y pruebas de integración del módulo.

## 4. Prácticas de Clean Code (evidencia 5+)

| # | Práctica | Dónde la aplicaste | Fragmento (ruta:líneas) |
| --- | --- | --- | --- |
| 1 | Nombres significativos (lenguaje ubicuo: `Prenda`, `cambiar_precio`, `EstadoPrenda`) | | |
| 2 | Funciones pequeñas, una sola responsabilidad | | |
| 3 | Sin valores mágicos (estados y monedas como enums/constantes, no strings sueltos) | | |
| 4 | Manejo de errores explícito (`ValidacionError` para datos comerciales inválidos y `RecursoNoEncontradoError` cuando falta una prenda) | | |
| 5 | DRY (conversión modelo↔entidad centralizada en mappers reutilizados) | | |

## 5. Mapa DDD del módulo (evidencia para la rúbrica)

| Elemento DDD | Clase(s) | Archivo |
| --- | --- | --- |
| Entidades | `Prenda`, `Categoria`, `TipoProducto` | `apps/catalogo/domain/prenda.py` |
| Objetos de Valor | `Dinero` (precio de la prenda), `EstadoPrenda` | `apps/compartido/domain/dinero.py`, `apps/compartido/domain/enums.py` |
| Agregado | `Prenda` (raíz, con precio `Dinero` y estado; métodos `activar`, `desactivar`, `cambiar_precio`) | `apps/catalogo/domain/prenda.py` |
| Fábrica | `PrendaFabrica` | `apps/catalogo/domain/prenda.py` |
| Repositorios (contratos) | `RepositorioPrenda`, `RepositorioCatalogo` (categorías y tipos). La separación en `RepositorioCategoria` y `RepositorioTipoProducto` está pendiente (refactor 4, ISP). | `apps/catalogo/domain/repositorios.py` |
| Repositorios (implementación) | `DjangoRepositorioPrenda`, `DjangoRepositorioCatalogo` | `apps/catalogo/infrastructure/repositories.py` |
| Servicio | `ServicioCatalogo` | `apps/catalogo/application/services.py` |
| Módulo | App `catalogo` con 4 capas | `apps/catalogo/` |

## 6. Definición de hecho

- [ ] Estilo de programación declarado y evidenciado (sección 2).
- [ ] Los 4 refactors SOLID implementados y evidenciados (sección 3). _Pendientes: refactor 3 (SRP, parcial) y refactor 4 (ISP)._
- [ ] 5+ prácticas Clean Code evidenciadas (sección 4).
- [ ] CRUD de prendas, categorías y tipos funciona (`uv run python manage.py check` + prueba manual de la API `api/prendas/`).
- [ ] Cambios funcionales dentro de `apps/catalogo`, con pruebas y documentación relacionadas cuando corresponda.
- [ ] Pull Request abierto hacia `dev` según [../flujo_git.md](../flujo_git.md).
