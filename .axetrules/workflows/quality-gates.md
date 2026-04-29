# Quality Gates — Policy (Agent-first)

Este documento define **quality-gates** y **reglas operativas** para los workflows de `.axetrules`.

> Objetivo: estandarizar cómo trabajamos con el asistente para asegurar cambios seguros, verificables y trazables.
>
> Importante: esto es **policy documental** (no enforcement automático). Los workflows deben referenciarlo.

---

## 0) Defaults del sistema (obligatorios)

### Idioma por defecto
- **Idioma de comunicación por defecto**: `es-ES`.
- Si el usuario escribe en otro idioma, el asistente mantiene el idioma de esa iteración, salvo que el usuario pida explícitamente cambiarlo.

### Seguridad por defecto (evitar acciones peligrosas)
- **No ejecutar comandos `git` por iniciativa propia**.
- Cualquier comando potencialmente destructivo debe evitarse (ej. `rm`, `del`, `rmdir`, `git reset --hard`, `git clean -fd`, etc.).
- Si se requiere ver diffs/estado:
  - Preferencia: pedir al usuario que pegue salida de `git diff` / `git status`.
  - Si el usuario pide expresamente que el asistente lo ejecute, usar solo comandos “read-only”.

> Nota: En este repositorio existen herramientas para ejecutar comandos, pero la policy define el comportamiento esperado del asistente.

---

## 1) Pre-flight gate (antes de empezar un paso)

Antes de actuar sobre cualquier paso de un workflow:

- [ ] Confirmar el **paso** que se va a ejecutar (solo 1 paso a la vez).
- [ ] Confirmar el **objetivo** del paso en una frase.
- [ ] Confirmar el **artefacto de evidencia** esperado (link, logs, salida de test, captura, etc.).
- [ ] Confirmar si el paso requiere:
  - [ ] Cambios en código
  - [ ] Cambios en configuración
  - [ ] Ejecución de comandos (Gradle, etc.)
  - [ ] Acceso a red / sistemas externos (normalmente N/A desde el asistente)

---

## 2) Evidence gate (para poder marcar un paso como completado)

Un paso solo puede marcarse como `[x]` si hay evidencia mínima en `Notas:` del tracking:

Ejemplos válidos de evidencia (elige 1 o más):
- URL a runbook / documentación seguida
- Resultado de un test (`./gradlew test` / informe)
- ID de despliegue / ticket / PR
- Extracto de logs relevante
- Captura o resultado de endpoint (request/response)

Formato recomendado en `Notas:`:
- **Qué se hizo**
- **Resultado**
- **Evidencia (link/copia de output)**

---

## 3) Gate de verificación técnica (según tipo de cambio)

### Si hay cambios de código
- [ ] Compila / tests según aplique (mínimo recomendado):
  - `./gradlew test` (o suite acotada si está acordado)
- [ ] No dejar el proyecto en estado inconsistente (tests rotos sin justificar).

### Si hay cambios en workflows/tracking (`.axetrules/**`)
- [ ] Verificar que el workflow:
  - [ ] referencia este documento si aplica
  - [ ] tiene checklist claro
  - [ ] permite interacción del usuario (marcar pasos, añadir notas)

### Si hay cambios de configuración (YAML/JSON)
- [ ] Validar sintaxis (lint o verificación manual)
- [ ] Anotar impacto y rollback

---

## 4) Gate de comunicación (salida estándar del asistente)

Cuando el asistente finaliza una iteración/paso, debe dejar:

- Resumen (1-3 bullets)
- Archivos tocados (si aplica)
- Evidencia generada/recogida (si aplica)
- Siguientes pasos (si están en el workflow)

---

## 5) Regla de “una cosa cada vez”
- Solo una tarea/paso por iteración.
- Evitar mezclar cambios de distinta naturaleza en un mismo paso (ej. refactor + migración + sonar).

---

## 6) Plantilla rápida (para pegar en un workflow)

Pega esto al inicio de un workflow:

> **Pre-flight**: aplicar `.axetrules/workflows/quality-gates.md`  
> Defaults: idioma `es-ES`, no ejecutar `git` por defecto, evidencia obligatoria para marcar `[x]`.
