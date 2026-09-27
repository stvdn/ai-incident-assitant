# Fase 5 — Procesamiento por eventos

**Entrada:** análisis funcional y evidencia de que su latencia o volumen hace inconveniente mantener abierto el request HTTP. No introducir una cola antes de ese problema.

- [ ] Medir latencia/volumen y documentar el umbral que motiva separar API y worker.
- [ ] Elegir RabbitMQ o cola respaldada por Redis; distinguir el evento `IncidentCreated` de un comando de análisis.
- [ ] Publicar trabajo y procesarlo en worker independiente, con estados `pending`, `processing`, `completed`, `failed`.
- [ ] Implementar correlation ID, retries con backoff, idempotencia y tratamiento de mensajes fallidos.
- [ ] Probar entrega duplicada, fallo del worker y recuperación sin análisis duplicado.

**Evidencia de cierre:** la API responde sin esperar el LLM, el estado converge, los duplicados son inocuos y los fallos pueden inspeccionarse y recuperarse. Explicar at-least-once delivery y consistencia eventual. Kafka se evalúa después, solo si aparece una necesidad concreta.
