# AI Incident Assistant

Proyecto portfolio para registrar fallos de jobs o servicios y, en el MVP, analizar sus logs con un LLM para proponer causas, evidencia y acciones. Se construye por etapas: primero un backend sólido, después AI; RAG, tool calling y procesamiento por eventos se agregan cuando estén justificados.

## Estado y documentación

Las Fases 1 y 2 permiten crear, consultar y listar incidentes en PostgreSQL y analizar sus logs con Gemini. Incluyen contratos Pydantic, migraciones Alembic, sesiones con rollback, errores HTTP, logging JSON y 69 pruebas verificadas localmente. Se verificaron un POST real de analisis y su recuperacion mediante GET. La ultima CI remota registrada corresponde a Fase 1; falta publicar y verificar los cambios de Fase 2. RAG, tool calling y procesamiento por eventos siguen en el roadmap.

Para estudiar los cambios en orden, sigue [la ruta por ramas y commits](docs/LEARNING_PATH.md). El plan detallado de la Fase 1 está en [docs/milestones/01-backend.md](docs/milestones/01-backend.md); el avance verificable se mantiene en [docs/progress.md](docs/progress.md).

- [Propósito y alcance](docs/PROJECT.md)
- [Arquitectura evolutiva](docs/ARCHITECTURE.md)
- [Hitos de las seis fases](docs/milestones/)
- [Decisiones técnicas](docs/decisions/)

El código ejecutable sigue en `backend/`. `src/` está reservado en la jerarquía documental propuesta.

## Ejecución local

Requisitos: Python 3.12 o posterior, uv, Docker y Docker Compose. Los comandos siguientes usan PowerShell y parten de la raíz del repositorio.

```powershell
Copy-Item .env.example .env
```

Define una contraseña local en `POSTGRES_PASSWORD` dentro de `.env`. La plantilla configura el acceso desde el host a `127.0.0.1:5432`. Conserva los archivos `.env` y `.env.test` fuera de Git.

```powershell
docker compose up -d --wait
Set-Location backend
uv sync --frozen
uv run --frozen --env-file ../.env alembic upgrade head
uv run --frozen --env-file ../.env uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000` y Swagger en `/docs`. `GET /health` comprueba que responde el proceso; la conexión real se comprueba con la prueba de PostgreSQL. Para detener la base, usa `docker compose stop` desde la raíz; el volumen de desarrollo conserva los datos. El 9 de octubre de 2026 el usuario confirmó que un incidente creado por API pudo recuperarse tras reiniciar PostgreSQL de desarrollo.

## Full application with Docker Compose

From the repository root, configure the untracked `.env` with database credentials and Gemini settings, then run:

```powershell
docker compose up -d --build --wait
docker compose ps
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

Compose builds the API from `backend/`, waits for database health, applies migrations and starts Uvicorn on port 8000. The container connects to PostgreSQL at `db:5432`; host-run Python uses `127.0.0.1`. Credentials are supplied at runtime. Stop any host-run Uvicorn process occupying port 8000 first.

The API healthcheck checks HTTP liveness, not database or provider availability. Migration-on-startup is intended for one API instance; separate migrations before running multiple replicas. Diagnose startup with `docker compose logs --tail 80 api`. Stop services with `docker compose stop`, retaining database data.

For host-run development, start only the database with `docker compose up -d --wait db` and stop the container API if it occupies port 8000.

## Probar la API

Con el servidor en marcha, desde otra terminal:

```powershell
$payload = @{ job_name = "daily-import"; log = "Connection timeout"; exit_code = 1 } | ConvertTo-Json
$incident = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/incidents -ContentType application/json -Body $payload
Invoke-RestMethod -Uri "http://127.0.0.1:8000/incidents/$($incident.id)"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/incidents?limit=20&offset=0"
```

La creación devuelve HTTP 201 con `id`, `job_name`, `log`, `exit_code` y `created_at`. El servidor genera el ID y la fecha. `job_name` acepta hasta 200 caracteres, `log` hasta 64 KiB UTF-8 y `exit_code` es opcional. El listado devuelve `items`, `limit` y `offset`, en orden de fecha e ID descendentes. La paginación se comprueba sobre un conjunto estable; las inserciones concurrentes pueden desplazar los offsets.

Los errores usan `error.code` y `error.message`: 404 para un incidente inexistente, 422 para entrada inválida y 500 para un fallo interno. El header `X-Request-ID` permite correlacionar un fallo con su evento de logging. No hay operaciones de actualización ni borrado en la API.

## Pruebas

Desde la raíz, prepara una base exclusiva para integración. La contraseña de la plantilla es un valor público para este entorno local de pruebas y coincide con `compose.test.yml`.

```powershell
Copy-Item .env.test.example .env.test
docker compose -f compose.test.yml up -d --wait
Set-Location backend
uv sync --frozen
uv run --frozen --env-file ../.env.test alembic upgrade head
uv run --frozen --env-file ../.env.test pytest
```

Esta suite tiene 33 casos: 18 de esquema, configuración y health; 15 de conexión, restricciones, transacciones y API con PostgreSQL. `compose.test.yml` declara el proyecto independiente `ai-incident-assitant-tests`, para que levantar o detener pruebas no retire la red de desarrollo. Las pruebas de integración usan nombres/UUID únicos y limpian sus filas. La prueba de paginación requiere la tabla `incidents` vacía: usa exclusivamente la base temporal en el puerto 5433, nunca la de desarrollo.

Para ejecutar los casos que no requieren PostgreSQL:

```powershell
uv run --frozen pytest -m unit
```

Para ejecutar únicamente integración, después de preparar PostgreSQL y aplicar las migraciones:

```powershell
uv run --frozen --env-file ../.env.test pytest -m integration
```

Los marcadores están registrados con `--strict-markers`. Una fixture automática exige `POSTGRES_DB=incidents_test` antes de ejecutar integración; comprueba el nombre configurado, no la identidad del servidor. La limpieza selecciona los datos propios de cada prueba y usa `finally` para ejecutarse aunque falle una aserción.

Al terminar, desde la raíz usa `docker compose -f compose.test.yml down`. La base de pruebas usa `tmpfs`: al recrear el contenedor hay que aplicar las migraciones de nuevo.


## Phase 2: Gemini incident analysis

The API can analyze an existing incident and store successful analyses in PostgreSQL. The provider adapter uses `google-genai`; normal tests substitute the provider and make no paid API calls.

Set `GEMINI_API_KEY` in the local, untracked `.env`, and set `GEMINI_MODEL` to a model available to your project. The code default is `gemini-2.5-flash-lite`; the reported live demonstration used `gemini-3.5-flash-lite`. Keep credentials out of Git. Use synthetic logs for free-tier demonstrations; availability, data handling and quotas depend on provider terms and project configuration. See [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

From `backend/`, with development PostgreSQL running:

```powershell
uv sync --frozen
uv run --frozen --env-file ../.env alembic upgrade head
uv run --frozen --env-file ../.env uvicorn app.main:app --reload
```

Create an incident through `POST /incidents`:

```json
{"job_name":"daily-import","log":"Connection refused at db:5432","exit_code":1}
```

Use the returned incident UUID in `POST /incidents/{incident_id}/analyses` (no request body). A successful 201 response includes:

```json
{
  "probable_cause": "PostgreSQL is unreachable.",
  "confidence": 0.8,
  "evidence": ["Connection refused at db:5432"],
  "suggested_actions": ["Check PostgreSQL availability."],
  "id": "3f61e9f9-fb3a-4f64-b909-fb1b4b7aa19d",
  "incident_id": "6647fa57-51ca-4995-8481-498b40798749",
  "status": "completed",
  "model": "example-model",
  "latency_ms": 1500,
  "created_at": "2026-10-27T18:37:52Z"
}
```

This is an illustrative response; generated content and metadata vary. `GET /incidents/{incident_id}/analyses?limit=20&offset=0` returns saved analyses, newest first. Repeated POST requests create separate analyses and consume provider quota.

### Behavior and limits

- The application sends incident data to Gemini as untrusted JSON, separately from system instructions. Prompt separation reduces risk but does not guarantee resistance to prompt injection.
- Pydantic validates the result. Evidence must also occur verbatim in the supplied log. These checks do not establish that the diagnosis is correct; confidence is not calibrated.
- The provider request uses a 30-second HTTP timeout and one attempt, with no automatic retries. This is not a strict end-to-end request deadline.
- Timeout maps to 504; rate limit to 503; other provider failures or invalid output to 502. Missing provider configuration returns 503. Raw provider errors are not returned to clients.
- Successful results store model, completed status, latency and creation time. Failed attempts do not create analysis rows. Token usage and cost accounting are not implemented.
- The read transaction is released before the provider call. A validated result is committed afterward, so provider failure does not change the incident.
- Analysis runs synchronously in the HTTP request. No queue, RAG, tools, or automatic recovery actions are implemented.

Run tests against the isolated test database, with no Gemini key required:

```powershell
docker compose -f ../compose.test.yml up -d --wait
uv run --frozen --env-file ../.env.test alembic upgrade head
uv run --frozen --env-file ../.env.test pytest
```
