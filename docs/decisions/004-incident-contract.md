# 004 — Contrato inicial de Incident

**Estado:** contrato inicial verificado; Hito 4 completo. **Fecha:** 27 de septiembre de 2026.

## Contexto y decisión acordada

En Fase 1, el cliente aporta `job_name` y `log`. El servidor genera `id` y `created_at`. El log se guarda como texto en PostgreSQL junto con el incidente y se limita a 64 KiB de datos codificados en UTF-8. Una solicitud que exceda el límite se rechaza antes de persistir.

El cliente también puede aportar `exit_code` como entero opcional, limitado al rango de PostgreSQL `Integer` (−2³¹ a 2³¹−1). Su ausencia se representa con `null`: algunos incidentes no provienen de un proceso que haya producido un código de salida. No se infiere un código a partir del log.

El contrato HTTP implementa `job_name` con máximo de 200 caracteres y recorte de espacios externos, conserva el texto original del `log` y rechaza entradas en blanco o que superen 64 KiB. La respuesta define `id` como UUID y `created_at` como `datetime`, y admite lectura desde un objeto ORM. El modelo y la migración están implementados; los endpoints quedan para el Hito 5.

Se excluye `status` del modelo inicial: no hay transiciones de estado del incidente en el alcance Create/Read y el resultado de un job o servicio no puede inferirse de cualquier log con fiabilidad. Se podrá añadir mediante migración cuando exista un caso de uso y una definición precisa.

`analysis_status`, `probable_cause`, `evidence` y `suggested_actions` pertenecen al análisis de Fase 2 y no son entrada del cliente en Fase 1. Su representación persistida aún no está decidida.

## Ventaja, costo y alternativa

Guardar el log en PostgreSQL permite confirmar incidente y log en una sola transacción y simplifica la ejecución y las pruebas locales. Aumenta el tamaño de la base y sus copias de seguridad; el límite contiene ese costo. Guardarlo como archivo local exigiría coordinar archivo y transacción, además de resolver limpieza y portabilidad. Si los logs reales superan el límite con frecuencia, medir tamaños y evaluar almacenamiento de objetos con una referencia en PostgreSQL.

## Verificación y seguimiento

La migración `ee06ce8fbc8f` se aplicó y Alembic mostró `head`. El usuario informó 11 pruebas de esquema aprobadas; 3 pruebas de integración comprobaron las restricciones contra PostgreSQL. Explicó que la validación de entrada evita operaciones innecesarias y que la base protege inserciones directas.
