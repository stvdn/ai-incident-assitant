# Proyecto y alcance

Fuente original: [AI Incident Assistant — Backend + AI + Event-Driven](https://app.notion.com/p/3e422251ed5481e3a44ef87835a8425e), consultada el 26 de septiembre de 2026 (última edición indicada: 23 de septiembre). La guía de aprendizaje de Fase 1 está incorporada en [01-backend.md](milestones/01-backend.md).

## Problema y objetivo

Un usuario envía datos de un job, proceso batch o servicio fallido. El asistente registra el incidente, analiza los logs y devuelve causa probable, evidencia y acciones sugeridas. El portfolio debe demostrar diseño de API, persistencia, pruebas, operación de un backend y aplicación práctica de LLMs. Roles objetivo: Python/Backend Software Engineer desde las primeras fases; AI Backend y Applied AI Engineer tras la integración con LLM y RAG.

**Principio de evolución:** no agregar una tecnología para mostrarla en el CV. Antes de incluirla, precisar el problema que resuelve, el costo o trade-off que introduce y una prueba o escenario que demuestre su utilidad.

## Alcance por fase

| Fase | Resultado | Plan |
| --- | --- | --- |
| 1. Backend | Crear, consultar y listar incidentes en PostgreSQL sin AI; pruebas y CI. | [01-backend.md](milestones/01-backend.md) |
| 2. AI | Análisis con LLM, salida estructurada y persistida, desacoplado del proveedor. | [02-ai-integration.md](milestones/02-ai-integration.md) |
| 3. RAG | Recomendaciones fundamentadas en runbooks recuperados con pgvector. | [03-rag.md](milestones/03-rag.md) |
| 4. Tool calling | Consultas controladas mediante funciones de la aplicación. | [04-tool-calling.md](milestones/04-tool-calling.md) |
| 5. Event-driven | Cola y worker cuando la latencia o carga justifique separar el análisis de HTTP. | [05-event-driven.md](milestones/05-event-driven.md) |
| 6. Production readiness | Evals, métricas, observabilidad, documentación de límites. | [06-production-readiness.md](milestones/06-production-readiness.md) |

Stack inicial previsto: Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose, pytest, GitHub Actions y API de LLM. Kubernetes, Kafka, Terraform complejo, microservicios múltiples, service mesh, entrenamiento desde cero, PyTorch avanzado y MLOps distribuido quedan fuera del alcance inicial. AWS se considera después del MVP: contenedor de FastAPI, RDS, S3 solo si hay documentos, secretos, logs, despliegue e IAM adecuados.

## MVP publicable

Se puede crear un incidente por API y recuperarlo desde PostgreSQL; un LLM analiza su log mediante salida estructurada; el análisis se persiste; existen pruebas unitarias y de integración, CI automática y ejecución local reproducible con Docker Compose. El README debe explicar problema, arquitectura, stack, ejecución, ejemplo de request/response, decisiones, pruebas, limitaciones y roadmap. **RAG, agentes y event-driven no son condiciones para publicar el MVP.**

## Qué debe poder explicar el proyecto

El recorrido HTTP → transacción → PostgreSQL; sync/async; validación y errores; índices; pruebas; secretos; integración con LLM sin acoplamiento; RAG y evaluación de retrieval; tool calling seguro; el motivo de pasar de análisis síncrono a cola; retries, duplicados e idempotencia; y qué cambiaría para soportar más tráfico. Registrar decisiones y su evidencia en [decisions/](decisions/).
