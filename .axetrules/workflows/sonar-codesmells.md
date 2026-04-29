# Workflow — Reducción de Code Smells (SonarQube) desde JSON

> **Pre-flight**: aplicar `.axetrules/workflows/quality-gates.md`  
> Defaults: idioma `es-ES`, no ejecutar `git` por defecto, evidencia obligatoria para marcar `[x]`.

Pipeline guiado para **reducir Code Smells** en SonarQube de forma **iterativa, trazable y con cambios atómicos**, usando como fuente la salida JSON del endpoint **`api/issues/search`**.

**Micro / proyecto:** ver `.axetrules/context.md` (campo `projectKey` / `projectName`)  
**Dashboard:** ver `.axetrules/context.md` (URL del dashboard)

> Este workflow es **reutilizable**: no hardcodea el micro. La configuración de Sonar (host, projectKey, etc.) se lee de `.axetrules/context.md` y/o `.axetrules/sonar/config.md`.

---

## Objetivo

- Partir de un JSON con issues `CODE_SMELL`.
- Generar un fichero de tracking **dentro de `.axetrules/`**.

---

## Artefactos

> Regla: **todos los artefactos auxiliares** (responses, outputs intermedios, etc.) deben quedar dentro de **`.axetrules/`** para mantener el repo limpio.

### Entrada

- JSON (respuesta de SonarQube): `.axetrules/sonar/response.json`
  - Debe ser la respuesta completa de `api/issues/search` (incluye `total`, `issues`, etc.).
  - Si `total > ps`, se debe paginar y **agregar** las páginas (ver “Exportar issues”).

### Salida

- Tracking: `.axetrules/sonar/sonar-codesmells.md`
  - Lista de issues en checklist, ordenada por severidad.
  - Fuente única para reanudar el trabajo iterativo.

### Config (opcional)

- Token/credenciales: `.axetrules/sonar/config.md`
  - Recomendación: token en local / vault / secret manager.
  - Evitar almacenar tokens reales en repositorios públicos.

---

## Flujo de trabajo (alto nivel)

1. **Exportar issues** (Sonar → `.axetrules/sonar/response.json`).
2. **PROMPT 1**: convertir `response.json` en `.axetrules/sonar/sonar-codesmells.md` (checklist completo, todo en `[ ]`).
3. **PROMPT 2 (iterativo)**: en cada iteración:
   - seleccionar 1 issue `[ ]` (prioridad por severidad),
   - generar patch(es) (unified diff),
   - marcarlo como `[x]` y añadir metadatos.

---

## Exportar issues (Sonar → JSON)

### Opción A) Automática (CLI) — recomendada
- Endpoint base: `<sonarHost>/api/issues/search` (ver `.axetrules/sonar/config.md`)
- Parámetros mínimos:
  - `componentKeys=<projectKey>` (ver `.axetrules/context.md` o `.axetrules/sonar/config.md`)
  - `types=CODE_SMELL`
  - `resolved=false`
  - `ps=500` (máximo habitual)

Guardar la salida en:
- `.axetrules/sonar/response.json`

**Notas de robustez (recomendadas):**
- Validar que la respuesta sea JSON (no HTML de login / error).
  - Señal típica de fallo: fichero vacío (0 bytes) o contenido HTML.
- Si `total > ps`, paginar con `p=1..n` y **agregar**:
  - concatenar `issues` de todas las páginas,
  - conservar `components` (idealmente unión sin duplicados, o conservar los de la primera página si Sonar devuelve todos siempre),
  - mantener `total` y `paging` coherentes (o documentar que es un agregado).

### Opción B) Manual (navegador) — fallback
Si no puedes ejecutar `curl`/CLI contra SonarQube (proxy, permisos, red corporativa, etc.):

1. Abre en el navegador una URL como esta (rellena `<sonarHost>` y `<projectKey>` desde `.axetrules/context.md` / `.axetrules/sonar/config.md`):
   - `<sonarHost>/api/issues/search?componentKeys=<projectKey>&types=CODE_SMELL&resolved=false&ps=500&p=1`
2. Si el navegador muestra JSON o descarga un fichero:
   - copia el contenido JSON completo y pégalo en el chat, **o**
   - guárdalo como `.axetrules/sonar/response.json`.
3. Si hay paginado, repite con `p=2`, `p=3`, etc. y pega todas las páginas (en orden) o indica cuántas páginas hay.

---

## Pasos rápidos de uso

1. Exportar el JSON del endpoint `api/issues/search` a: `.axetrules/sonar/response.json` (ver “Exportar issues”).
2. Ejecutar **PROMPT 1** y crear/actualizar `.axetrules/sonar/sonar-codesmells.md` con el resultado.
3. Ejecutar **PROMPT 2** tantas veces como sea necesario, pegando siempre el contenido actualizado del tracking.

---

## PROMPT 1 — Generar `sonar-codesmells.md` desde JSON

Copia este bloque completo en el chat de la IA:

```text
Tengo la salida JSON del endpoint api/issues/search de SonarQube guardada localmente en el fichero:
.axetrules/sonar/response.json

El fichero contiene la respuesta completa en formato JSON (con los campos total, issues, etc.).

Instrucciones:
Usa exclusivamente el contenido de ese JSON para crear/actualizar el fichero:
.axetrules/sonar/sonar-codesmells.md

Reglas obligatorias

REGLA 0) Cabecera
Incluye una cabecera con este formato:

# Sonar Code Smells

> **Pre-flight**: aplicar `.axetrules/workflows/quality-gates.md`  
> Defaults: idioma `es-ES`, no ejecutar `git` por defecto, evidencia obligatoria para marcar `[x]`.

Source: response.json
Total issues (code smells): <N>
Blocker: X, Critical: Y, Major: Z, Minor: W
Generated: <fecha UTC en ISO-8601>

REGLA 1) Formato por issue
Para cada issue del JSON crea una entrada sin marcar ([ ]) con este formato EXACTO:

- [ ] <SEVERITY> | <RULE_KEY> | <ruta/archivo.java>:L<linea> | <resumen corto del message>
  - Detalle: <message completo>
  - Recomendación: Ver regla <RULE_KEY> en SonarQube
  - IssueKey: <key>
  - Tags: <tags separados por coma o "N/A">
  - Esfuerzo estimado: <si existe en el JSON; si no, "N/A">

REGLA 2) Ordenación
Ordena los issues por severidad: BLOCKER → CRITICAL → MAJOR → MINOR.
Dentro de cada severidad respeta el orden del JSON.

REGLA 3) Línea desconocida
Si un issue no tiene línea (line), usa L?.

REGLA 4) Ruta del fichero
Extrae la ruta del fichero desde el campo component eliminando el projectKey inicial.

REGLA 5) No marcar
No marques ningún item como corregido en esta primera iteración.

REGLA 6) Nota final
Al final del fichero añade una nota breve indicando que los issues se corregirán en iteraciones usando parches y commits atómicos.

Importante
- No inventes información que no esté en el JSON.
- No elimines issues.
- Si el JSON es demasiado grande para procesarlo completo, indícalo explícitamente y espera a que te lo envíe por partes.

Ahora genera el contenido completo de .axetrules/sonar/sonar-codesmells.md a partir de response.json.
```

---

## PROMPT 2 — Corregir code smells de forma iterativa

Copia este bloque completo en el chat de la IA, junto con el contenido actualizado de `.axetrules/sonar/sonar-codesmells.md`:

```text
ROL: Eres un programador software experto en corrección de code smells sin alterar la funcionalidad.

Quiero que corrijas los code smells listados en .axetrules/sonar/sonar-codesmells.md.

REGLA 0) — PROHIBICIÓN ABSOLUTA (CRÍTICA)
- NO ejecutes comandos de ningún tipo.
- NO escribas comandos en formato ejecutable (Git, Gradle, terminal, PowerShell, Bash, etc.).
- NO incluyas líneas que puedan interpretarse como comandos, aunque sea como ejemplo.
- NO incluyas secciones tipo “Comandos sugeridos” ni bloques de comandos.
- Si necesitas indicar acciones, descríbelas solo en lenguaje natural, nunca como comandos.

REGLA 1) Lectura
Lee el fichero .axetrules/sonar/sonar-codesmells.md tal cual está (te lo proporcionaré en el mensaje o lo adjuntaré).

REGLA 2) Selección
- Elige hasta X = 1 items marcados con [ ] por iteración.
- Prioriza estrictamente por severidad:
  BLOCKER → CRITICAL → MAJOR → MINOR
  y dentro de la misma severidad, por orden de aparición en el fichero.

REGLA 3) Corrección
- Para cada item seleccionado, corrige el código en los ficheros .java correspondientes.
- Devuelve SIEMPRE los cambios como parches en formato unified diff.
- Cada parche debe ir dentro de un bloque (un bloque por parche):

<diff completo aquí>

- No devuelvas fragmentos sueltos si el cambio afecta a más de unas pocas líneas.
- Si el issue requiere renombrar símbolos públicos, incluye:
  - lista de ficheros afectados
  - plan de refactor en texto (sin comandos)

REGLA 4) Verificación (solo descriptiva)
Indica en texto:
- si el cambio debería compilar
- si afecta a tests existentes
- si sería recomendable ejecutar build o tests

(No escribas comandos, solo describe la acción.)

REGLA 5) Actualización del tracking
Actualiza .axetrules/sonar/sonar-codesmells.md:
- Marca como [x] solo los items para los que has entregado un parche.
- Mantén intactos todos los demás.

En cada item corregido añade:
- Commit (sugerido): <mensaje en texto>
- Patch (sugerido): <nombre.patch>
- Cambios: <resumen breve>

Si un item es un falso positivo:
- marca [x]
- añade:
  - Tipo de cierre: FALSE_POSITIVE
  - Evidencia: <explicación>
- no incluyas patch

REGLA 6) Formato de salida OBLIGATORIO
Devuelve la respuesta exactamente con estas secciones y en este orden:

### Items abordados
### Parches
### sonar-codesmells.md actualizado
### Pasos manuales

REGLA 7) Patches
Asegúrate de que has creado los ficheros .patch para yo poder hacer los commits manualmente.

REGLA 8) Reanudación
Si la respuesta se corta:
- volveré a ejecutar ESTE MISMO PROMPT,
- deberás volver a leer el sonar-codesmells.md actualizado,
- continuar desde los siguientes items [ ],
- no modificar los [x].
```

---

## Propuestas de mejora (recomendadas)

- Añadir un paso “sanity check” del JSON:
  - comprobar que existe `issues` y que `total` es numérico.
- Añadir paginado automático en el exportador (si se permite en el entorno) o instrucción explícita de cómo hacerlo.
- Mantener el tracking en `.axetrules/` para no “ensuciar” `src/main/resources/`.
- (Opcional) Guardar snapshots por fecha:
  - `.axetrules/sonar/snapshots/response-YYYYMMDD.json` para comparar tendencias.

## Buenas prácticas

- Cambios pequeños y atómicos (idealmente 1 issue por commit).
- Revisar manualmente los diffs antes de aplicar:
  - no cambiar lógica de negocio,
  - no introducir nuevos smells.
- Evitar silenciar reglas o “ignore blocks” salvo falso positivo justificado.
