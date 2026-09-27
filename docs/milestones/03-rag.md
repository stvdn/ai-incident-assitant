# Fase 3 — RAG sobre runbooks

**Entrada:** analizador funcional con LLM. **Problema:** las recomendaciones deben apoyarse en documentación de operación, no solo en conocimiento general del modelo.

- [ ] Definir fuentes y formato de runbooks; conservar origen y versión.
- [ ] Implementar ingestión, chunking y embeddings con metadata.
- [ ] Guardar vectores en pgvector y recuperar fragmentos relevantes mediante búsqueda por similitud.
- [ ] Enviar contexto recuperado al analizador y guardar qué documentos/chunks se usaron.
- [ ] Mostrar referencias/evidencia en el resultado y evaluar relevancia y casos de contexto irrelevante.

**Evidencia de cierre:** un conjunto pequeño de preguntas/incidentes conocidos muestra recuperación útil, trazabilidad de fuentes y una evaluación repetible. Distinguir explícitamente búsqueda semántica de generación.
