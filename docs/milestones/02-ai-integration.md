# Fase 2 — Integración con AI

**Entrada:** Fase 1 cerrada y backend capaz de persistir incidentes sin AI. **Resultado:** analizar un incidente con un LLM y guardar una respuesta estructurada. Esta fase contribuye al MVP publicable; RAG y agentes quedan fuera.

- [x] Definir la interfaz `IncidentAnalyzer` y separar dominio, proveedor y representación HTTP. Ver [decisión 003](../decisions/003-llm-abstraction.md).
- [x] Enviar log y metadata como datos no confiables; separar instrucciones del sistema.
- [x] Validar una salida con `probable_cause`, `confidence`, `evidence` y `suggested_actions`; definir comportamiento ante salida inválida.
- [x] Persistir análisis y registrar modelo, estado, latencia y, si es posible, consumo/costo aproximado.
- [x] Manejar timeout, rate limit y errores del proveedor sin exponer secretos; definir retries solo donde sean seguros.
- [x] Probar caso exitoso y fallos con fake/mock del proveedor, sin gastar llamadas reales en la suite normal.

**Evidencia de cierre:** análisis recuperable desde PostgreSQL, contrato estructurado comprobado, pruebas de error y README con límites, costos y ejemplo. Aprendizajes: prompts de tarea, context windows, tokens, rate limits, timeouts y seguridad frente a instrucciones incrustadas en logs.


## Verified status - 27 October 2026

Phase 2 implementation is complete. Direct local verification: test Compose service started with --wait; both Alembic migrations applied to a fresh temporary test database; alembic check reported no new upgrade operations; full suite passed 69 tests in 72.44 seconds. Normal tests use mocked providers and real PostgreSQL for integration. Live Gemini POST and GET success are user-reported, with the completed response supplied in chat. README documents configuration, examples, errors and limitations. Explanations were provided directly under the user's requested accelerated workflow; no independent interview assessment is claimed. Token/cost accounting and dedicated provider-failure events remain optional improvements. Publication and CI for these uncommitted changes remain pending.
