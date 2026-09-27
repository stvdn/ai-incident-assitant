# 002 — PostgreSQL como persistencia

**Estado:** elegido en el alcance del proyecto; falta validar el flujo completo. **Contexto:** los incidentes necesitan persistencia, consultas, orden estable y transacciones. La hoja de ruta considera pgvector para RAG, pero la Fase 1 no necesita vectores.

## Razones y costo

PostgreSQL permite trabajar con transacciones y restricciones reales desde el inicio y mantener la misma base en pruebas de integración. Cuesta levantar y cuidar un servicio adicional y aislar datos de pruebas. SQLite puede servir para pruebas muy acotadas, pero no sustituye las de integración de este proyecto por diferencias de semántica. La elección no obliga a activar pgvector todavía.

## Validación

Comprobar Compose, readiness, persistencia tras reinicio, migración desde base vacía, rollback y pruebas de integración repetibles. Revisar índices cuando exista el patrón real de búsqueda y paginación; documentar la justificación de cada índice.
