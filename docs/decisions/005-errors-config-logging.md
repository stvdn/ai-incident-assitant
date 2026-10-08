# 005 — Configuración, errores HTTP y logging

**Fecha:** 7 de octubre de 2026. **Estado:** implementado y pruebas reportadas como aprobadas; explicación del usuario pendiente.

## Decisión

Validar variables obligatorias y rango del puerto mediante `config.py`; el lifespan crea el motor al arrancar y lo dispone al apagar. Crear el motor valida configuración, pero no comprueba conexión real a PostgreSQL.

Mantener un contrato de error `error.code` y `error.message`, con ubicación y tipo de fallo en validaciones 422. No devolver entrada original ni texto de excepciones inesperadas. Los estados HTTP siguen distinguiendo recurso inexistente (404), entrada inválida (422) y fallo interno (500).

Usar logging estándar con formatter JSON y campos permitidos: timestamp, level, event, incident_id, request_id y error_type. Registrar `incident_created` tras commit y refresh; registrar `request_failed` con clase de excepción y UUID generado para la petición. El header `X-Request-ID` permite relacionar la respuesta con el evento de fallo.

El middleware convierte excepciones de rutas en respuestas 500 mediante el manejador compartido. Así evita que esos fallos lleguen a Uvicorn como excepciones no manejadas con su texto completo. Se conserva el manejador general como respaldo. Los logs de aplicación omiten cuerpo, log del incidente, contraseña y traceback.

## Ventaja y costo

La biblioteca estándar evita otra dependencia; los campos explícitos permiten buscar eventos e incidentes y reducen exposición de datos. Omitir texto de excepción y traceback limita el diagnóstico: si resulta insuficiente, añadir contexto técnico seleccionado y pruebas de redacción antes de ampliar lo registrado. La captura de logging en memoria verifica nuestro formatter y los eventos; no constituye una auditoría de todos los logs de terceros ni de fallos de arranque.

## Evidencia

El usuario confirmó 6 casos de configuración y 9 casos HTTP aprobados. Los tests incluyen error interno simulado, registro del ID del incidente, coincidencia del request ID con la respuesta y ausencia de marcadores sensibles. No se compartió salida exacta de las últimas ejecuciones.

El 7 de octubre de 2026 Codex ejecutó directamente los 18 casos sin conexión PostgreSQL y la suite completa con `.env.test`: 18 y 33 aprobados respectivamente. La ejecución completa incluye los 6 casos de configuración y los 9 HTTP. La explicación del usuario sobre la selección de campos sigue pendiente para cerrar el hito.
