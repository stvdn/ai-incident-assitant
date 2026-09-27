# Fase 2 — Integración con AI

**Entrada:** Fase 1 cerrada y backend capaz de persistir incidentes sin AI. **Resultado:** analizar un incidente con un LLM y guardar una respuesta estructurada. Esta fase contribuye al MVP publicable; RAG y agentes quedan fuera.

- [ ] Definir la interfaz `IncidentAnalyzer` y separar dominio, proveedor y representación HTTP. Ver [decisión 003](../decisions/003-llm-abstraction.md).
- [ ] Enviar log y metadata como datos no confiables; separar instrucciones del sistema.
- [ ] Validar una salida con `probable_cause`, `confidence`, `evidence` y `suggested_actions`; definir comportamiento ante salida inválida.
- [ ] Persistir análisis y registrar modelo, estado, latencia y, si es posible, consumo/costo aproximado.
- [ ] Manejar timeout, rate limit y errores del proveedor sin exponer secretos; definir retries solo donde sean seguros.
- [ ] Probar caso exitoso y fallos con fake/mock del proveedor, sin gastar llamadas reales en la suite normal.

**Evidencia de cierre:** análisis recuperable desde PostgreSQL, contrato estructurado comprobado, pruebas de error y README con límites, costos y ejemplo. Aprendizajes: prompts de tarea, context windows, tokens, rate limits, timeouts y seguridad frente a instrucciones incrustadas en logs.
