
# Workflow — Migración de micro (Agent-first)

Workflow “macro” para guiar una migración de microservicio paso a paso, permitiendo que el usuario **marque qué pasos están completados** y reanude el trabajo fácilmente.

> **Objetivo:** convertir una lista de tareas de migración en un checklist ejecutable y trazable dentro de `.axetrules/`. Tras cada paso completado, se generará un artefacto en la carpeta de historial para mantener un registro de auditoría.

---

## Artefactos

### Tracking (fuente de verdad)
- **`.axetrules/micro-migration/micro-migration.md`**
  - Checklist editable por el usuario.
  - El agente lo lee al inicio de cada iteración para decidir el “siguiente paso [ ]”.

### Registro de Historial (Artefactos de ejecución)
- **`.axetrules/history/<YYYY-MM-DD-ejecucion>/`**
  - Carpeta creada por cada ejecución/fecha.
  - Contendrá los resúmenes de cada paso (ej: `01-endpoints-report.md`, `05-coverage-summary.md`).

### Workflows reutilizados
- [cite_start]**Pruebas de Endpoints** → `.axetrules/workflows/endpoint-testing.md` [cite: 3, 6]
- **Aumentar cobertura de tests** → `.axetrules/workflows/unit-tests.md`
- **Generación de Modelo de Datos/README** → `.axetrules/workflows/modelo-datos.instrucciones.v3.end2end.md`
- **Tareas Sonar** → `.axetrules/workflows/sonar-codesmells.md`

---

## Cómo se usa (operativa)

1. Crear (o actualizar) el fichero de tracking:
    - `.axetrules/micro-migration/micro-migration.md`
2. Ejecutar el workflow con:
    - `/workflow micro-migration`
3. Interacción:
    - El agente propondrá el **siguiente paso pendiente** y pedirá confirmación.
    - Al finalizar un paso técnico, el agente generará automáticamente el artefacto de resumen en la carpeta `history` correspondiente.

---

## Plantilla de tracking (copiar a `.axetrules/micro-migration/micro-migration.md`)

> Si el fichero ya existe, **no lo sobreescribas**; actualízalo.

```md
# Micro migration — Tracking

> **Pre-flight**: aplicar `.axetrules/workflows/quality-gates.md`  
> Defaults: idioma `es-ES`, no ejecutar `git` por defecto, evidencia obligatoria para marcar `[x]`.

Micro/Repo: <pendiente>
Fecha inicio: <YYYY-MM-DD>
Responsable: <pendiente>

## Checklist

- [ ] 1. Pruebas endpoints pre-migración
  - Workflow: .axetrules/workflows/endpoint-testing.md
  - Notas:

- [ ] 2. Modificaciones pre-migración
  - Referencia: Pedir al humano que ejecute las tareas premigracion
  - Notas:

- [ ] 3. Migración
  - Referencia: Pedir al humano que ejecute migracion
  - Notas:

- [ ] 4. Modificaciones post-migración
  - Referencia: Pedir al humano que ejecute tareas postmigracion incluyendo generar README
  - Notas:

- [ ] 5. Aumentar cobertura de tests
  - Workflow: .axetrules/workflows/unit-tests.md
  - Notas:

- [ ] 6. Tareas sonar
  - Workflow: .axetrules/workflows/sonar-codesmells.md
  - Notas:

- [ ] 7. Superar prisma
  - Referencia: Pedir al humano que confirme que superamos prisma
  - Notas:

- [ ] 8. Validación final y Documentación
  - Workflow 8.1 (Endpoints): .axetrules/workflows/endpoint-testing.md
  - Workflow 8.2 (Data Model/README): .axetrules/workflows/modelo-datos.instrucciones.v3.end2end.md
  - Notas:

## Historial
- <YYYY-MM-DD> - <persona> - <cambio>
```

---

## Algoritmo de ejecución (para el agente)

En cada invocación de `/workflow micro-migration`:

1.  **Inicialización de Historia:** Crear (si no existe) la carpeta `.axetrules/history/<YYYY-MM-DD-micro-migration>/` para almacenar los artefactos de la sesión actual.
2.  **Lectura de Tracking:** Leer `.axetrules/micro-migration/micro-migration.md`. Si no existe, crearlo usando la plantilla.
3.  **Localización de Tarea:** Localizar el **primer item** con `- [ ]`.
4.  **Ejecución de Lógica:**
    -   **Si es (1) o (8.1) Endpoints:** Iniciar `.axetrules/workflows/endpoint-testing.md`. [cite_start]Al terminar, guardar el reporte en `history`[cite: 203].
    -   **Si es (5) Cobertura:** Iniciar `.axetrules/workflows/unit-tests.md`. Al terminar, generar un resumen de cobertura en `history`.
    -   **Si es (6) Sonar:** Iniciar `.axetrules/workflows/sonar-codesmells.md`.
    -   **Si es (8.2) Documentación:** Iniciar `.axetrules/workflows/modelo-datos.instrucciones.v3.end2end.md` para generar el modelo de datos y actualizar el README.
    -   **Si es un paso manual (2, 3, 4, 7):**
        - Mostrar al humano la `Referencia:` y las `Notas:`.
        - Esperar confirmación de ejecución manual.
5.  **Cierre de Tarea:**
    -   Tras completar cualquier paso, generar un **artefacto resumen** en la carpeta de historia con el formato `paso-XX-resumen.md`.
    -   Marcar el item como `[x]` en el tracking y registrar la entrada en el “Historial” del documento.
6.  **Siguiente Paso:** Preguntar si se desea continuar con el siguiente paso pendiente o terminar la sesión.

---

## Reglas de oro

- **Trazabilidad Obligatoria:** No marcar un paso como completado sin haber generado su correspondiente artefacto explicativo en la carpeta de `history`.
- **El tracking manda:** No inventar información; si falta un runbook/enlace, dejarlo como `<pendiente>`.
- **Interacción en pasos manuales:** El agente solo muestra instrucciones y espera confirmación para avanzar.
- **Atomicidad:** Se recomienda procesar un paso técnico complejo por iteración para asegurar la estabilidad del contexto.