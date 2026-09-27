# Fase 4 — Tool calling

**Entrada:** servicios de consulta y, cuando aplique, RAG funcional. **Resultado:** el modelo puede pedir consultas controladas; la aplicación conserva el control de su ejecución.

- [ ] Implementar primero como servicios Python funciones candidatas: `get_incident`, `get_job_history`, `get_related_failures`, `search_runbooks`, `get_recent_incidents`.
- [ ] Definir esquemas estrictos de argumentos y validar toda salida del modelo antes de ejecutar.
- [ ] Limitar herramientas y datos accesibles; registrar cada invocación y su correlación con el incidente.
- [ ] Probar herramienta equivocada, argumentos inválidos, límites y fallos de cada servicio.

**Evidencia de cierre:** escenarios positivos y negativos reproducibles, sin ejecución de acciones no permitidas. Evaluar frameworks de agentes solo después de comprender y medir estas piezas.
