import argparse
import json
from pathlib import Path
from typing import Dict


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_all_literal(template: str, mapping: Dict[str, str]) -> str:
    result = template
    for key, value in mapping.items():
        result = result.replace(f"<{key}>", value)
    return result


def resolve_path(repo_root: Path, maybe_relative: str) -> Path:
    """
    Resuelve rutas aceptando:
    - absolutas
    - relativas a la raíz del repo (repo_root)
    - relativas al directorio actual (cwd), como fallback (útil cuando se invoca desde la raíz del repo)
    """
    p = Path(maybe_relative)
    if p.is_absolute():
        return p

    # Primero intentamos relativo al directorio actual (comportamiento esperado al ejecutar desde la raíz del repo)
    cwd_candidate = Path.cwd() / p
    if cwd_candidate.exists():
        return cwd_candidate

    # Fallback: relativo a la raíz del repo calculada desde la ubicación del script
    return repo_root / p


def build_optional_templates(cfg: dict) -> Dict[str, str]:
    """
    Replica los bloques opcionales del generador HTML:
    - <TEMPLATE_KUDU>
    - <TEMPLATE_SOLR>
    - <TEMPLATE_KERBEROS_KUDU> (solo si Kudu está activo)
    """
    include_kudu = bool(cfg.get("includeKudu", False))
    include_solr = bool(cfg.get("includeSolr", False))
    kudu_keytab = (cfg.get("kuduKeytab") or "").strip()

    template_kudu = ""
    template_kerberos_kudu = ""
    if include_kudu:
        template_kudu = "\n".join(
            [
                "#### Configuración de Kudu",
                "Especifica las direcciones del servidor Kudu y las configuraciones de seguridad. El `realm` indica el dominio de Kerberos, y el `username` se utiliza para la autenticación. La sección `path` proporciona las rutas a los archivos de configuración de Kerberos necesarios, incluyendo `krb5.conf`, la configuración de JAAS y el archivo keytab para la autenticación",
                "",
                "    kudu:",
                "      server: ld6mk01.es.wcorp.carrefour.com:7051,ld6mk02.es.wcorp.carrefour.com:7051,ld6mk03.es.wcorp.carrefour.com:7051",
                "      security:",
                "        realm: ES.WCORP.CARREFOUR.COM",
                "        username: ms_dev_suply",
                "        path:",
                "          krb5: /etc/kerberos/conf/krb5.conf",
                "          jaas: /etc/kerberos/jaas/kerberos.jaas",
                f"          keytab: /etc/kerberos/keytab/{kudu_keytab}.keytab"
                if kudu_keytab
                else "          keytab: /etc/kerberos/keytab/<KUDU_KEYTAB>.keytab",
            ]
        )

        template_kerberos_kudu = "\n".join(
            [
                "  kudu:",
                "    realm: ES.WCORP.CARREFOUR.COM",
                "    username: ms_dev_mdata",
                f"    keytabPath: /etc/kerberos/keytab/{kudu_keytab}.keyta"
                if kudu_keytab
                else "    keytabPath: /etc/kerberos/keytab/<KUDU_KEYTAB>.keyta",
            ]
        )

    template_solr = ""
    if include_solr:
        template_solr = "\n".join(
            [
                "### Configuración de Solr",
                "Configura los hosts de Zookeeper para Solr, permitiendo que la aplicación se conecte al servicio de Solr para la indexación y búsqueda de datos.",
                "",
                "    data:",
                "      solr:",
                "        zk-host: ld6mk01.es.wcorp.carrefour.com:2181,ld6mk02.es.wcorp.carrefour.com:2181,ld6mk03.es.wcorp.carrefour.com:2181",
            ]
        )

    return {
        "TEMPLATE_KUDU": template_kudu.strip(),
        "TEMPLATE_SOLR": template_solr.strip(),
        "TEMPLATE_KERBEROS_KUDU": template_kerberos_kudu.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera README a partir de plantilla + config + modelo de datos.")
    parser.add_argument(
        "--config",
        default="tools/docgen/workflow_crearReadme/readme.config.json",
        help="Ruta al JSON de configuración",
    )
    args = parser.parse_args()

    # raíz del repo calculada desde la ubicación del script
    # __file__ = <repo>/tools/docgen/workflow_crearReadme/generate_readme.py
    # parents[4] = <repo>
    repo_root = Path(__file__).resolve().parents[4]

    config_path = resolve_path(repo_root, args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"No existe config: {config_path}")

    cfg = json.loads(read_text(config_path))

    template_path = resolve_path(
        repo_root,
        cfg.get("templatePath", "tools/docgen/workflow_crearReadme/readme.template.md"),
    )
    if not template_path.exists():
        raise FileNotFoundError(f"No existe template: {template_path}")

    modelo_datos_path = resolve_path(repo_root, cfg.get("modeloDatosPath", "docs/modelo-datos.md"))
    modelo_datos = read_text(modelo_datos_path).strip() if modelo_datos_path.exists() else ""

    # README generado: por defecto en raíz del repo
    out_path = resolve_path(repo_root, cfg.get("outReadmePath", "README.generated.md"))

    optional = build_optional_templates(cfg)

    mapping = {
        "NOMBRE_MICRO": (cfg.get("nombreMicro") or "").strip(),
        "DESC_MICRO": (cfg.get("descMicro") or "").strip(),
        "URL_DEL_REPOSITORIO": (cfg.get("urlRepo") or "").strip(),
        "NOMBRE_DEL_JAR": (cfg.get("nombreJar") or "").strip()
        or ((cfg.get("nombreMicro") or "").strip() + ".jar" if (cfg.get("nombreMicro") or "").strip() else ""),
        "APP_NAME": (cfg.get("appName") or "").strip() or (cfg.get("nombreMicro") or "").strip(),
        "APP_MODULEID": (cfg.get("appModuleId") or "").strip() or (cfg.get("nombreMicro") or "").strip(),
        "EXTERNAL_HOSTNAME": (cfg.get("externalHostname") or "").strip(),
        "MAX_CPU": str(cfg.get("maxCpu") or "").strip(),
        "MIN_CPU": str(cfg.get("minCpu") or "").strip(),
        "MAX_MEM": str(cfg.get("maxMem") or "").strip(),
        "MIN_MEM": str(cfg.get("minMem") or "").strip(),
        "MODELO_DATOS": modelo_datos,
        **optional,
    }

    template = read_text(template_path)
    rendered = replace_all_literal(template, mapping).rstrip() + "\n"

    write_text(out_path, rendered)
    print(f"README generado: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
