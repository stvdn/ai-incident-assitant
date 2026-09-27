# 001 — Acceso síncrono o asíncrono a PostgreSQL

**Estado:** provisional; pendiente de la respuesta consolidada del Hito 0. **Contexto:** la Fase 1 tiene poca carga esperada y operaciones de PostgreSQL; el repositorio ya usa SQLAlchemy con `postgresql+psycopg` y funciones FastAPI síncronas.

## Opciones por evaluar

- **Sync:** flujo transaccional sencillo y compatible con el código actual; cada operación que espera la base ocupa un hilo. Con mucha concurrencia podrían saturarse hilos y/o conexiones, aumentando latencia.
- **Async:** la tarea puede ceder el control durante I/O con driver y sesión compatibles; exige disciplina async en las capas y pruebas y no elimina límites del pool ni de PostgreSQL.

## Decisión provisional y prueba

Continuar con sync en la primera versión **si** la investigación de drivers y una prueba de carga acorde al uso previsto lo respaldan. Antes de aprobar, comparar un candidato sync y otro async con SQLAlchemy, dibujar dos requests concurrentes y registrar ventaja, costo y alternativa descartada. Cambiar si la medición muestra saturación o si aparecen operaciones I/O concurrentes que justifiquen la complejidad. No atribuir la decisión solamente a que la AI todavía no existe.
