# AI Incident Assistant

Proyecto portfolio para registrar fallos de jobs o servicios y, en el MVP, analizar sus logs con un LLM para proponer causas, evidencia y acciones. Se construye por etapas: primero un backend sólido, después AI; RAG, tool calling y procesamiento por eventos se agregan cuando estén justificados.

## Estado y documentación

La Fase 1 ya permite crear, consultar y listar incidentes persistidos en PostgreSQL. Incluye contratos Pydantic, migración Alembic, sesiones con rollback, paginación, errores HTTP, configuración y logging JSON. Hay 33 pruebas automatizadas; CI y el cierre de algunos criterios de aprendizaje siguen pendientes. Las fases 2 a 6 son roadmap: todavía no hay análisis con AI.

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

La API queda en `http://127.0.0.1:8000` y Swagger en `/docs`. `GET /health` comprueba que responde el proceso; la conexión real se comprueba con la prueba de PostgreSQL. Para detener la base, usa `docker compose stop` desde la raíz; el volumen de desarrollo conserva los datos. La persistencia tras reinicio sigue pendiente de verificación.

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

Esta suite tiene 33 casos: 18 de esquema, configuración y health; 15 de conexión, restricciones, transacciones y API con PostgreSQL. Las pruebas de integración usan nombres/UUID únicos y limpian sus filas. La prueba de paginación requiere la tabla `incidents` vacía: usa exclusivamente la base temporal en el puerto 5433, nunca la de desarrollo.

Para ejecutar los 18 casos que no requieren PostgreSQL:

```powershell
uv run --frozen pytest -m unit
```

Para ejecutar únicamente integración, después de preparar PostgreSQL y aplicar las migraciones:

```powershell
uv run --frozen --env-file ../.env.test pytest -m integration
```

Los marcadores están registrados con `--strict-markers`. Una fixture automática exige `POSTGRES_DB=incidents_test` antes de ejecutar integración; comprueba el nombre configurado, no la identidad del servidor. La limpieza selecciona los datos propios de cada prueba y usa `finally` para ejecutarse aunque falle una aserción.

Al terminar, desde la raíz usa `docker compose -f compose.test.yml down`. La base de pruebas usa `tmpfs`: al recrear el contenedor hay que aplicar las migraciones de nuevo.
