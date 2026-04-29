# Workflow: `context-discovery` (v2.0)

---
**id**: `context-discovery`  
**version**: `2.0`  
**tags**: [discovery, stack, automation-ready]  
**primary_output**: `.axetrules/context.json`  
**history_dir**: `.axetrules/history/`  
---

##  Objetivo
Inspeccionar la anatomía completa del proyecto para generar una **fuente de verdad estructurada (JSON)**. Este archivo servirá como la "memoria compartida" para todos los agentes de IA que trabajen en el repositorio, eliminando alucinaciones sobre versiones o arquitecturas.

---

##  Inputs y Configuración
1. **Ruta del Contexto:** `.axetrules/context.json` (fijo, para evitar dispersión).
2. **Modo de Operación:**
   - `refresh` (Default): Re-escanea y actualiza valores manteniendo la estructura.
   - `deep-scan`: Fuerza la lectura de archivos de código fuente para detectar patrones de diseño.

---

##  Fuentes de Verdad (Jerarquía de Evidencia)
El agente debe construir el JSON basándose en:
1. **Build Manifests:** `pom.xml`, `build.gradle`, `package.json`.
2. **Runtime & Infra:** `docker-compose.yml`, `Dockerfile`, `Chart.yaml`.
3. **App Config:** `application.yml`, `bootstrap.properties`, `.env.example`.
4. **Integraciones:** `db/migration/`, Swagger JSON, carpetas de recursos externos.

---

##  Proceso de Ejecución

### 1. Extracción de Stack Base
El agente debe mapear:
- **Runtime:** Lenguaje, versión exacta, vendor de la JVM (si aplica).
- **Frameworks:** Versión de Spring Boot, Jakarta EE, o similares.
- **Tooling:** Maven/Gradle version, Node version.

### 2. Inventario de Superficie (Surface Area)
Descubrir componentes activos:
- **Persistencia:** Tipo de DB (SQL/NoSQL), motor de migraciones.
- **Comunicaciones:** REST, Feign Clients, Kafka, WebSockets, gRPC.
- **Seguridad:** JWT, OAuth2, Spring Security.

### 3. Redacción de Seguridad (CRÍTICO)
**Prohibición absoluta:** No se permite guardar credenciales, tokens o keys en el JSON. 
- Si se encuentra un secreto en un `yml` o `properties`, se debe registrar la clave pero el valor debe ser estrictamente `REDACTED_SECRET`.

---

##  Quality Gates (Puertas de Calidad)
Antes de finalizar, el agente debe validar el output contra estos criterios:

* **GATE_1 (Evidence):** Cada valor tecnológico debe tener un campo `"evidence_file"` apuntando al archivo donde se detectó.
* **GATE_2 (No_Secrets):** El JSON no contiene valores sensibles (redacción aplicada).
* **GATE_3 (Version_Pinning):** Se han extraído versiones numéricas (ej. `17`, no solo `Java`).
* **GATE_4 (Schema_Validity):** El JSON generado es válido y parseable.

---

##  Estructura del Output (`context.json`)
El agente debe generar un objeto con esta estructura mínima de ejemplo:

```json
{
  "project_info": {
    "name": "string",
    "last_discovery": "ISO-8601-TIMESTAMP"
  },
  "stack": {
    "language": { "name": "Java", "version": "17", "evidence": "pom.xml" },
    "framework": { "name": "Spring Boot", "version": "3.2.0", "evidence": "pom.xml" },
    "build_tool": "Maven"
  },
  "infrastructure": {
    "database": "PostgreSQL 15",
    "cache": "Redis",
    "containers": "Docker Compose"
  },
  "conventions": {
    "architecture": "Layered/Hexagonal/Unknown",
    "naming": "kebab-case-endpoints",
    "testing_lib": "JUnit 5 + Mockito"
  },
  "security": {
    "auth_type": "JWT",
    "secrets_redacted": true
  }
}
```

---

##  Registro de Historial
Tras generar el JSON, el agente debe crear un snapshot en Markdown para legibilidad humana en:
- `.axetrules/history/YYYY-MM-DD-discovery-report.md`
- Resumen de cambios: *"Se detectó actualización de Java 11 a 17 en el pom.xml"*.

---

##  Definition of Done (DoD)
1. El archivo `.axetrules/context.json` ha sido creado o actualizado con datos 100% reales.
2. El reporte de historial ha sido registrado.
3. Se han pasado todos los **Quality Gates**.
4. No hay carpetas fuera de `.axetrules` (limpieza total).

