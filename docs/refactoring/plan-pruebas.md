# Plan de pruebas y refactorización

La revisión ampliada añade una regresión de catálogo que verifica que un tipo inexistente no modifica ni guarda la prenda. En el cliente HTTP, una solicitud multipart comprueba que el cuerpo y el encabezado se delegan al navegador y que el estado 204 devuelve `null`. Las pruebas del backend y frontend se enlazan desde [la comparación](resultado-ampliado.md).

| Hallazgo | Valores / preparación | Acción | Resultado esperado |
| --- | --- | --- | --- |
| Q-01 | Detalles desordenados, stock válido, inventario ausente y variante inexistente | Generar y cancelar pedido | Mismos totales y estados; bloqueos ordenados; mismas excepciones; rollback cuando corresponda |
| Q-02 | Contraseñas válida, inválida y repetida; usuario activo e inactivo | Crear usuario, cambiar contraseña y autenticar | Mismos errores y resultados; comprobar llamadas a política y auditoría |
| Q-03 | Credenciales correctas e incorrectas; rol y sesión existentes | Login | Mismas claves de respuesta; sesión de ocho horas y registro correcto del intento |
| Q-04 | Repositorio que falla al guardar contraseña | Crear usuario | Ningún usuario parcial persistido después de la corrección |
| Q-05 | Fallo durante sincronización de permisos | Guardar rol y permisos | Conservar estado previo completo después del rollback |

Usar Arrange–Act–Assert y nombres consistentes con el componente. Ejecutar primero las suites existentes de usuarios y pedidos. Agregar casos que falten y conservar salida antes/después. No fabricar una fase roja para un refactoring que ya conserva comportamiento.
