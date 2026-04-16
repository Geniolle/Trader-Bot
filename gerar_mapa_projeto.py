
#!/usr/bin/env python3
"""
Gerador automático de mapa do projeto.

Objetivo:
- varrer a raiz do projeto
- identificar ficheiros, imports, classes, funções, endpoints e integrações
- montar relações internas entre ficheiros
- escrever um mapa atualizado sempre que for executado

Também suporta modo --watch para atualizar continuamente.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_OUTPUT = "MAPA_DO_PROJETO.md"
DEFAULT_CACHE = ".project_map_cache.json"

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".turbo",
    ".cache",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".parcel-cache",
    ".DS_Store",
}

DEFAULT_INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".md",
}

ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "websocket"}

PYTHON_ROUTE_RE = re.compile(
    r"@\s*(?:\w+\.)?(get|post|put|patch|delete|options|head|websocket)\s*\(\s*([\"'])(.*?)\2",
    re.IGNORECASE,
)

JS_IMPORT_RE = re.compile(
    r"""(?:import\s+[^;]*?\s+from\s+|import\s*\(\s*|require\s*\(\s*)(["'])(.*?)\1""",
    re.MULTILINE,
)

FETCH_URL_RE = re.compile(
    r"""(?:fetch|axios\.(?:get|post|put|patch|delete)|axios)\s*\(\s*(["'])(.*?)\1""",
    re.MULTILINE,
)

WEBSOCKET_RE = re.compile(
    r"""new\s+WebSocket\s*\(\s*(["'])(.*?)\1""",
    re.MULTILINE,
)

HTTP_URL_RE = re.compile(r"""https?://[^\s"'`)>]+""")
WS_URL_RE = re.compile(r"""wss?://[^\s"'`)>]+""")

COMMENT_LINE_RE = re.compile(r"^\s*(#|//)")
FASTAPI_ROUTER_PREFIX_RE = re.compile(
    r"""APIRouter\s*\(\s*prefix\s*=\s*(["'])(.*?)\1""",
    re.MULTILINE,
)


@dataclass
class EndpointInfo:
    method: str
    path: str
    source: str


@dataclass
class FileInfo:
    path: str
    language: str
    category: str
    size_bytes: int
    line_count: int
    non_empty_line_count: int
    comment_line_count: int
    sha1: str
    imports_raw: list[str] = field(default_factory=list)
    uses_files: list[str] = field(default_factory=list)
    imported_by: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    endpoints: list[EndpointInfo] = field(default_factory=list)
    outbound_http: list[str] = field(default_factory=list)
    outbound_ws: list[str] = field(default_factory=list)
    probable_role: str = ""
    summary: str = ""
    warnings: list[str] = field(default_factory=list)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def safe_read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def sha1_text(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8", errors="replace")).hexdigest()


def count_comment_lines(text: str) -> int:
    total = 0
    for line in text.splitlines():
        if COMMENT_LINE_RE.match(line):
            total += 1
    return total


def normalize_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def guess_language(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript-react",
        ".ts": "typescript",
        ".tsx": "typescript-react",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".md": "markdown",
    }.get(suffix, "text")


def guess_category(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()

    if name in {"main.py", "main.tsx", "main.ts", "app.py"}:
        return "entrypoint"
    if "endpoint" in parts or "api" in parts:
        return "api"
    if "provider" in parts or "providers" in parts:
        return "provider"
    if "repository" in name or "repositories" in parts:
        return "repository"
    if "storage" in parts or "database" in name:
        return "storage"
    if "schema" in name or "schemas" in parts:
        return "schema"
    if "model" in name or "models" in parts:
        return "model"
    if "strategy" in name or "strategies" in parts:
        return "strategy"
    if "engine" in name or "engine" in parts:
        return "engine"
    if "hook" in name or "hooks" in parts:
        return "hook"
    if "component" in parts or "components" in parts:
        return "component"
    if "service" in name or "services" in parts:
        return "service"
    if "config" in name or "settings" in name or "constants" in parts:
        return "config"
    if path.suffix.lower() == ".md":
        return "documentation"
    return "source"


def looks_like_binary_or_too_large(path: Path, max_bytes: int) -> bool:
    try:
        if path.stat().st_size > max_bytes:
            return True
        with path.open("rb") as fh:
            sample = fh.read(2048)
        return b"\x00" in sample
    except OSError:
        return True


def iter_project_files(root: Path, include_extensions: set[str], ignore_dirs: set[str]) -> Iterable[Path]:
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".git")]
        current_root_path = Path(current_root)
        for filename in filenames:
            path = current_root_path / filename
            if path.name.startswith(".") and path.suffix.lower() not in {".env"}:
                continue
            if path.suffix.lower() not in include_extensions:
                continue
            yield path


def extract_python_imports(tree: ast.AST) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level > 0:
                prefix = "." * node.level
                imports.append(f"{prefix}{module}" if module else prefix)
            elif module:
                imports.append(module)
    return sorted(set(imports))


def extract_python_classes_functions(tree: ast.AST) -> tuple[list[str], list[str]]:
    classes: list[str] = []
    functions: list[str] = []
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
    return classes, functions


def extract_python_router_prefix(text: str) -> str:
    match = FASTAPI_ROUTER_PREFIX_RE.search(text)
    if not match:
        return ""
    return match.group(2).strip()


def extract_python_endpoints(tree: ast.AST, text: str) -> list[EndpointInfo]:
    endpoints: list[EndpointInfo] = []
    router_prefix = extract_python_router_prefix(text)

    for node in tree.body if isinstance(tree, ast.Module) else []:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            method = None
            if isinstance(func, ast.Attribute) and func.attr.lower() in ROUTE_METHODS:
                method = func.attr.lower()
            elif isinstance(func, ast.Name) and func.id.lower() in ROUTE_METHODS:
                method = func.id.lower()
            if not method:
                continue

            route_path = ""
            if decorator.args:
                first = decorator.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    route_path = first.value
            if not route_path:
                for kw in decorator.keywords:
                    if kw.arg == "path" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                        route_path = kw.value.value
                        break

            full_path = f"{router_prefix}{route_path}" if router_prefix or route_path else router_prefix or route_path
            endpoints.append(
                EndpointInfo(
                    method=method.upper(),
                    path=full_path or "/",
                    source=node.name,
                )
            )

    if endpoints:
        return endpoints

    # fallback por regex se o AST não capturou algo
    for match in PYTHON_ROUTE_RE.finditer(text):
        method = match.group(1).upper()
        route_path = match.group(3).strip()
        full_path = f"{router_prefix}{route_path}" if router_prefix or route_path else route_path
        endpoints.append(EndpointInfo(method=method, path=full_path or "/", source="decorator"))
    return endpoints


def extract_js_imports(text: str) -> list[str]:
    return sorted({m.group(2).strip() for m in JS_IMPORT_RE.finditer(text) if m.group(2).strip()})


def extract_functions_by_regex(text: str) -> list[str]:
    found = set()
    patterns = [
        re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\bconst\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\("),
        re.compile(r"\bexport\s+function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\bexport\s+const\s+([A-Za-z_][A-Za-z0-9_]*)\s*="),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            found.add(match.group(1))
    return sorted(found)


def extract_classes_by_regex(text: str) -> list[str]:
    return sorted({m.group(1) for m in re.finditer(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b", text)})


def extract_outbound_http(text: str) -> list[str]:
    urls = {m.group(2).strip() for m in FETCH_URL_RE.finditer(text) if m.group(2).strip()}
    urls.update(HTTP_URL_RE.findall(text))
    return sorted(urls)


def extract_outbound_ws(text: str) -> list[str]:
    urls = {m.group(2).strip() for m in WEBSOCKET_RE.finditer(text) if m.group(2).strip()}
    urls.update(WS_URL_RE.findall(text))
    return sorted(urls)


def python_module_candidates_from_path(path_str: str) -> set[str]:
    path = Path(path_str)
    if path.suffix != ".py":
        return set()
    without_suffix = path.with_suffix("")
    parts = without_suffix.parts
    candidates = {"/".join(parts) + ".py"}
    candidates.add(".".join(parts))
    if parts[-1] == "__init__":
        folder_parts = parts[:-1]
        if folder_parts:
            candidates.add("/".join(folder_parts) + "/__init__.py")
            candidates.add(".".join(folder_parts))
    return candidates


def resolve_python_import(import_name: str, current_path: str, all_files: set[str]) -> list[str]:
    results: set[str] = set()
    current_parts = Path(current_path).with_suffix("").parts

    if import_name.startswith("."):
        level = len(import_name) - len(import_name.lstrip("."))
        module = import_name[level:]
        base_parts = list(current_parts[:-1])

        if level > 0:
            base_parts = base_parts[: max(0, len(base_parts) - (level - 1))]

        if module:
            target_parts = base_parts + module.split(".")
            target_file = "/".join(target_parts) + ".py"
            init_file = "/".join(target_parts + ["__init__"]) + ".py"
            if target_file in all_files:
                results.add(target_file)
            if init_file in all_files:
                results.add(init_file)
        else:
            init_file = "/".join(base_parts + ["__init__"]) + ".py"
            if init_file in all_files:
                results.add(init_file)
        return sorted(results)

    parts = import_name.split(".")
    target_file = "/".join(parts) + ".py"
    init_file = "/".join(parts + ["__init__"]) + ".py"
    if target_file in all_files:
        results.add(target_file)
    if init_file in all_files:
        results.add(init_file)
    return sorted(results)


def resolve_js_import(import_name: str, current_path: str, all_files: set[str]) -> list[str]:
    if not import_name.startswith("."):
        return []

    current_dir = Path(current_path).parent
    base = (current_dir / import_name).as_posix()

    candidates = [
        base,
        f"{base}.ts",
        f"{base}.tsx",
        f"{base}.js",
        f"{base}.jsx",
        f"{base}.json",
        f"{base}/index.ts",
        f"{base}/index.tsx",
        f"{base}/index.js",
        f"{base}/index.jsx",
    ]

    return sorted({c for c in candidates if c in all_files})


def detect_probable_role(info: FileInfo, text: str) -> str:
    path_lower = info.path.lower()
    name = Path(info.path).name.lower()

    if info.category == "entrypoint":
        return "Ponto de entrada da aplicação"
    if info.endpoints:
        return "Expõe endpoints HTTP/WebSocket"
    if "apirouter" in text.lower():
        return "Configura roteamento da API"
    if info.category == "repository":
        return "Lê ou grava dados na camada de persistência"
    if info.category == "provider":
        return "Integra fontes externas de dados"
    if info.category == "engine":
        return "Orquestra lógica principal de execução"
    if info.category == "strategy":
        return "Implementa regras de estratégia"
    if info.category == "hook":
        if info.outbound_ws:
            return "Hook de frontend com consumo em tempo real"
        if info.outbound_http:
            return "Hook de frontend com consumo de API"
        return "Hook de frontend"
    if info.category == "component":
        return "Componente visual do frontend"
    if info.category == "config":
        return "Centraliza configurações e constantes"
    if info.category == "schema":
        return "Define contratos de dados e serialização"
    if info.category == "model":
        return "Define modelos de domínio ou persistência"
    if "test" in path_lower:
        return "Ficheiro de testes"
    if name == "readme.md":
        return "Documentação principal do projeto"
    if info.outbound_ws:
        return "Consome ou inicia comunicação WebSocket"
    if info.outbound_http:
        return "Consome API HTTP ou integração externa"
    if info.language in {"yaml", "toml", "json"}:
        return "Ficheiro de configuração/estrutura"
    if info.language == "markdown":
        return "Documentação"
    return "Lógica de suporte do projeto"


def build_summary(info: FileInfo) -> str:
    parts: list[str] = [info.probable_role]

    if info.endpoints:
        routes = ", ".join(f"{item.method} {item.path}" for item in info.endpoints[:5])
        parts.append(f"Rotas detectadas: {routes}")
    if info.classes:
        preview = ", ".join(info.classes[:6])
        parts.append(f"Classes principais: {preview}")
    if info.functions:
        preview = ", ".join(info.functions[:6])
        parts.append(f"Funções principais: {preview}")
    if info.outbound_http:
        preview = ", ".join(info.outbound_http[:4])
        parts.append(f"Integrações HTTP: {preview}")
    if info.outbound_ws:
        preview = ", ".join(info.outbound_ws[:4])
        parts.append(f"Integrações WS: {preview}")
    if info.uses_files:
        preview = ", ".join(info.uses_files[:6])
        parts.append(f"Depende de: {preview}")
    if info.imported_by:
        preview = ", ".join(info.imported_by[:6])
        parts.append(f"Referenciado por: {preview}")

    return ". ".join(part.strip().rstrip(".") for part in parts if part).strip() + "."


def analyze_file(root: Path, path: Path, max_bytes: int) -> FileInfo | None:
    if looks_like_binary_or_too_large(path, max_bytes=max_bytes):
        return None

    text = safe_read_text(path)
    rel_path = normalize_posix(path, root)
    language = guess_language(path)
    category = guess_category(path)

    line_count = text.count("\n") + (0 if not text else 1)
    non_empty_line_count = sum(1 for line in text.splitlines() if line.strip())
    comment_line_count = count_comment_lines(text)

    imports_raw: list[str] = []
    classes: list[str] = []
    functions: list[str] = []
    endpoints: list[EndpointInfo] = []
    outbound_http = extract_outbound_http(text)
    outbound_ws = extract_outbound_ws(text)
    warnings: list[str] = []

    if language == "python":
        try:
            tree = ast.parse(text, filename=rel_path)
            imports_raw = extract_python_imports(tree)
            classes, functions = extract_python_classes_functions(tree)
            endpoints = extract_python_endpoints(tree, text)
        except SyntaxError as exc:
            warnings.append(f"Falha ao analisar AST Python: {exc.msg} (linha {exc.lineno})")
            imports_raw = sorted(set(extract_js_imports(text)))
    elif language in {"javascript", "javascript-react", "typescript", "typescript-react"}:
        imports_raw = extract_js_imports(text)
        classes = extract_classes_by_regex(text)
        functions = extract_functions_by_regex(text)
    else:
        imports_raw = extract_js_imports(text)

    return FileInfo(
        path=rel_path,
        language=language,
        category=category,
        size_bytes=path.stat().st_size,
        line_count=line_count,
        non_empty_line_count=non_empty_line_count,
        comment_line_count=comment_line_count,
        sha1=sha1_text(text),
        imports_raw=imports_raw,
        classes=classes,
        functions=functions,
        endpoints=endpoints,
        outbound_http=outbound_http,
        outbound_ws=outbound_ws,
        warnings=warnings,
    )


def build_relationships(file_infos: dict[str, FileInfo]) -> None:
    all_files = set(file_infos.keys())

    for path, info in file_infos.items():
        resolved: set[str] = set()
        if info.language == "python":
            for item in info.imports_raw:
                resolved.update(resolve_python_import(item, path, all_files))
        elif info.language in {"javascript", "javascript-react", "typescript", "typescript-react"}:
            for item in info.imports_raw:
                resolved.update(resolve_js_import(item, path, all_files))
        info.uses_files = sorted(resolved)

    reverse_map: dict[str, list[str]] = defaultdict(list)
    for path, info in file_infos.items():
        for used in info.uses_files:
            reverse_map[used].append(path)

    for path, info in file_infos.items():
        info.imported_by = sorted(set(reverse_map.get(path, [])))
        # ordenar visualmente
        info.probable_role = detect_probable_role(info, "")
        # detect_probable_role needs text? patched below


def enrich_roles_and_summaries(root: Path, file_infos: dict[str, FileInfo], max_bytes: int) -> None:
    for path, info in file_infos.items():
        full_path = root / path
        text = safe_read_text(full_path) if full_path.exists() and full_path.stat().st_size <= max_bytes else ""
        info.probable_role = detect_probable_role(info, text)
        info.summary = build_summary(info)


def build_tree(paths: list[str]) -> str:
    tree: dict[str, dict] = {}
    for path in paths:
        node = tree
        for part in path.split("/"):
            node = node.setdefault(part, {})
    lines: list[str] = []

    def walk(subtree: dict, prefix: str = "") -> None:
        items = sorted(subtree.items(), key=lambda item: (not item[1], item[0].lower()))
        for index, (name, child) in enumerate(items):
            connector = "└── " if index == len(items) - 1 else "├── "
            lines.append(prefix + connector + name)
            extension = "    " if index == len(items) - 1 else "│   "
            walk(child, prefix + extension)

    walk(tree)
    return "\n".join(lines)


def build_overview(file_infos: dict[str, FileInfo]) -> dict[str, object]:
    by_language = Counter(info.language for info in file_infos.values())
    by_category = Counter(info.category for info in file_infos.values())
    endpoint_files = [info for info in file_infos.values() if info.endpoints]
    outbound_http_files = [info for info in file_infos.values() if info.outbound_http]
    outbound_ws_files = [info for info in file_infos.values() if info.outbound_ws]
    hot_spots = sorted(
        file_infos.values(),
        key=lambda item: (len(item.imported_by), len(item.uses_files), item.path.lower()),
        reverse=True,
    )

    return {
        "total_files": len(file_infos),
        "by_language": by_language,
        "by_category": by_category,
        "endpoint_files": endpoint_files,
        "outbound_http_files": outbound_http_files,
        "outbound_ws_files": outbound_ws_files,
        "hot_spots": hot_spots[:15],
    }


def render_markdown(root: Path, file_infos: dict[str, FileInfo], output_name: str) -> str:
    overview = build_overview(file_infos)
    endpoint_lines: list[str] = []
    for info in sorted(overview["endpoint_files"], key=lambda item: item.path.lower()):
        for endpoint in info.endpoints:
            endpoint_lines.append(f"- `{endpoint.method} {endpoint.path}` → `{info.path}` ({endpoint.source})")

    http_lines = [
        f"- `{info.path}` → {', '.join(f'`{item}`' for item in info.outbound_http[:8])}"
        for info in sorted(overview["outbound_http_files"], key=lambda item: item.path.lower())
    ]

    ws_lines = [
        f"- `{info.path}` → {', '.join(f'`{item}`' for item in info.outbound_ws[:8])}"
        for info in sorted(overview["outbound_ws_files"], key=lambda item: item.path.lower())
    ]

    lang_table = "\n".join(
        f"| {language} | {count} |"
        for language, count in sorted(overview["by_language"].items(), key=lambda item: item[0])
    ) or "| - | 0 |"

    category_table = "\n".join(
        f"| {category} | {count} |"
        for category, count in sorted(overview["by_category"].items(), key=lambda item: item[0])
    ) or "| - | 0 |"

    hot_spot_lines = []
    for item in overview["hot_spots"]:
        hot_spot_lines.append(
            f"- `{item.path}` | referenciado por `{len(item.imported_by)}` ficheiro(s) | usa `{len(item.uses_files)}` ficheiro(s) | papel: {item.probable_role}"
        )

    lines: list[str] = []
    lines.append("# MAPA DO PROJETO")
    lines.append("")
    lines.append(f"- **Raiz analisada:** `{root.as_posix()}`")
    lines.append(f"- **Gerado em:** {utc_now_iso()}")
    lines.append(f"- **Ficheiro de saída:** `{output_name}`")
    lines.append(f"- **Total de ficheiros analisados:** {overview['total_files']}")
    lines.append("")
    lines.append("## Objetivo deste ficheiro")
    lines.append("")
    lines.append(
        "Este documento é reescrito automaticamente e tenta explicar o papel de cada ficheiro, "
        "as ligações internas, endpoints, integrações HTTP/WS e pontos de entrada do projeto."
    )
    lines.append("")
    lines.append("## Estrutura de pastas analisadas")
    lines.append("")
    lines.append("```text")
    lines.append(build_tree(sorted(file_infos.keys())))
    lines.append("```")
    lines.append("")
    lines.append("## Distribuição por linguagem")
    lines.append("")
    lines.append("| Linguagem | Quantidade |")
    lines.append("|---|---:|")
    lines.append(lang_table)
    lines.append("")
    lines.append("## Distribuição por categoria")
    lines.append("")
    lines.append("| Categoria | Quantidade |")
    lines.append("|---|---:|")
    lines.append(category_table)
    lines.append("")
    lines.append("## Pontos de maior impacto")
    lines.append("")
    lines.extend(hot_spot_lines or ["- Nenhum hot spot identificado."])
    lines.append("")
    lines.append("## Endpoints detectados")
    lines.append("")
    lines.extend(endpoint_lines or ["- Nenhum endpoint detectado automaticamente."])
    lines.append("")
    lines.append("## Integrações HTTP detectadas")
    lines.append("")
    lines.extend(http_lines or ["- Nenhuma integração HTTP detectada automaticamente."])
    lines.append("")
    lines.append("## Integrações WebSocket detectadas")
    lines.append("")
    lines.extend(ws_lines or ["- Nenhuma integração WebSocket detectada automaticamente."])
    lines.append("")
    lines.append("## Mapa ficheiro a ficheiro")
    lines.append("")

    for path in sorted(file_infos.keys()):
        info = file_infos[path]
        lines.append(f"### `{info.path}`")
        lines.append("")
        lines.append(f"- **Papel provável:** {info.probable_role}")
        lines.append(f"- **Categoria:** `{info.category}`")
        lines.append(f"- **Linguagem:** `{info.language}`")
        lines.append(f"- **Tamanho:** {info.size_bytes} bytes")
        lines.append(
            f"- **Linhas:** {info.line_count} totais | {info.non_empty_line_count} não vazias | {info.comment_line_count} comentários"
        )
        lines.append(f"- **Hash lógico:** `{info.sha1}`")
        if info.classes:
            lines.append(f"- **Classes principais:** {', '.join(f'`{item}`' for item in info.classes[:20])}")
        if info.functions:
            lines.append(f"- **Funções principais:** {', '.join(f'`{item}`' for item in info.functions[:30])}")
        if info.endpoints:
            lines.append(
                "- **Endpoints:** "
                + "; ".join(f"`{item.method} {item.path}` ({item.source})" for item in info.endpoints)
            )
        if info.outbound_http:
            lines.append(
                "- **Integrações HTTP:** " + ", ".join(f"`{item}`" for item in info.outbound_http[:20])
            )
        if info.outbound_ws:
            lines.append(
                "- **Integrações WebSocket:** " + ", ".join(f"`{item}`" for item in info.outbound_ws[:20])
            )
        if info.imports_raw:
            lines.append("- **Imports/refs brutas:** " + ", ".join(f"`{item}`" for item in info.imports_raw[:30]))
        if info.uses_files:
            lines.append("- **Usa internamente:** " + ", ".join(f"`{item}`" for item in info.uses_files[:30]))
        if info.imported_by:
            lines.append("- **Referenciado por:** " + ", ".join(f"`{item}`" for item in info.imported_by[:30]))
        if info.warnings:
            lines.append("- **Avisos:** " + " | ".join(info.warnings))
        lines.append(f"- **Resumo técnico:** {info.summary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_cache_payload(file_infos: dict[str, FileInfo]) -> dict[str, object]:
    return {
        "generated_at": utc_now_iso(),
        "files": {
            path: {
                "sha1": info.sha1,
                "language": info.language,
                "category": info.category,
            }
            for path, info in sorted(file_infos.items())
        },
    }


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def load_previous_cache(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def analyze_project(
    root: Path,
    output_name: str,
    include_extensions: set[str],
    ignore_dirs: set[str],
    max_bytes: int,
    cache_name: str,
) -> tuple[str, dict[str, FileInfo]]:
    file_infos: dict[str, FileInfo] = {}

    for path in iter_project_files(root, include_extensions=include_extensions, ignore_dirs=ignore_dirs):
        rel = normalize_posix(path, root)
        if rel == output_name or rel == cache_name:
            continue
        info = analyze_file(root, path, max_bytes=max_bytes)
        if info is not None:
            file_infos[info.path] = info

    build_relationships(file_infos)
    enrich_roles_and_summaries(root, file_infos, max_bytes=max_bytes)

    markdown = render_markdown(root, file_infos, output_name)
    return markdown, file_infos


def print_run_summary(previous_cache: dict[str, object], current_infos: dict[str, FileInfo]) -> None:
    previous_files = previous_cache.get("files", {}) if isinstance(previous_cache, dict) else {}
    previous_files = previous_files if isinstance(previous_files, dict) else {}

    current_map = {path: info.sha1 for path, info in current_infos.items()}

    added = sorted(path for path in current_map if path not in previous_files)
    removed = sorted(path for path in previous_files if path not in current_map)
    changed = sorted(
        path
        for path, sha in current_map.items()
        if path in previous_files
        and isinstance(previous_files.get(path), dict)
        and previous_files[path].get("sha1") != sha
    )

    print(f"[mapa] ficheiros analisados: {len(current_infos)}")
    print(f"[mapa] novos: {len(added)} | alterados: {len(changed)} | removidos: {len(removed)}")

    if added:
        print("[mapa] novos:", ", ".join(added[:10]) + (" ..." if len(added) > 10 else ""))
    if changed:
        print("[mapa] alterados:", ", ".join(changed[:10]) + (" ..." if len(changed) > 10 else ""))
    if removed:
        print("[mapa] removidos:", ", ".join(removed[:10]) + (" ..." if len(removed) > 10 else ""))


def run_once(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Erro: raiz inválida: {root}", file=sys.stderr)
        return 2

    include_extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.include_ext}
    ignore_dirs = set(DEFAULT_IGNORE_DIRS) | set(args.ignore_dir)
    output_path = root / args.output
    cache_path = root / args.cache

    previous_cache = load_previous_cache(cache_path)

    markdown, infos = analyze_project(
        root=root,
        output_name=args.output,
        include_extensions=include_extensions,
        ignore_dirs=ignore_dirs,
        max_bytes=args.max_bytes,
        cache_name=args.cache,
    )

    write_text(output_path, markdown)
    write_text(cache_path, json.dumps(build_cache_payload(infos), ensure_ascii=False, indent=2))

    print_run_summary(previous_cache, infos)
    print(f"[mapa] escrito em: {output_path}")
    return 0


def watch_loop(args: argparse.Namespace) -> int:
    last_fingerprint = None
    print("[mapa] modo watch ativo. Prima Ctrl+C para terminar.")
    while True:
        root = Path(args.root).expanduser().resolve()
        include_extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.include_ext}
        ignore_dirs = set(DEFAULT_IGNORE_DIRS) | set(args.ignore_dir)

        fingerprint_items: list[str] = []
        for path in iter_project_files(root, include_extensions=include_extensions, ignore_dirs=ignore_dirs):
            rel = normalize_posix(path, root)
            if rel in {args.output, args.cache}:
                continue
            try:
                stat = path.stat()
                fingerprint_items.append(f"{rel}:{int(stat.st_mtime)}:{stat.st_size}")
            except OSError:
                continue

        current_fingerprint = sha1_text("|".join(sorted(fingerprint_items)))
        if current_fingerprint != last_fingerprint:
            print(f"[mapa] alteração detetada em {utc_now_iso()}. A regenerar...")
            exit_code = run_once(args)
            if exit_code != 0:
                return exit_code
            last_fingerprint = current_fingerprint

        time.sleep(max(1, int(args.watch_interval)))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um mapa técnico do projeto e reescreve o ficheiro de saída."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Raiz do projeto a analisar. Padrão: diretório atual.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Nome do ficheiro de saída na raiz do projeto. Padrão: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--cache",
        default=DEFAULT_CACHE,
        help=f"Nome do ficheiro de cache na raiz do projeto. Padrão: {DEFAULT_CACHE}",
    )
    parser.add_argument(
        "--include-ext",
        nargs="*",
        default=sorted(DEFAULT_INCLUDE_EXTENSIONS),
        help="Extensões a analisar. Ex.: .py .ts .tsx .js .md",
    )
    parser.add_argument(
        "--ignore-dir",
        nargs="*",
        default=[],
        help="Diretórios adicionais para ignorar.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=512_000,
        help="Tamanho máximo por ficheiro para análise textual. Padrão: 512000 bytes.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Fica a observar alterações e regenera o mapa automaticamente.",
    )
    parser.add_argument(
        "--watch-interval",
        type=int,
        default=3,
        help="Intervalo de polling em segundos no modo --watch. Padrão: 3.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.watch:
        try:
            return watch_loop(args)
        except KeyboardInterrupt:
            print("\n[mapa] watch terminado pelo utilizador.")
            return 0
    return run_once(args)


if __name__ == "__main__":
    raise SystemExit(main())
