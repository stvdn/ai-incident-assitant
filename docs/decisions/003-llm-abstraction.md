# 003 — Abstracción del analizador LLM

**Estado:** decisión de diseño prevista para Fase 2; aún no implementada. **Contexto:** el backend debe guardar y consultar incidentes sin depender de un proveedor de modelos, y las pruebas normales deben ser deterministas.

## Dirección propuesta

Definir `IncidentAnalyzer` como contrato de aplicación para convertir datos de incidente en un análisis estructurado. Un adaptador del proveedor manejará transporte, timeouts y detalles de su API. El dominio y la persistencia consumirán el contrato validado, no la respuesta cruda del proveedor.

## Costo y validación

Agrega una interfaz y mapeo de errores, que solo se justifican si reducen el acoplamiento real y facilitan pruebas. Validar con un fake que cubra éxito, timeout, error y salida mal formada, y comprobar que la persistencia y API funcionan sin credenciales reales. Evitar una jerarquía de adaptadores hasta que exista un segundo caso que la necesite.


## Implementation evidence - 27 October 2026

Implemented IncidentAnalyzer as a Protocol with an immutable AnalysisInput snapshot, AnalysisResult validation, and provider-neutral timeout/rate-limit/failure exceptions. The service releases its read transaction before provider I/O, then commits a successful result as a separate history row. Failed attempts leave no analysis row; existing incidents remain intact. HTTP POST and paginated GET are implemented under /incidents/{incident_id}/analyses. User reports the full suite passing; API tests use a fake provider and real test PostgreSQL. The real adapter is pending, so Phase 2 is not complete.


## Gemini adapter and live demonstration - 27 October 2026

User selected Gemini for free-tier development. GeminiAnalyzer uses google-genai structured JSON output and local Pydantic validation; evidence must be a verbatim substring of the incident log. System instructions are separate from untrusted incident JSON. The HTTP client uses a 30000 ms timeout and one attempt, and is closed after the request. No automatic retry, token accounting or cost estimation is implemented. HTTP errors map to controlled 502/503/504 responses. Failed attempts are not persisted; dedicated provider-failure log events are a remaining observability improvement. Confidence is explicitly uncalibrated and prompt separation is not a security guarantee.

The user supplied a completed live response (model reported as gemini-3.5-flash-lite, latency 1546 ms) and confirmed GET returned 200 with the saved analysis. This records an observed demonstration, not a guarantee of model availability. README now documents setup, API examples, limitations and quota considerations.
