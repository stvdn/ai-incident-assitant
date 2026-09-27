# 003 — Abstracción del analizador LLM

**Estado:** decisión de diseño prevista para Fase 2; aún no implementada. **Contexto:** el backend debe guardar y consultar incidentes sin depender de un proveedor de modelos, y las pruebas normales deben ser deterministas.

## Dirección propuesta

Definir `IncidentAnalyzer` como contrato de aplicación para convertir datos de incidente en un análisis estructurado. Un adaptador del proveedor manejará transporte, timeouts y detalles de su API. El dominio y la persistencia consumirán el contrato validado, no la respuesta cruda del proveedor.

## Costo y validación

Agrega una interfaz y mapeo de errores, que solo se justifican si reducen el acoplamiento real y facilitan pruebas. Validar con un fake que cubra éxito, timeout, error y salida mal formada, y comprobar que la persistencia y API funcionan sin credenciales reales. Evitar una jerarquía de adaptadores hasta que exista un segundo caso que la necesite.
