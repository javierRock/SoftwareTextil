# Guías de Trabajo por Integrante

Cada integrante tiene una guía con el alcance de su módulo, los objetivos de refactor detectados en el código y las secciones de **evidencia** que exige la rúbrica del proyecto final (`docs/labFinal.pdf`): estilo de programación, 5+ prácticas de Clean Code, 3+ principios SOLID y elementos DDD.

| Guía | Integrante | Módulo | Rama |
| --- | --- | --- | --- |
| [carlos-autenticacion.md](carlos-autenticacion.md) | Carlos | Autenticación y Roles | `feature/autenticacion-carlos` |
| [lizzy-catalogo.md](lizzy-catalogo.md) | Lizzy | Catálogo | `feature/catalogo-lizzy` |
| [alejandro-inventario.md](alejandro-inventario.md) | Alejandro | Inventario | `feature/inventario-alejandro` |
| [angelo-pedidos.md](angelo-pedidos.md) | Angelo | Pedidos (y Carrito) | `feature/pedidos-angelo` |
| [javier-pagos.md](javier-pagos.md) | Javier | Pagos | `feature/pagos-javier` |

## Cómo usar tu guía

1. Haz checkout de tu rama (`git checkout feature/<modulo>-<tu-nombre>`).
2. Declara tu **estilo de programación** en la sección correspondiente de tu guía (cada integrante usa un estilo distinto — coordinen para no repetir).
3. Implementa los objetivos de refactor de tu módulo aplicando tu estilo.
4. Completa las tablas de evidencia (práctica/principio → descripción → fragmento de código con ruta y líneas).
5. Abre tu Pull Request a `dev` siguiendo [../flujo_git.md](../flujo_git.md).

## Estilos de programación de referencia

(Basados en *Exercises in Programming Style*, C. V. Lopes.) Cada integrante elige **uno distinto**:

| Estilo | Idea central |
| --- | --- |
| Things (OOP) | Todo se modela como objetos con estado encapsulado y mensajes |
| Pipeline | Funciones puras encadenadas: la salida de una es la entrada de la siguiente |
| Cookbook | Procedimientos paso a paso que comparten estado del módulo |
| Persistent Tables | Los datos viven en tablas; la lógica consulta y transforma relaciones |
| Declared Intentions | Contratos explícitos: type hints, validación de tipos/argumentos declarada |
| Constructivist | Ante errores, valores por defecto razonables: la ejecución continúa |
| Tantrum | Ante errores, fallar rápido y ruidoso: excepciones inmediatas |
| Passive-Aggressive | Los errores se propagan hacia arriba; solo el nivel superior los maneja |
| RESTful | Interacción por recursos, verbos uniformes y estado transferido |
| Lazy Rivers | Flujos de datos perezosos (generadores) que procesan bajo demanda |

## Prácticas Clean Code de referencia (elige y evidencia 5+)

1. Nombres significativos y pronunciables (lenguaje ubicuo en español).
2. Funciones pequeñas que hacen una sola cosa.
3. Sin números ni cadenas mágicas (constantes/enums con nombre).
4. Comentarios solo donde aportan (el código se explica solo).
5. Manejo de errores explícito (excepciones de dominio, no códigos de retorno).
6. DRY: extraer duplicación a funciones/módulos comunes.
7. Formato consistente (PEP 8) y organización vertical del código.
8. Evitar efectos secundarios ocultos en funciones.

## Principios SOLID (elige y evidencia 3+)

| Principio | Cómo se ve en este proyecto |
| --- | --- |
| **S**RP | Views delgadas: la lógica vive en `application/services.py`, no en `presentation/` |
| **O**CP | Extender con nuevas clases (permisos, métodos de pago, tipos de movimiento) sin modificar las existentes |
| **L**SP | Los repositorios concretos son sustituibles por sus contratos ABC sin romper a los servicios |
| **I**SP | Contratos de repositorio pequeños y específicos por agregado, no interfaces gigantes |
| **D**IP | Los servicios dependen de los ABCs de `domain/repositorios.py`, nunca de clases `Django*` concretas |
