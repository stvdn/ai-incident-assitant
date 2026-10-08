# Fase 1 — Backend sólido: plan de los hitos 0 a 8

**Resultado de la fase:** registrar y consultar incidentes de forma confiable en PostgreSQL, sin depender de AI. Debe ser posible explicar el recorrido de cada request, las transacciones, validaciones, pruebas y decisiones. Fuente: [ruta guiada de Notion](https://app.notion.com/p/3e422251ed548196b882c8dc07a4be1f), consultada el 26 de septiembre de 2026. El estado verificable vive en [progress.md](../progress.md).

**Modo de trabajo:** seguir el apoyo gradual de [ai-incident-coach](../../.codex/skills/ai-incident-coach/SKILL.md): Codex muestra y explica un ejemplo funcional cuando el concepto es nuevo; el usuario revisa y modifica una parte pequeña antes de intentar escribir una solución independiente. Proponer un solo ejercicio a la vez y ayudar con código si se bloquea. Solo cerrar un hito con evidencia y explicación propia. Una solicitud directa de implementación del usuario prevalece sobre este modo. Cada decisión relevante se documenta con contexto, opciones, ventaja, costo, forma de validarla y condición para cambiarla.

## Secuencia y dependencias

`0 alcance → 1 aplicación mínima → 2 PostgreSQL → 3 persistencia/migraciones → 4 contrato de Incident → 5 endpoints → 6 errores/config/logging → 7 pruebas completas → 8 CI`.

Las pruebas empiezan en el Hito 1 y acompañan los siguientes; el Hito 7 consolida su estrategia. La documentación de ejecución y decisiones se actualiza durante el trabajo. No adelantar AI, RAG, agentes ni colas en esta fase. No agregar Update/Delete: los requisitos son crear y leer.

## Hito 0 — Alcance y decisiones iniciales

**Entregable:** una nota breve, en palabras del usuario, que cubra responsabilidad de la API en Fase 1, exclusiones, módulos y sus responsabilidades, criterio sync/async y condiciones observables para afirmar que un incidente fue creado. No escribir código para este ejercicio.

- [ ] Precisar operaciones: crear un incidente, consultarlo por id y listar con paginación. Explicar por qué Update/Delete no están incluidos.
- [ ] Delimitar rutas/API, dominio/casos de uso y acceso a datos sin un módulo `shared` genérico sin consumidores.
- [ ] Comparar dos requests concurrentes esperando PostgreSQL bajo sync y async; identificar qué hilo/tarea espera y qué recurso puede saturarse.
- [ ] Investigar un driver sync y uno async, su compatibilidad con SQLAlchemy y el efecto sobre código y pruebas. Registrar la decisión provisional en [001-sync-vs-async.md](../decisions/001-sync-vs-async.md).
- [ ] Distinguir validación, commit exitoso y entrega de respuesta HTTP; explicar qué ocurre si la respuesta falla después del commit.
- [ ] Formular dos riesgos distintos: condición que los provoca, impacto observable y prueba o medición.
- [ ] Para alcance Create/Read, ausencia de `shared` y elección sync/async, escribir ventaja, costo y alternativa descartada.

**Evidencia para cerrar:** respuesta final consolidada con los cinco apartados, dos riesgos, tres trade-offs y sin contradicciones sobre concurrencia. La revisión 3 de Notion la dejó cerca de aprobar, pero todavía pendiente; no inferir aprobación por el código existente.

## Hito 1 — Esqueleto ejecutable de FastAPI

**Preguntas:** ¿cuál es el punto de entrada?, ¿cómo separar creación de app, rutas y configuración?, ¿qué respuesta mínima prueba que el proceso está vivo?, ¿cómo ejecutarlo desde un entorno limpio?

- [ ] Revisar la estructura y el `create_app()` existentes en `backend/app/main.py`; ajustar solo si una responsabilidad concreta lo requiere.
- [ ] Documentar instalación y arranque reproducible en el README cuando se hayan comprobado.
- [ ] Mantener una comprobación HTTP mínima (`GET /health`) con respuesta y status explícitos.
- [ ] Ejecutar la prueba automatizada de la ruta desde un entorno limpio y registrar el resultado.

**Evidencia para cerrar:** servidor arranca con instrucciones documentadas, `/health` responde, test pasa y el usuario explica la estructura sin apelar a un tutorial. **Estado observado:** hay ruta y test, pero no se verificó su ejecución.

## Hito 2 — PostgreSQL reproducible con Docker Compose

**Preguntas:** ¿qué variables necesita el contenedor?, ¿qué debe sobrevivir a un reinicio?, ¿cómo distinguir proceso iniciado de base lista?, ¿qué valores pueden estar en Git?

- [ ] Completar y comprobar el flujo `compose.yml` + `.env.example` sin versionar contraseña real.
- [ ] Verificar el healthcheck y que la aplicación se conecte mediante variables de entorno, con error claro si faltan.
- [ ] Comprobar que los datos sobreviven a un reinicio normal del contenedor y volumen.
- [ ] Documentar inicio, parada y verificación de conexión; evitar secretos en comandos o logs compartidos.

**Evidencia para cerrar:** arranque reproducible, conexión comprobada, persistencia tras reinicio y explicación de «contenedor iniciado» frente a «PostgreSQL listo». **Estado observado:** Compose, healthcheck y prueba `SELECT 1` existen, sin ejecución verificada.

## Hito 3 — Persistencia y migraciones

**Preguntas:** ¿qué hace SQLAlchemy y qué hace Alembic?, ¿dónde empieza/termina la transacción?, ¿cómo se recupera una sesión tras error?, ¿cómo recrear esquema desde cero?

- [ ] Definir la sesión de base de datos y su ciclo de vida por request/caso de uso.
- [ ] Crear configuración Alembic y una migración inicial para el esquema aprobado en Hito 4; coordinar los hitos 3 y 4 sin fijar campos antes del contrato.
- [ ] Definir commit, rollback y cierre de sesión; evitar commits escondidos en varias capas.
- [ ] Aplicar migraciones sobre una base vacía y comprobar el esquema resultante.
- [ ] Probar que una operación fallida hace rollback y que la siguiente operación puede usar una sesión válida.

**Evidencia para cerrar:** migración versionada y reproducible desde cero, transacciones recuperables tras fallo y explicación del límite transaccional.

## Hito 4 — Modelo de dominio y contrato de API

**Preguntas:** ¿qué entrega el cliente y qué controla el servidor?, ¿qué puede ser nulo en Fase 1?, ¿qué estados son válidos?, ¿qué tamaño/formato aceptar?, ¿por qué separar entrada, persistencia y salida?

- [ ] Clasificar los campos propuestos: `id`, `job_name`, `status`, `log`, `exit_code`, `created_at`, `analysis_status`, `probable_cause`, `evidence`, `suggested_actions`.
- [ ] Definir tipos, obligatoriedad, defaults y estados válidos; precisar qué campos de análisis quedan sin valor hasta Fase 2.
- [ ] Establecer límites razonables de texto y log y casos inválidos antes de programar.
- [ ] Diseñar contratos explícitos de creación y respuesta; decidir representación de fechas, ids y campos opcionales.
- [ ] Traducir el contrato a modelo SQLAlchemy y migración, comprobando que no puedan persistirse estados imposibles.

**Evidencia para cerrar:** ejemplo válido e inválidos, esquemas de entrada/salida, defaults ubicados en la capa correcta y persistencia alineada con la migración.

## Hito 5 — Crear, consultar y listar incidentes

**Orden:** `POST /incidents` → `GET /incidents/{id}` → `GET /incidents` con paginación.

- [ ] Para cada ruta definir entrada, status/respuesta de éxito, errores esperados, reparto entre caso de uso y acceso a datos, y una prueba que demuestre el comportamiento.
- [ ] En creación, confirmar transacción antes de responder y devolver un identificador consultable; distinguir commit de entrega HTTP.
- [ ] En consulta por id, definir id inválido e inexistente sin filtrar detalles internos.
- [ ] En listado, definir `limit`/`offset` o alternativa, máximos, valores cero/negativos, orden estable y metadata necesaria para el cliente.
- [ ] Comprobar que la lectura recupera datos realmente persistidos y que la paginación no duplica u omite registros en un conjunto estable.

**Evidencia para cerrar:** los tres endpoints cumplen sus contratos, casos de error previstos y pruebas con PostgreSQL para persistencia y orden. No implementar operaciones extra por llamarlas «CRUD».

## Hito 6 — Errores, configuración y logging

- [ ] Definir una forma coherente de error HTTP y distinguir entradas inválidas, recursos inexistentes y fallos del servidor.
- [ ] Centralizar configuración necesaria y hacer que falte pronto y con mensaje accionable cuando no existe un valor requerido.
- [ ] Definir eventos de log estructurados y campos útiles como evento, incident_id y correlation_id cuando aplique.
- [ ] Evitar API keys, contraseñas, logs sensibles del usuario y detalles internos en respuestas y logs.
- [ ] Probar al menos un error de cada categoría y verificar que los logs puedan consultarse por evento/incidente.

**Evidencia para cerrar:** errores equivalentes tienen forma consistente, secretos no aparecen y el registro es útil sin interpretar texto libre.

## Hito 7 — Pruebas unitarias y de integración

- [ ] Clasificar validación, creación exitosa, id inexistente, rollback, paginación/orden y persistencia real como prueba unitaria, integración o ambas, justificando la elección.
- [ ] Ejecutar unitarias sin infraestructura externa con dependencias sustituidas cuando corresponda.
- [ ] Ejecutar integración contra PostgreSQL real; aislar y limpiar datos de cada caso.
- [ ] Cubrir rutas y fallos relevantes sin escribir pruebas que solo repitan la implementación.
- [ ] Documentar cómo preparar servicios y ejecutar ambas suites desde cero.

**Evidencia para cerrar:** suite repetible, fallos detectables y explicación concreta de qué defecto captura cada prueba. SQLite no sustituye aquí la prueba de comportamiento PostgreSQL.

## Hito 8 — Integración continua

- [ ] Definir verificaciones que deben bloquear un merge: instalación, pruebas y otras comprobaciones realmente necesarias.
- [ ] Crear workflow de GitHub Actions para push/PR con servicio PostgreSQL si la suite lo requiere.
- [ ] Inyectar variables de prueba sin secretos reales; esperar readiness para evitar carreras.
- [ ] Comprobar un run exitoso y que un fallo simulado o real produzca información accionable.

**Evidencia para cerrar:** el pipeline corre automáticamente, ejecuta las mismas pruebas documentadas y no contiene secretos. No marcarlo completo solo por haber creado un archivo YAML.

## Salida de la Fase 1

Se pueden crear, consultar y listar incidentes persistidos; levantar el entorno y reconstruir su esquema desde cero; ejecutar pruebas locales y CI; y explicar validación, transacciones, errores, configuración, observabilidad básica y decisiones técnicas. El progreso se registra en [progress.md](../progress.md) con fecha y pruebas. El siguiente trabajo es [Fase 2 — AI](02-ai-integration.md).
