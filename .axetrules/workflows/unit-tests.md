# Workflow: `unit-tests` (v5.2)

---
**id**: `unit-tests`  
**version**: `5.2`  
**tags**: [testing, java, automation, quality-gate]  
**dependency**: `.axetrules/context.json`  
**history_dir**: `.axetrules/history/`  
---

## Objetivo
Incrementar la cobertura de líneas del microservicio actual hasta alcanzar un **60% real (Line Coverage)**. El agente debe actuar de forma autónoma, recursiva y resiliente, priorizando la velocidad de ejecución y la estabilidad del build.

---

## 0. Fase de Sincronización y Contexto
Antes de tocar el código, el agente debe “leer la habitación”:

### Nota crítica: Shell y directorio de trabajo (Windows)
Este workflow puede ejecutarse en distintos shells. **NO mezclar sintaxis**.

#### Detectar el shell actual
- **PowerShell**: `echo $PSVersionTable.PSVersion`
- **CMD**: `echo %COMSPEC%`

#### Regla de oro (anti-errores de cwd)
En Windows, **NO uses** `cd mall-admin && ...` (ruta relativa) en automatizaciones: muchos runners/agents ejecutan cada comando en un proceso distinto o cambian de shell, y el `cd` no aplica donde crees.

**Regla obligatoria: comandos atómicos con ruta absoluta**
- PowerShell: `Set-Location 'C:\...\microservicio'; <comando>`
- CMD: `cd /d "C:\...\microservicio" && <comando>`

**Checklist de “estoy en el módulo correcto”**
- Debe existir `pom.xml` o `build.gradle(.kts)` en el cwd.
- Debe existir `./.coverage-cache.json` después de `analyze`.
- Si `next` dice “No se encontró caché…”, asume que **NO estás en el directorio correcto**.

Ejemplos correctos (Windows):

**PowerShell:**
```powershell
Set-Location 'C:\Users\jgarfiaa\Proyectos\mall\mall-admin'; npx coverage-orchestrator-cli analyze --path target\site\jacoco\jacoco.xml --minCoverageToIgnore 101
Set-Location 'C:\Users\jgarfiaa\Proyectos\mall\mall-admin'; npx coverage-orchestrator-cli next
```

**CMD:**
```bat
cd /d "C:\Users\jgarfiaa\Proyectos\mall\mall-admin" && npx coverage-orchestrator-cli analyze --path target\site\jacoco\jacoco.xml --minCoverageToIgnore 101
cd /d "C:\Users\jgarfiaa\Proyectos\mall\mall-admin" && npx coverage-orchestrator-cli next
```

---

1. **Lectura de Memoria**
   - Leer `.axetrules/context.json` para identificar la versión de Java, el build tool y la librería de aserciones. **Prohibido alucinar versiones.**

2. **Localización Estricta (cd + verificación obligatoria)**
   - Identificar el microservicio objetivo.
   - El Agente **debe** posicionarse en la raíz del módulo (donde existe `pom.xml` o `build.gradle(.kts)`) y ejecutar TODO desde ahí.
   - Usar el bloque que corresponda a tu shell:

   **PowerShell (recomendado):**
   ```powershell
   Set-Location 'C:\path\to\microservicio'
   Get-Location
   dir pom.xml, build.gradle, build.gradle.kts -ErrorAction SilentlyContinue
   ```

   **CMD (cmd.exe):**
   ```bat
   cd /d "C:\path\to\microservicio" && echo %cd% && dir pom.xml build.gradle build.gradle.kts
   ```

   - Si no aparece `pom.xml` o `build.gradle(.kts)`, **no continuar**: corregir el path del microservicio (subir/bajar carpetas hasta estar en la raíz del módulo).

3. **Bootstrap Check (JaCoCo no puede medir “cero tests”)**
   - Si no existe ningún test, crear un `BootstrapTest.java` mínimo en `src/test/java` para habilitar el motor de tests y que JaCoCo genere `jacoco.xml`.

4. **Generación de Evidencia (JaCoCo XML)**
   - Ejecutar el build con reporte JaCoCo para generar `jacoco.xml`.

   **Maven (recomendado):**
   ```powershell
   mvn clean jacoco:prepare-agent test jacoco:report "-DskipTests=false"
   ```

   **Gradle:**
   ```powershell
   ./gradlew clean test jacocoTestReport
   ```

5. **Indexación (analyze) + verificación de cache (obligatoria)**
   - Ejecutar `analyze` con `--path` explícito (no depender de auto-detect si se busca robustez).
   - Usar el bloque que corresponda a tu shell:

   **PowerShell (Maven default):**
   ```powershell
   npx coverage-orchestrator-cli analyze --path target\site\jacoco\jacoco.xml --minCoverageToIgnore 101
   dir .coverage-cache.json
   ```

   **PowerShell (Gradle default):**
   ```powershell
   npx coverage-orchestrator-cli analyze --path build\reports\jacoco\test\jacocoTestReport.xml --minCoverageToIgnore 101
   dir .coverage-cache.json
   ```

   **CMD (Maven default):**
   ```bat
   npx coverage-orchestrator-cli analyze --path target\site\jacoco\jacoco.xml --minCoverageToIgnore 101 && dir .coverage-cache.json
   ```

   **CMD (Gradle default):**
   ```bat
   npx coverage-orchestrator-cli analyze --path build\reports\jacoco\test\jacocoTestReport.xml --minCoverageToIgnore 101 && dir .coverage-cache.json
   ```

   - Si no existe `.coverage-cache.json` en el directorio actual:
     - no continuar,
     - repetir el paso 4 (asegurar que `jacoco.xml` existe y la ruta es correcta),
     - y repetir este paso 5.

> Nota de arquitectura: el CLI es **scope por módulo**. `next` y `summary` solo leen `./.coverage-cache.json` en el **directorio actual**.

---

## 1. Fase de Misión Quirúrgica
1. **Obtención de Tarea**
   - PowerShell:
     ```powershell
     npx coverage-orchestrator-cli next
     ```
   - CMD:
     ```bat
     npx coverage-orchestrator-cli next
     ```

2. **Validación de Módulo (defensa)**
   - Verificar que el comando sugerido (`suggestedTestCommand`) corresponde al módulo actual.
   - Reglas:
     - Si incluye `-pl`, debe coincidir con el basename de `pwd`.
     - Si no coincide, corregir dinámicamente `-pl <modulo_actual>`.

3. **Análisis de SUT**
   - Identificar colaboradores a mockear y métodos al 0% (según la misión).

---

## 2. Fase de Diseño y Arquitectura (Senior Path)
1. **Aislamiento Total**
   - Solo tests unitarios con Mockito.
   - Prohibido `@SpringBootTest`.
   - `@WebMvcTest` solo si es imprescindible y está justificado por el tipo de clase.

2. **Inyección con Reflection (compatibilidad)**
   - Si `context.json` indica Java < 17, usar:
     - `ReflectionTestUtils.setField(...)` para dependencias privadas o `@Value`,
     - o inyección por constructor si es viable.
   - Si Java >= 17, mantener el test simple (constructor/visibilidad) y evitar hacks innecesarios.

3. **Redacción de Secretos**
   - Si aparecen credenciales (config/properties/yml), **no usarlas**.
   - Usar dummy values (`"test-secret"`, `"dummy-key"`).

---

## 3. Fase de Validación y Protocolo de Eyección (Strike 5)
Para evitar bloqueos y desperdicio de recursos:

1. **Ejecución Selectiva (solo la clase objetivo)**
   - Ejecutar únicamente el comando sugerido para la clase asignada (ejemplos):

   **Maven (single test):**
   ```powershell
   mvn test "-Dtest=ClaseTest"
   ```

   **Maven (módulo):**
   ```powershell
   mvn test -pl <modulo> "-Dtest=ClaseTest"
   ```

   **Gradle:**
   ```powershell
   ./gradlew test --tests ClaseTest
   ```

2. **Bucle de Corrección**
   - Máximo **5 intentos** de reparación (lógica/compilación).
   - Mantener cambios mínimos por iteración; no introducir refactors grandes.

3. **GATE_STRIKE_5 (Abandono Técnico)**
   - Si el test falla por 5ª vez:
     - desactivar el test (`@Disabled` o comentar lo mínimo necesario),
     - el build debe quedar en **SUCCESS** antes de seguir.
   - Ejecutar `analyze` para registrar el strike y permitir auto-skip del CLI:
     ```powershell
     npx coverage-orchestrator-cli analyze --path target\site\jacoco\jacoco.xml --minCoverageToIgnore 101
     ```

---

## 4. Bucle Autónomo Recursivo
**INSTRUCCIÓN PARA EL AGENTE:** Tras cada validación exitosa:

1. Ejecutar:
   - PowerShell:
     ```powershell
     npx coverage-orchestrator-cli summary
     ```
   - CMD:
     ```bat
     npx coverage-orchestrator-cli summary
     ```

2. Si `Gap (Line) > 0` y hay clases en `TODO`, iniciar inmediatamente la siguiente misión:
   - PowerShell:
     ```powershell
     npx coverage-orchestrator-cli next
     ```
   - CMD:
     ```bat
     npx coverage-orchestrator-cli next
     ```

3. **No despedirse ni pedir permiso.** El objetivo es el 60%.

---

## Quality Gates (Verificación Obligatoria)
El agente no puede dar por “terminada” una misión si no cumple:

- **GATE_1 (No_Generic_Asserts):** Prohibido `assertTrue(true)`. Cada test valida lógica real.
- **GATE_2 (Context_Match):** Compatible con `javaVersion` de `context.json`.
- **GATE_3 (Isolated):** No levanta DB ni contexto Spring (salvo excepción justificada por `@WebMvcTest`).
- **GATE_4 (Green_Build):** El comando selectivo termina en `BUILD SUCCESS`.

---

## Reglas de Oro (Terminal Safe)
1. **Comandos Limpios:** Solo enviar a la terminal comandos ejecutables. Prohibido pegar Markdown (`- [ ]`) o XML.
2. **Windows Syntax:** Envuelve propiedades en comillas:
   - `"-Dtest=ClassName"`
3. **Historial:** Errores persistentes de arquitectura → documentar breve en:
   - `.axetrules/history/testing-log.md`
4. **Resiliencia:** Si JaCoCo no refleja subida tras un test exitoso:
   - ejecutar `analyze` igualmente,
   - seguir con la siguiente clase recomendada,
   - **no detenerse**.
5. **Comandos Atómicos (anti-cwd issues):**
   - Si hay riesgo de ejecutar en el directorio equivocado, usar comandos atómicos por shell:

   **PowerShell (usa `;`):**
   ```powershell
   Set-Location 'C:\path\to\microservicio'; npx coverage-orchestrator-cli next
   ```

   **CMD (usa `&&`):**
   ```bat
   cd /d "C:\path\to\microservicio" && npx coverage-orchestrator-cli next
   ```
