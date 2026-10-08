# Aprender el backend por ramas

Este recorrido reconstruye los cambios que se habían acumulado sin commits. Las ramas son acumulativas y los commits separan responsabilidades. No representa una nueva implementación ni fecha cada cambio como si se hubiera versionado durante su desarrollo original. Todas estas etapas pertenecen a la Fase 1; AI, RAG, tool calling, colas y CI siguen pendientes.

Los nombres usan `fase-1/<hito>-<tema>` para las etapas y `fase-1/backend` para el resultado integrado. La preparación del aprendizaje se identifica con `00`; no demuestra el cierre del Hito 0 de alcance. Las fases 2 a 6 tendrán su rama cuando exista una implementación verificable.

## Recorrido

| Orden | Rama | Qué estudiar |
| --- | --- | --- |
| 1 | `fase-1/01-fastapi` | Punto de partida existente: factory de FastAPI, `/health`, motor PostgreSQL y documentación inicial. |
| 2 | `fase-1/00-preparacion` | Instrucciones de apoyo gradual y ajustes del editor para practicar. |
| 3 | `fase-1/02-postgresql` | Base PostgreSQL temporal, variables de prueba y conexión sin cargar el `.env` de desarrollo. |
| 4 | `fase-1/03-04-persistencia` | Dos commits: primero contrato, modelo y migración; después sesión, commit, refresh y rollback. Los hitos 3 y 4 se coordinan porque la migración necesita un contrato definido. |
| 5 | `fase-1/05-endpoints` | POST, consulta por UUID, listado paginado y pruebas HTTP con persistencia real. |
| 6 | `fase-1/06-configuracion-errores-logging` | Dos commits: validación de configuración al arrancar; después errores 404/422/500, request ID y eventos JSON. |
| 7 | `fase-1/backend` | Estado integrado, instrucciones de ejecución y evidencia actualizada. |

Cada rama permite inspeccionar el código sin cambios de hitos posteriores. Los nuevos commits descienden de `38279a8`; `fase-1/01-fastapi` conserva ese punto de partida. `main` integra el recorrido completo mediante fast-forward y `fase-1/backend` apunta al mismo estado integrado.

## Cómo recorrerlo

Primero lee esta guía desde la rama final. Con el árbol de trabajo limpio, cambia a una etapa y compara con su predecesora:

```powershell
git switch fase-1/03-04-persistencia
git log --oneline --reverse 38279a8..HEAD
git diff fase-1/02-postgresql..fase-1/03-04-persistencia -- backend
```

Para ver un commit individual usa `git show <hash>`. Evita estudiar todas las diferencias a la vez: lee la decisión, sigue el flujo y después ejecuta las pruebas disponibles en esa rama. Para volver al estado integrado:

```powershell
git switch fase-1/backend
```

`main` y las siete ramas del recorrido se publican juntas mediante un push atómico con referencias explícitas, sin forzar ni reescribir el historial. Una persona que clone el repositorio puede comprobarlas con `git branch -a` y recorrerlas usando los mismos nombres. Las ramas intermedias conservan sus checkpoints para estudiar cada etapa.

## Preparar y comprobar cada etapa

Desde `fase-1/02-postgresql` existe `.env.test.example`. Sigue la preparación de la base de pruebas del README de la rama final. Ejecuta los comandos desde `backend/` y usa las variables de prueba. Desde la etapa de persistencia aplica `alembic upgrade head` antes de pytest. En la etapa de base de pruebas todavía no existe Alembic configurado.

| Etapa | Comprobación | Casos esperados |
| --- | --- | --- |
| Base de pruebas | `uv run --frozen --env-file ../.env.test pytest` | 2 |
| Primer commit de contrato/migración | Mismo comando, después de migrar | 16 |
| Persistencia completa | Mismo comando, después de migrar | 18 |
| API | Mismo comando, después de migrar | 25 |
| Primer commit de configuración | Mismo comando, después de migrar | 31 |
| Errores y logging / estado integrado | Mismo comando, después de migrar | 33 |

Las etapas con migraciones se verifican sobre bases nuevas de PostgreSQL, con las mismas credenciales locales de pruebas y nombres temporales distintos. La suite borra las filas que crea; la paginación requiere una tabla vacía.

## Preguntas para comprobar comprensión

- Contrato: ¿por qué validar el límite del log en bytes y mantener también restricciones en PostgreSQL?
- Persistencia: ¿qué diferencia hay entre `flush()`, `commit()` y `refresh()`? ¿Qué permanece si falla HTTP después del commit?
- API: ¿por qué desempatar por UUID en el listado? ¿Qué limita la paginación por offset ante inserciones concurrentes?
- Configuración y logging: ¿crear el motor prueba la conexión? ¿Qué campos permiten investigar un fallo sin guardar el log del cliente ni el texto de la excepción?

El recorrido conserva las pruebas existentes y su evidencia; no cierra por sí solo los criterios de aprendizaje pendientes de [progress.md](progress.md).
