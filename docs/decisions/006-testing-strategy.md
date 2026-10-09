# 006 — Estrategia de pruebas e aislamiento

**Fecha:** 9 de octubre de 2026. **Estado:** implementado, verificado por el usuario y explicado.

## Contexto y decisión

Separar las 33 pruebas mediante marcadores pytest registrados con `--strict-markers`: 18 `unit` de contratos, configuración y health, sin infraestructura externa; 15 `integration` de conexión, restricciones, transacciones y API contra PostgreSQL real. Los casos HTTP permanecen en integración según sus dependencias actuales. El nombre del marcador unit identifica la suite sin infraestructura, incluyendo la comprobación HTTP de health.

Preparar PostgreSQL mediante `compose.test.yml` (puerto 5433, tmpfs) y reconstruir el esquema con Alembic. Una fixture automática exige `POSTGRES_DB=incidents_test` antes de ejecutar integración. Este control verifica el nombre configurado, no la identidad del servidor.

Usar UUID/nombres únicos y limpieza selectiva en `finally` para las filas confirmadas. Las restricciones y el rollback se comprueban con transacciones reales. La lectura desde otra sesión verifica que un commit hace persistente el incidente. Paginación exige tabla vacía y se ejecuta secuencialmente; prueba prioridad de fecha, desempate por UUID, páginas consecutivas y agotamiento.

## Ventaja, costo y alternativas

Las unitarias permiten feedback sin Docker. PostgreSQL real comprueba restricciones y transacciones que SQLite o mocks no demostrarían. Mantener limpieza explícita permite verificar commits reales; envolver todos los casos en una transacción externa con rollback podría ocultar la ausencia de commit si la lectura compartiera esa transacción.

El costo es preparar PostgreSQL y cuidar la limpieza. Una interrupción abrupta puede dejar filas; recrear el contenedor de pruebas elimina su almacenamiento temporal. El aislamiento actual no permite ejecutar la paginación concurrentemente con otros escritores. Si se necesita paralelismo, evaluar bases o esquemas independientes por worker antes de incorporarlo.

## Evidencia

El usuario confirmó 18 unitarias aprobadas, 15 de integración aprobadas y la prueba de paginación modificada aprobada. Compartió el bloqueo esperado en setup al seleccionar `POSTGRES_DB=incidents`. Confirmó además 18 unitarias y 33 casos totales aprobados tras instalar en un entorno Python nuevo y recrear la base de pruebas con migraciones. Los resultados satisfactorios son reportados por el usuario, sin salida adjunta.

El usuario explicó lectura desde otra sesión, limpieza aun cuando falla una aserción, riesgo de borrar filas de otra prueba y prioridad de fecha. Los comandos están documentados en README. CI corresponde al Hito 8 y todavía no está verificado.
