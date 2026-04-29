#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de inventario de clases Java + marcador de "entidad" para IA (v3)

Objetivo v3:
- Producir una lista suficientemente amplia de clases "candidatas" para que un plugin/IA
  pueda decidir cuáles son entidades y cuáles no.
- Mantener un marcador determinista basado en anotaciones JPA (@Entity/@Embeddable/@MappedSuperclass).
- Evitar ruido obvio: excluir por defecto componentes típicos de capa web/servicios/repositorio
  (Controller/Service/Repository/etc.) salvo que se fuerce su inclusión.
- Permitir incluir clases sin campos con --include-empty-classes (útil para clasificación por IA).

Requisitos:
  - Python 3.9+
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional


# Resolver rutas de forma estable aunque se ejecute desde cualquier CWD
REPO_ROOT = Path(__file__).resolve().parents[4]
GENERATED_ROOT = REPO_ROOT / "generated"

PROMPT_DEFAULT = REPO_ROOT / "tools/docgen/workflow_crearReadme/modelo-datos.prompt.md"
JAVA_FILE_GLOB = "**/*.java"

# Heurística para identificar clases "de modelo" comunes por nombre
DEFAULT_CLASS_INCLUDE = re.compile(r".*\b(Entity|Model|DTO|DO|PO|VO)\b.*", re.IGNORECASE)

# Excluir ruido "obvio" por nombre (configurable)
DEFAULT_CLASS_EXCLUDE = re.compile(
    r".*\b("
    r"Controller|RestController|Advice|ExceptionHandler|"
    r"Service|ApplicationService|"
    r"Repository|Dao|DAO|"
    r"Config|Configuration|Properties|"
    r"Filter|Interceptor|Aspect|"
    r"Security|Authenticator|Authorization|"
    r"Mapper|Converter|Assembler|Factory|Builder|"
    r"Test|Tests"
    r")\b.*",
    re.IGNORECASE,
)

CLASS_DECL_RE = re.compile(
    r"(?m)^[ \t]*(public\s+)?(final\s+)?(abstract\s+)?(class|record)\s+(?P<name>[A-Za-z_]\w*)\b"
)

PACKAGE_RE = re.compile(r"(?m)^[ \t]*package\s+(?P<pkg>[\w.]+)\s*;")

# JPA annotations (cubre javax y jakarta)
ENTITY_ANNOTATION_RE = re.compile(
    r"(?m)^[ \t]*@(?:(?:javax|jakarta)\.persistence\.)?(Entity|Embeddable|MappedSuperclass)\b"
)

GETTER_RE = re.compile(
    r"""(?mx)
    ^[ \t]*
    (public|protected)\s+
    (?P<type>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\s*<[^>]+>)?)\s+
    (?P<name>get[A-Z]\w*|is[A-Z]\w*)\s*
    \(\s*\)
    (?:\s*throws\s+[^{]+)?
    \s*\{
    """
)

FIELD_RE = re.compile(
    r"""(?mx)
    ^[ \t]*
    (?P<mods>(public|protected|private|static|final|transient|volatile|\s)+)?
    [ \t]*
    (?P<type>
        (?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*
        (?:\s*<[^;>{}]+>)?
        (?:\s*\[\s*\])?
    )
    [ \t]+
    (?P<name>[A-Za-z_]\w*)
    [ \t]*
    (?:=\s*[^;]+)?
    ;
    """
)

APIMODELPROPERTY_RE = re.compile(
    r"""@ApiModelProperty\s*\(\s*(?:value\s*=\s*)?(?P<q>"[^"]*"|'[^']*')""",
    re.MULTILINE,
)

SCHEMA_RE = re.compile(
    r"""@Schema\s*\(\s*(?:description\s*=\s*)?(?P<q>"[^"]*"|'[^']*')""",
    re.MULTILINE,
)


def _unquote(s: str) -> str:
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def _clean_javadoc(block: str) -> str:
    inner = block.strip()
    inner = inner.lstrip("/").lstrip("*").strip()
    inner = inner.rstrip("/").rstrip("*").strip()
    lines = []
    for line in inner.splitlines():
        line = line.strip()
        if line.startswith("*"):
            line = line[1:].strip()
        if line:
            lines.append(line)
    return " ".join(lines).strip()


@dataclass
class JavaField:
    name: str
    type: str
    description: Optional[str] = None


@dataclass
class JavaClass:
    name: str
    package: Optional[str]
    fields: List[JavaField] = field(default_factory=list)
    source: str = ""  # para embebido en ENTIDADES_MICRO
    is_jpa_entity: bool = False
    file: Optional[str] = None


def iter_java_files(src_dirs: List[Path]) -> Iterable[Path]:
    for src in src_dirs:
        if not src.exists():
            continue
        yield from src.glob(JAVA_FILE_GLOB)


def _extract_public_class_source(class_block: str) -> str:
    return class_block.strip() + "\n"


def _getter_to_field_name(method_name: str) -> Optional[str]:
    if method_name == "getClass":
        return None
    if method_name.startswith("get") and len(method_name) > 3:
        raw = method_name[3:]
    elif method_name.startswith("is") and len(method_name) > 2:
        raw = method_name[2:]
    else:
        return None
    return raw[0].lower() + raw[1:] if raw else None


def _extract_getters_as_fields(class_block: str) -> List[JavaField]:
    fields: List[JavaField] = []
    lines = class_block.splitlines()

    pending_javadoc: Optional[str] = None
    pending_desc: Optional[str] = None

    i = 0
    while i < len(lines):
        line = lines[i]

        if "/**" in line:
            buf = [line]
            i += 1
            while i < len(lines) and "*/" not in lines[i]:
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                buf.append(lines[i])
            pending_javadoc = _clean_javadoc("\n".join(buf))
            i += 1
            continue

        m_schema = SCHEMA_RE.search(line)
        if m_schema:
            pending_desc = _unquote(m_schema.group("q"))
            i += 1
            continue

        m_api = APIMODELPROPERTY_RE.search(line)
        if m_api:
            pending_desc = _unquote(m_api.group("q"))
            i += 1
            continue

        m_get = GETTER_RE.match(line)
        if m_get:
            mname = m_get.group("name")
            fname = _getter_to_field_name(mname)
            if fname:
                ftype = re.sub(r"\s+", " ", m_get.group("type")).strip()
                desc = pending_desc or pending_javadoc
                fields.append(JavaField(name=fname, type=ftype, description=desc))
            pending_desc = None
            pending_javadoc = None

        i += 1

    return fields


def _extract_fields_with_descriptions(class_block: str) -> List[JavaField]:
    lines = class_block.splitlines()
    fields: List[JavaField] = []

    pending_desc: Optional[str] = None
    pending_javadoc: Optional[str] = None

    i = 0
    while i < len(lines):
        line = lines[i]

        if "/**" in line:
            buf = [line]
            i += 1
            while i < len(lines) and "*/" not in lines[i]:
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                buf.append(lines[i])
            pending_javadoc = _clean_javadoc("\n".join(buf))
            i += 1
            continue

        m_schema = SCHEMA_RE.search(line)
        if m_schema:
            pending_desc = _unquote(m_schema.group("q"))
            i += 1
            continue

        m_api = APIMODELPROPERTY_RE.search(line)
        if m_api:
            pending_desc = _unquote(m_api.group("q"))
            i += 1
            continue

        m_field = FIELD_RE.match(line)
        if m_field:
            name = m_field.group("name")
            ftype = re.sub(r"\s+", " ", m_field.group("type")).strip()
            desc = pending_desc or pending_javadoc
            fields.append(JavaField(name=name, type=ftype, description=desc))
            pending_desc = None
            pending_javadoc = None

        i += 1

    return fields


def parse_java_file(path: Path) -> List[JavaClass]:
    text = path.read_text(encoding="utf-8", errors="ignore")

    pkg_m = PACKAGE_RE.search(text)
    pkg = pkg_m.group("pkg") if pkg_m else None

    classes: List[JavaClass] = []
    for cls_match in CLASS_DECL_RE.finditer(text):
        cls_name = cls_match.group("name")

        start = cls_match.start()
        block = text[start:]
        open_idx = block.find("{")
        if open_idx == -1:
            continue

        i = open_idx
        depth = 0
        end = None
        while i < len(block):
            ch = block[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
            i += 1

        class_block = block[:end] if end else block

        # Las anotaciones como @Entity suelen estar antes de la declaración de clase,
        # así que revisamos también un "prefijo" del fichero anterior a la clase.
        prefix = text[max(0, start - 2000) : start]
        is_jpa_entity = bool(ENTITY_ANNOTATION_RE.search(prefix)) or bool(
            ENTITY_ANNOTATION_RE.search(class_block)
        )

        java_class = JavaClass(
            name=cls_name,
            package=pkg,
            source=_extract_public_class_source(class_block),
            is_jpa_entity=is_jpa_entity,
            file=str(path).replace("\\", "/"),
        )

        fields = _extract_fields_with_descriptions(class_block)
        getters = _extract_getters_as_fields(class_block)

        by_name: dict[str, JavaField] = {f.name: f for f in fields}
        for g in getters:
            if g.name not in by_name:
                by_name[g.name] = g

        java_class.fields = list(by_name.values())
        classes.append(java_class)

        # evitar inner classes (igual que v2)
        break

    return classes


def should_include_class(
    java_class: JavaClass,
    include_regex: re.Pattern | None,
    exclude_regex: re.Pattern | None,
    include_jpa_only: bool,
) -> bool:
    # 1) Si el usuario fuerza include_regex, se respeta (y el exclude se ignora, para no sorprender).
    if include_regex is not None:
        return bool(include_regex.match(java_class.name))

    # 2) Si el usuario quiere solo JPA, filtrar a eso.
    if include_jpa_only:
        return java_class.is_jpa_entity

    # 3) Excluir por nombre "obvio" (controllers, services, etc.)
    if exclude_regex is not None and exclude_regex.match(java_class.name):
        return False

    # 4) Prioridad: si es JPA, incluir siempre
    if java_class.is_jpa_entity:
        return True

    # 5) fallback heurística por nombre (model/DTO/VO/...)
    return bool(DEFAULT_CLASS_INCLUDE.match(java_class.name))


def build_entidades_micro(classes: List[JavaClass]) -> str:
    parts = []
    for c in classes:
        header = ""
        if c.package:
            header += f"package {c.package};\n\n"
        parts.append(header + c.source.strip() + "\n")
    return "\n\n".join(parts).strip() + "\n"


def build_entities_json(classes: List[JavaClass]) -> str:
    import json

    payload = []
    for c in classes:
        payload.append(
            {
                "name": c.name,
                "package": c.package,
                "file": c.file,
                "isJpaEntity": c.is_jpa_entity,
                "fields": [{"name": f.name, "type": f.type, "description": f.description} for f in c.fields],
            }
        )

    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_prompt(template_path: Path, entidades_micro: str, entities_json: str) -> str:
    template = template_path.read_text(encoding="utf-8")
    result = template.replace("{{ENTIDADES_MICRO}}", entidades_micro)
    result = result.replace("{{ENTIDADES_JSON}}", entities_json)
    return result


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description='Genera prompt final + JSON de inventario para "Modelo de datos" (v3).'
    )
    p.add_argument(
        "--src",
        action="append",
        required=True,
        help="Directorio raíz donde buscar .java (puede repetirse)",
    )
    p.add_argument("--prompt-template", default=str(PROMPT_DEFAULT), help="Plantilla de prompt .md")
    p.add_argument("--mode", choices=["prompt"], default="prompt", help="Modo de ejecución")

    p.add_argument(
        "--out-dir",
        default="generated/docgen/modelo-datos",
        help="Directorio base donde escribir las salidas por defecto (si no se especifican --out-prompt/--out-entities-json).",
    )

    p.add_argument(
        "--include-class-regex",
        default=None,
        help='Regex para filtrar nombres de clase a incluir (si se usa, ignora --exclude-class-regex)',
    )
    p.add_argument(
        "--exclude-class-regex",
        default=str(DEFAULT_CLASS_EXCLUDE.pattern),
        help="Regex para excluir por nombre de clase (por defecto excluye controllers/services/repos/etc.)",
    )
    p.add_argument(
        "--include-jpa-only",
        action="store_true",
        help="Si se activa, solo incluye clases JPA (@Entity/@Embeddable/@MappedSuperclass).",
    )
    p.add_argument(
        "--include-empty-classes",
        action="store_true",
        help="Si se activa, incluye clases aunque no se detecten campos/getters.",
    )

    p.add_argument(
        "--out-prompt",
        default=None,
        help="Salida del prompt final. Si no se especifica, se generará en --out-dir.",
    )
    p.add_argument(
        "--out-entities-json",
        default=None,
        help="Salida JSON con entidades/campos (para prompts más limpios). Si no se especifica, se generará en --out-dir.",
    )
    args = p.parse_args(argv)

    src_dirs = [Path(s) if Path(s).is_absolute() else (REPO_ROOT / Path(s)) for s in args.src]
    template_path = (
        Path(args.prompt_template)
        if Path(args.prompt_template).is_absolute()
        else (REPO_ROOT / Path(args.prompt_template))
    )

    include_re = re.compile(args.include_class_regex) if args.include_class_regex else None
    exclude_re = re.compile(args.exclude_class_regex) if args.exclude_class_regex else None

    classes: List[JavaClass] = []
    for f in iter_java_files(src_dirs):
        for c in parse_java_file(f):
            if should_include_class(c, include_re, exclude_re, args.include_jpa_only):
                if args.include_empty_classes or c.fields:
                    classes.append(c)

    if not classes:
        print(
            "No se han encontrado clases candidatas. Ajusta --include-class-regex/--exclude-class-regex o --src.",
            file=sys.stderr,
        )
        return 2

    entidades_micro = build_entidades_micro(classes)
    entities_json = build_entities_json(classes)

    out_dir = Path(args.out_dir) if Path(args.out_dir).is_absolute() else (REPO_ROOT / Path(args.out_dir))

    out_entities = (
        (Path(args.out_entities_json) if Path(args.out_entities_json).is_absolute() else (REPO_ROOT / Path(args.out_entities_json)))
        if args.out_entities_json
        else (out_dir / "modelo-datos.entities.v3.json")
    )
    out_entities.parent.mkdir(parents=True, exist_ok=True)
    out_entities.write_text(entities_json, encoding="utf-8")

    prompt = render_prompt(template_path, entidades_micro, entities_json)

    out_prompt = (
        (Path(args.out_prompt) if Path(args.out_prompt).is_absolute() else (REPO_ROOT / Path(args.out_prompt)))
        if args.out_prompt
        else (out_dir / "modelo-datos.prompt.final.v3.md")
    )
    out_prompt.parent.mkdir(parents=True, exist_ok=True)
    out_prompt.write_text(prompt, encoding="utf-8")
    print(f"Prompt final generado: {out_prompt}")
    print(f"Entities JSON generado: {out_entities}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
