# AI Incident Assistant

Proyecto portfolio para registrar fallos de jobs o servicios y, en el MVP, analizar sus logs con un LLM para proponer causas, evidencia y acciones. Se construye por etapas: primero un backend sólido, después AI; RAG, tool calling y procesamiento por eventos se agregan cuando estén justificados.

## Estado y documentación

La implementación actual es inicial: FastAPI expone `GET /health` y existe una configuración básica de PostgreSQL. El plan detallado de la Fase 1 está en [docs/milestones/01-backend.md](docs/milestones/01-backend.md); el avance verificable se mantiene en [docs/progress.md](docs/progress.md).

- [Propósito y alcance](docs/PROJECT.md)
- [Arquitectura evolutiva](docs/ARCHITECTURE.md)
- [Hitos de las seis fases](docs/milestones/)
- [Decisiones técnicas](docs/decisions/)

El código ejecutable sigue en `backend/`. `src/` está reservado en la jerarquía documental propuesta; cualquier traslado del código será una tarea aparte con actualización de imports, comandos y pruebas. Las instrucciones completas de ejecución local se documentarán al cerrar los hitos 1 y 2.
