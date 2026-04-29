# Instrucciones GAIA/Axet (1 mensaje): “Modelo de datos” end-to-end con selección de entidades (v3)

Objetivo: ejecutar un flujo completo:
1) Generar inventario de clases Java (v3)
2) Pedir a la IA que **seleccione entidades** a partir del inventario (sin usar `isJpaEntity`)
3) Generar el apartado final **“Modelo de datos”** solo con entidades seleccionadas
4) Guardarlo en `.axetrules/generated/modelo-datos.md`
5) Generar `README.generated.md` embebiendo el modelo de datos

---

## Paso -1) Prechecks (Python y repo)

1) Comprueba que puedes ejecutar Python:
- Ejecuta: `python --version`
- Si falla, prueba: `py -V`
- Si falla, prueba: `python3 --version`

2) Comprueba que existe el repo y el directorio `tools/docgen`:
- Debe existir: `tools/docgen`
- Debe existir: `tools/docgen/v3`

---

## Paso 0) Detecta el directorio de código Java (para usarlo como `--src`)

Determina cuál usar como `--src` siguiendo este orden:
1) Si existe `src/main/java`, usa `src/main/java`.
2) Si existe `src`, busca dentro un subdirectorio que contenga muchos `.java` y usa ese directorio raíz.
3) Si no, busca en el repo un directorio que contenga `.java` y úsalo como `--src`.

Si tienes dudas, prioriza `src/main/java`.

---

## Paso 1) Genera el inventario de clases (v3)

Ejecuta primero (Windows suele tener `python`):

```bat
python tools/docgen/workflow_crearReadme/v3/generate_modelo_datos_v3.py --src <SRC_DETECTADO> --mode prompt --include-empty-classes --out-entities-json .axetrules/generated/modelo-datos.entities.v3.json --out-prompt .axetrules/generated/modelo-datos.prompt.final.v3.md
```

Si `python` no existe, reintenta con `python3`:

```bat
python3 tools/docgen/workflow_crearReadme/v3/generate_modelo_datos_v3.py --src <SRC_DETECTADO> --mode prompt --include-empty-classes --out-entities-json .axetrules/generated/modelo-datos.entities.v3.json --out-prompt .axetrules/generated/modelo-datos.prompt.final.v3.md
```

Si tampoco existe, usa el launcher:

```bat
py -3 tools/docgen/workflow_crearReadme/v3/generate_modelo_datos_v3.py --src <SRC_DETECTADO> --mode prompt --include-empty-classes --out-entities-json .axetrules/generated/modelo-datos.entities.v3.json --out-prompt .axetrules/generated/modelo-datos.prompt.final.v3.md
```

### Si aparece el error “No se han encontrado clases candidatas…”
Reintenta forzando incluir todas las clases (equivalente a v2):

```bat
python tools/docgen/workflow_crearReadme/v3/generate_modelo_datos_v3.py --src <SRC_DETECTADO> --mode prompt --include-empty-classes --include-class-regex ".*" --out-entities-json .axetrules/generated/modelo-datos.entities.v3.json --out-prompt .axetrules/generated/modelo-datos.prompt.final.v3.md
```

(usa `python3` o `py -3` si aplica)

Resultado esperado tras este paso:
- existe `.axetrules/generated/modelo-datos.entities.v3.json`
- existe `.axetrules/generated/modelo-datos.prompt.final.v3.md` (no es obligatorio para el resto del flujo, pero se guarda por trazabilidad)

---

## Paso 2) IA: Selecciona entidades desde el inventario (IGNORANDO `isJpaEntity`)

### Entrada
- Lee `.axetrules/generated/modelo-datos.entities.v3.json`.
- Para cada elemento, usa solo:
  - `name`, `package`, `file`
  - `fields[]`
- **Ignora completamente** `isJpaEntity` (no lo uses como señal).

### Salida requerida
Devuelve **solo JSON** (sin Markdown) y guárdalo en:
- `.axetrules/generated/modelo-datos.entities.selected.v3.json`

Formato exacto:

```json
{
  "entities": [
    {
      "fqn": "<package>.<name>",
      "confidence": "high|medium|low",
      "reasons": ["..."]
    }
  ]
}
```

Reglas:
- `fqn` debe ser totalmente cualificado (`package.name`). Si `package` es null, usa solo `name`.
- Incluye 1-2 razones breves por clase.
- No inventes campos.

---

## Paso 3) Genera un prompt final para “Modelo de datos” usando solo las entidades seleccionadas

### 3.1) Preparación
- Lee `.axetrules/generated/modelo-datos.entities.selected.v3.json`.
- Construye una lista de FQN seleccionados (`entities[].fqn`).
- Con esa lista, filtra el inventario original (`.axetrules/generated/modelo-datos.entities.v3.json`) quedándote solo con esas clases.

### 3.2) Construcción del prompt
- Usa como plantilla base: `tools/docgen/modelo-datos.prompt.md`.
- Rellena:
  - `{{ENTIDADES_JSON}}` con el JSON filtrado (solo entidades seleccionadas)
  - `{{ENTIDADES_MICRO}}` con las clases filtradas (puedes reconstruirlas a partir de `file` leyendo el fichero y pegando el bloque de clase, o si no, déjalo vacío y apóyate en `ENTIDADES_JSON`).

Guarda el prompt final en:
- `.axetrules/generated/modelo-datos.prompt.final.selected.v3.md`

---

## Paso 4) IA: Genera el Markdown “Modelo de datos”

- Lee `.axetrules/generated/modelo-datos.prompt.final.selected.v3.md`.
- Ejecuta exactamente sus instrucciones para generar el apartado **“Modelo de datos”**.
- Respeta el formato indicado por el prompt (FORMATO_EXAMPLE) y sus reglas.
- Si faltan descripciones y el prompt indica “Sin descripción”, respétalo.

---

## Paso 5) Guarda el resultado en `.axetrules/generated/modelo-datos.md`

- Escribe el resultado en `.axetrules/generated/modelo-datos.md`.
  - Si no existe, créalo.
  - Si existe, sobrescribe su contenido.
- No añadas texto adicional fuera del Markdown solicitado.
- No envuelvas la salida en bloques de código (no uses ```).

Control mínimo antes de continuar:
- Asegúrate de que `.axetrules/generated/modelo-datos.md` NO está vacío.

---

## Paso 6) Genera el README final (a partir de plantilla + config + modelo de datos)

Este paso:
- Lee la plantilla: `tools/docgen/workflow_crearReadme/readme.template.md`
- Lee la config: `tools/docgen/workflow_crearReadme/readme.config.json`
- Lee el modelo de datos: `.axetrules/generated/modelo-datos.md`
- Genera: `README.generated.md` (o la ruta configurada en `outReadmePath`)

Ejecuta primero:

```bat
python tools/docgen/workflow_crearReadme/generate_readme.py --config tools/docgen/workflow_crearReadme/readme.config.json
```

Si `python` no existe, reintenta con `python3`:

```bat
python3 tools/docgen/workflow_crearReadme/generate_readme.py --config tools/docgen/workflow_crearReadme/readme.config.json
```

Si tampoco existe, usa:

```bat
py -3 tools/docgen/workflow_crearReadme/generate_readme.py --config tools/docgen/workflow_crearReadme/readme.config.json
```

Resultado esperado:
- `README.generated.md` actualizado (o la ruta definida en `outReadmePath` dentro de `tools/docgen/workflow_crearReadme/readme.config.json`).
