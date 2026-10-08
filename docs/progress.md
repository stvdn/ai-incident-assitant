# Progreso y próxima acción

**Corte inicial:** 26 de septiembre de 2026. Este registro combina la guía de Notion con una inspección de archivos; no se ejecutaron pruebas en ese corte. Actualizarlo cuando exista evidencia nueva. La fuente de verdad de la implementación es el código y sus verificaciones, no las casillas de Notion.

| Fase 1 | Estado | Evidencia actual / pendiente |
| --- | --- | --- |
| Hito 0 — Alcance y decisiones | Pendiente de aprobación | En Notion, la revisión 3 pidió una respuesta final consolidada, dos riesgos, drivers sync/async y trade-offs. Ver [plan](milestones/01-backend.md). |
| Hito 1 — FastAPI | Parcial, sin verificar | `backend/app/main.py` expone `GET /health`; existe `backend/test/test_health.py`. Falta demostrar inicio desde entorno limpio y test pasando. |
| Hito 2 — PostgreSQL | Parcial, sin verificar | `compose.yml` declara PostgreSQL 17, volumen y healthcheck; `backend/app/database.py` configura motor; existe prueba `SELECT 1`. Falta comprobar arranque, conexión y persistencia tras reinicio. |
| Hito 3 — Persistencia y migraciones | Migración verificada; sesión pendiente | Alembic reconstruye el esquema sobre PostgreSQL nuevo; falta el ciclo de vida de sesiones. |
| Hito 4 — Modelo y contrato | Completo (27 sep 2026) | Contrato Pydantic, modelo y restricciones PostgreSQL; 11 casos de esquema y 3 de restricciones. El usuario explicó el papel de ambas validaciones. Ver decisión 004. |
| Hito 5 — Endpoints de incidentes | Pendiente | No se observaron rutas de incidentes. |
| Hito 6 — Errores, config y logging | Pendiente | Existe lectura inicial de variables de entorno; faltan contrato de errores y logging. |
| Hito 7 — Estrategia de pruebas | Parcial, sin verificar | Existen pruebas de health y conexión; faltan cobertura de casos de uso, aislamiento y ejecución comprobada. |
| Hito 8 — CI | Pendiente | No se observó workflow de GitHub Actions. |

**Siguiente paso de aprendizaje:** continuar con la siguiente etapa; los criterios iniciales y CI conservan sus pendientes. No interpretar una rama como cierre automático de un hito.

## Registro de avances

Para cada hito cerrado, añadir fecha, cambio realizado, comando o prueba ejecutada, resultado y explicación del usuario. Si una verificación depende de PostgreSQL, indicar cómo se levantó y cómo se aislaron los datos. Mantener las decisiones en [decisions/](decisions/).

- **7 de octubre de 2026 — Versionado por etapas:** checkpoint `contract` verificado con `python -m pytest`: 16 casos aprobados sobre una base PostgreSQL temporal nueva. Las credenciales proceden del entorno local de pruebas y no se versionan. Se usa el intérprete del entorno uv existente; no se afirma instalación desde un entorno limpio.
