# Informe de refactorización local

Este informe describe la primera entrega. La [comparación ampliada](resultado-ampliado.md) registra la validación y los cambios posteriores.

## Alcance de la entrega propuesta

Base `a312d0a` de `dev`. Rama local `refactor/code-quality`.
Se seleccionaron Q-01, Q-03 y Q-05 como primera entrega verificable. Q-02 y Q-04 son oportunidades de evolución pendientes, con sus riesgos y pruebas propuestas en el inventario.

El análisis SonarQube añadió tres correcciones sencillas: un fallback CSS que duplicaba `background`, una referencia a modelo repetida y un prefijo de rutas repetido. Se conservan cinco alertas para revisión: dos sobre iteración de `StrEnum` y tres sobre imports de configuración Django. SonarQube 9.9.7 avisa que trata Python 3.11 como 3.10; esto limita la interpretación de `StrEnum` y debe consignarse en la revisión.

La primera importación de cobertura detectó rutas absolutas del host incompatibles con `/usr/src` del scanner. Se conservaron sus logs y se repitieron ambos análisis usando una copia XML con raíz `/usr/src/apps`; las métricas finales provienen de las ejecuciones corregidas.

## Cambios realizados

### Pedidos: eliminar conocimiento duplicado

Antes, `_reservar` y `_liberar` contenían el mismo algoritmo para ordenar variantes, bloquear filas y detectar stock inexistente. Ahora `_stocks_bloqueados` concentra ese conocimiento. Cada operación mantiene su comportamiento específico de reserva o liberación y su persistencia.

El iterador entrega un elemento por vez: no adelanta la búsqueda de todas las variantes. Esto conserva la secuencia de consultas y escrituras y el orden de bloqueo que reduce interbloqueos. Las transacciones existentes del servicio se mantienen.

### Usuarios: separar responsabilidades del login

`login` mantiene validación y auditoría y delega la creación/persistencia de sesión en `_crear_sesion`. `_respuesta_login` arma el contrato de salida. No cambia la API: token, usuario, nombre, email, rol y expiración conservan sus claves y origen.

Las pruebas existentes cubren usuarios activos, inactivos e inexistentes y contraseñas incorrectas. La verificación del contrato de respuesta se amplió.

### Roles: persistencia atómica del agregado

Dos pruebas nuevas simulan un fallo de sincronización de permisos. Antes del cambio, ambas fallan: el rol nuevo permanece o el nombre actualizado no se revierte. La salida real se conserva en `evidencias/antes/rollback-rojo.txt`.

El adaptador Django ahora delimita `guardar` con `transaction.atomic`. Un fallo revierte tanto el rol como las operaciones de permisos. El contrato del dominio permanece igual; no se trasladaron dependencias Django al dominio.

## Validación

Consultar `comparacion.md` y los archivos de evidencia originales. Ruff es complementario; sus reglas no equivalen a las reglas de SonarQube. No se declara saneado todo el proyecto por corregir tres hallazgos.

## Revisión y publicación

Revisar el diff local y los reportes. Las URLs de GitHub Projects, Issues y commits remotos quedan pendientes por la decisión de trabajar localmente. Las tarjetas están en `kanban.md`. El usuario debe aprobar la publicación y revisar la integración antes de considerar un despliegue a producción.
