# Pagos - Laboratorios 9, 10 y 11

Contenido listo para copiar a Trello. Este archivo no afirma que el tablero haya sido modificado.

## Tarjeta

`Pagos - Laboratorios 9, 10 y 11`

## Checklist: tareas de implementación

- [x] Revisar convenciones.
- [x] Refactorizar dominio.
- [x] Crear excepciones.
- [x] Desacoplar servicio.
- [x] Implementar repositorio.
- [x] Limpiar views.
- [x] Aplicar cuatro estilos.
- [x] Aplicar Clean Code.
- [x] Agregar pruebas.
- [ ] Ejecutar SonarLint en el IDE.
- [x] Actualizar documentación.

## Checklist: escenarios de prueba

- [x] Registrar un pago pendiente.
- [x] Obtener un pago por ID.
- [x] Listar todos los pagos.
- [x] Filtrar pagos por `pedido_id`.
- [x] Aprobar un pago pendiente.
- [x] Rechazar un pago pendiente.
- [x] Impedir aprobar un pago ya aprobado.
- [x] Impedir aprobar un pago rechazado.
- [x] Impedir rechazar un pago ya rechazado.
- [x] Impedir rechazar un pago aprobado.
- [x] Rechazar monto cero.
- [x] Rechazar monto negativo.
- [x] Rechazar métodos no soportados.
- [x] Permitir efectivo sin referencia.
- [x] Exigir referencia para tarjeta.
- [x] Exigir referencia para transferencia.
- [x] Exigir referencia para Yape.
- [x] Devolver 404 para un pago inexistente.
- [x] Devolver 409 para una transición repetida.
- [x] No aceptar número de tarjeta, CVV ni PIN.
- [x] Conservar monto como `Decimal`, moneda, método, estado, referencia y fecha.
- [x] Probar el servicio con un repositorio en memoria, sin Django ORM.
- [x] Comprobar que las vistas no consultan `PagoModel.objects`.
- [x] Comprobar que no existen migraciones pendientes.
