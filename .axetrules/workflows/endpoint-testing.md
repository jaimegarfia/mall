# Workflow: `endpoint-testing` (v1.1)

---
**id**: `endpoint-testing`  
**version**: `1.1`  
**tags**: [api, swagger, integration-testing, automation]  
**dependency**: `.axetrules/context.json`  
**primary_output**: `.axetrules/history/testing/`  
---

##  Objetivo
Automatizar el ciclo de vida de pruebas de integración para endpoints **GET**. El flujo integra el descubrimiento automático de la especificación OpenAPI (v1.6.14) detectada en el proyecto y la ejecución resiliente de batches para verificar la disponibilidad de la API.

---

##  Proceso de Ejecución Paso a Paso

### 1. Fase de Sincronización (Context Awareness)
Antes de empezar, el agente debe leer el stack real del proyecto:
1.  **Lectura de Stack:** Confirmar en `context.json` que el proyecto usa **Java 8** y **Spring Boot 2.7.18**.
2.  **Localización de API:** Identificar la ruta del Swagger. Según el contexto, la librería es `springdoc-openapi-ui` y el path configurado es `/swagger-ui.html`.
3.  **Extracción de Endpoints:** Localizar el archivo JSON de la especificación (ej: `v3/api-docs`) para identificar los métodos GET y sus parámetros.

### 2. Fase de Triage de Datos (Interaction Gate)
El agente debe minimizar el ruido. Solo preguntará una vez:
1.  **Mapeo de Parámetros:** Listar todos los parámetros de tipo `Path` o `Query` marcados como obligatorios (`REQUIRED`).
2.  **Solicitud al Usuario:** "He detectado que para probar los endpoints de `gaia-api` necesito valores para: `{id}`, `{slug}`. Por favor, dímelos ahora para procesar todos los batches automáticamente."

### 3. Fase de Motor de Ejecución (Curl Engine)
El agente ejecutará las peticiones usando `curl.exe` (estándar en entornos Windows/Linux):
1.  **Seguridad de Host:** Solo se permiten llamadas a dominios en la allowlist (ej: `localhost:8080`).
2.  **Inyección Dinámica:** Sustituir los placeholders por los valores reales del usuario.
3.  **Captura de Evidencia:** Por cada llamada, obtener el `http_code` y el `time_total`. El cuerpo de respuesta se truncará a 2000 caracteres para el log técnico.

### 4. Fase de Generación de Informe y Persistencia
No se requiere intervención humana para consolidar resultados:
1.  **Creación de Reporte:** Generar un archivo en `.axetrules/history/testing/get-report-<timestamp>.md`.
2.  **Contenido Obligatorio:**
    * **Resumen Ejecutivo:** Total de endpoints, % de éxito (2xx) y % de fallos.
    * **Tabla de Resultados:** Detalle por Request ID, URL probada, Status y Tiempo.
    * **Sección de Errores:** Listado de endpoints que devolvieron 4xx o 5xx con su causa.
3.  **Snapshot de Estado:** Actualizar el campo `last_run` y `status` de los entrypoints en el `context.json` para mantener la memoria del proyecto.

---

##  Quality Gates (Puertas de Calidad)
* **GATE_1 (Safe_Method):** Solo se procesan métodos **GET**. Cualquier intento de ejecutar POST/PUT/DELETE mediante este flujo será bloqueado.
* **GATE_2 (Domain_Lock):** Si la `baseUrl` no coincide con el host configurado en `context.json`, el agente abortará la ejecución.
* **GATE_3 (Zero_Clutter):** Prohibido generar archivos temporales en la carpeta `postman/` o `resources/`. Todo el estado temporal debe vivir en la memoria del agente o en `.axetrules/history/`.

---

##  Reglas de Oro para el Agente
1.  **Sin "Copy-Paste" Manual:** El agente es responsable de leer los logs técnicos y transformarlos en el reporte final. No pidas al usuario que pegue resultados de consola.
2.  **Resiliencia:** Si un batch falla por un error de red, el agente debe reintentar una vez y, si persiste, marcar el batch como `FAILED` en el reporte pero continuar con el siguiente.
3.  **Contexto Java 8:** Asegurar que cualquier script auxiliar generado respete las limitaciones de entorno del proyecto.

---
