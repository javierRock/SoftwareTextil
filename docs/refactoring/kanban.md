# Kanban local de calidad

Consulta el [tablero de la entrega ampliada](tablero.md) y el [reparto actual](reparto/README.md).

Esta es la versión local para revisión. No se ha creado ni actualizado ningún proyecto remoto en esta etapa.

| TO-DO | CURRENT ITERATION | IN PROGRESS | FIX VALIDATION | DONE |
| --- | --- | --- | --- | --- |
| Q-02: desacoplar políticas de Django (3 h) | | | Q-01: compartir bloqueo de stock (2 h) | |
| Q-04: reproducir fallo entre guardado y contraseña (3 h) | | | Q-03: separar responsabilidades del login (2 h) | |
| | | | Q-05: rollback del agregado rol (2 h) | |
| S-04/S-05: revisar compatibilidad de StrEnum e imports | | | S-01/S-02/S-03: CSS y constantes (1 h total) | |

Q-01, Q-03 y Q-05 están implementados localmente y esperan revisión del usuario. Q-02 y Q-04 permanecen como backlog: no son parte del cambio local propuesto para integración.
Responsable de la implementación local de las tres tareas: carlosGCMP. Validación e integración: pendientes de revisión.

## Tarjetas listas para convertir en issues

### Q-01: Centralizar la obtención bloqueada del stock de pedidos

Etiqueta: `code smell`. Prioridad: media. Responsable propuesto: carlosGCMP. Duración: 2 h.

Problema: reservar y liberar repiten el orden de bloqueos, búsqueda y validación de stock.
Estrategia: Extract Method mediante un iterador que conserva el orden y la secuencia buscar–modificar–guardar.
Aceptación: reservas y liberaciones conservan cantidades, excepciones y persistencia; suites de pedidos y regresión aprobadas.

### Q-03: Separar la construcción de sesión y respuesta del login

Etiqueta: `code smell`. Prioridad: media. Responsable propuesto: carlosGCMP. Duración: 2 h.

Problema: login mezcla autenticación, auditoría, creación de sesión y serialización de la respuesta.
Estrategia: Extract Method. Mantener las claves de respuesta y las excepciones existentes.
Aceptación: login válido, inválido e inactivo siguen cubiertos; se verifica token, expiración y contrato de respuesta.

### Q-05: Garantizar rollback al guardar roles y permisos

Etiqueta: `bug`. Prioridad: alta. Responsable propuesto: carlosGCMP. Duración: 2 h.

Problema reproducido: si falla la sincronización de permisos, una creación o actualización del rol queda persistida parcialmente.
Estrategia: encapsular la persistencia del agregado en `transaction.atomic` en el adaptador Django.
Aceptación: dos pruebas de rollback fallan antes y pasan después; el nombre previo se conserva y no quedan roles nuevos parciales.

Antes de publicar, crear cada issue, colocar su URL en trazabilidad y usar su número real en el commit correspondiente.
