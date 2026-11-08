# 002 — PostgreSQL como persistencia

**Estado:** implementado y flujo completo verificado al 12 de octubre de 2026. **Contexto:** los incidentes necesitan persistencia, consultas, orden estable y transacciones. La hoja de ruta considera pgvector para RAG, pero la Fase 1 no necesita vectores.

## Razones y costo

PostgreSQL permite trabajar con transacciones y restricciones reales desde el inicio y mantener la misma base en pruebas de integración. Cuesta levantar y cuidar un servicio adicional y aislar datos de pruebas. SQLite puede servir para pruebas muy acotadas, pero no sustituye las de integración de este proyecto por diferencias de semántica. La elección no obliga a activar pgvector todavía.

## Validación

Se verificaron Compose, readiness, migraciones sobre volumen nuevo, API real y persistencia tras reinicio el 12 de octubre de 2026. Las pruebas de rollback e integración y el run exitoso de CI están registrados en `docs/progress.md`. El usuario explicó la responsabilidad del volumen y del healthcheck. El proyecto Compose de pruebas tiene nombre independiente para separar redes y ciclo de vida.

Comprobar Compose, readiness, persistencia tras reinicio, migración desde base vacía, rollback y pruebas de integración repetibles. Revisar índices cuando exista el patrón real de búsqueda y paginación; documentar la justificación de cada índice.
