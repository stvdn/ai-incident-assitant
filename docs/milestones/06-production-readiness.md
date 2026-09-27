# Fase 6 — Evals y preparación para operar

**Entrada:** funciones principales implementadas. **Resultado:** calidad, rendimiento y fallos medibles.

- [ ] Crear dataset pequeño de incidentes conocidos y criterios de diagnóstico esperado.
- [ ] Evaluar recuperación de runbooks y calidad de respuestas del LLM por separado.
- [ ] Medir latencia, costo aproximado por análisis, errores y retries.
- [ ] Separar health de readiness cuando las dependencias lo requieran y agregar observabilidad básica.
- [ ] Documentar amenazas, límites, sesgos de evaluación y operaciones de recuperación.

**Evidencia de cierre:** evaluaciones reproducibles, métricas consultables y documentación operativa. AWS puede añadirse después del MVP con FastAPI en contenedor, RDS, S3 si hay documentos, secretos y permisos IAM mínimos, logs y despliegue desde CI. Kubernetes no forma parte del criterio de cierre.
