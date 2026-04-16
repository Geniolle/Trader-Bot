#!/usr/bin/env python3
"""
Gerador automático de mapa do projeto - versão especializada para Trader-Bot.

Melhorias desta versão:
- heurísticas específicas para o backend Trader-Bot
- identifica melhor candles, providers, runs, stage tests, catálogo e persistência
- adiciona secção de workflows críticos detectados
- descreve melhor cada ficheiro com "papel", "workflow" e "ligações"
- continua a reescrever o mapa completo sempre que for executado

Uso:
    python gerar_mapa_projeto_v2.py .
    python gerar_mapa_projeto_v2.py . --watch
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
    r"""(?:import\s+[^;]*?\s+from\s+|import\s*\(\s*|require\s*\(\s*)([\"'])(.*?)\1""",
    re.MULTILINE,
)
FETCH_URL_RE = re.compile(
    r"""(?:fetch|axios\.(?:get|post|put|patch|delete)|axios)\s*\(\s*([\"'])(.*?)\1""",
    re.MULTILINE,
)
WEBSOCKET_RE = re.compile(
    r"""new\s+WebSocket\s*\(\s*([\"'])(.*?)\1""",
    re.MULTILINE,
)
HTTP_URL_RE = re.compile(r"""https?://[^\s\"'`)>]+""")
WS_URL_RE = re.compile(r"""wss?://[^\s\"'`)>]+""")
COMMENT_LINE_RE = re.compile(r"^\s*(#|//)")
FASTAPI_ROUTER_PREFIX_RE = re.compile(
    r"""APIRouter\s*\(\s*prefix\s*=\s*([\"'])(.*?)\1""",
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
    workflow: str = ""
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


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
    return sum(1 for line in text.splitlines() if COMMENT_LINE_RE.match(line))


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
    if "endpoints" in parts or "api" in parts:
        return "api"
    if "providers" in parts:
        return "provider"
    if "repositories" in parts or "repository" in name:
        return "repository"
    if "storage" in parts or "database" in name:
        return "storage"
    if "schemas" in parts or "schema" in name:
        return "schema"
    if "models" in parts or "model" in name:
        return "model"
    if "strategies" in parts or "strategy" in name:
        return "strategy"
    if "engine" in parts or "engine" in name:
        return "engine"
    if "hooks" in parts or "hook" in name:
        return "hook"
    if "components" in parts:
        return "component"
    if "services" in parts or "service" in name:
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
    return match.group(2).strip() if match else ""


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
            endpoints.append(EndpointInfo(method=method.upper(), path=full_path or "/", source=node.name))

    if endpoints:
        return endpoints

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


def infer_project_profiles(file_infos: dict[str, FileInfo]) -> set[str]:
    paths = set(file_infos.keys())
    profiles: set[str] = set()
    if "app/providers/twelvedata.py" in paths and "app/engine/run_engine.py" in paths:
        profiles.add("trader_bot_backend")
    if "web/src/hooks/useCandles.ts" in paths and "web/src/App.tsx" in paths:
        profiles.add("trader_bot_frontend")
    return profiles


def detect_probable_role_generic(info: FileInfo, text: str) -> str:
    path_lower = info.path.lower()
    name = Path(info.path).name.lower()
    if info.category == "entrypoint":
        return "Ponto de entrada da aplicação"
    if info.endpoints:
        return "Expõe endpoints HTTP ou WebSocket"
    if "apirouter" in text.lower():
        return "Configura roteamento da API"
    if info.category == "repository":
        return "Lê ou grava dados na persistência"
    if info.category == "provider":
        return "Integra fonte externa de dados"
    if info.category == "engine":
        return "Orquestra lógica principal"
    if info.category == "strategy":
        return "Implementa regras de estratégia"
    if info.category == "hook":
        if info.outbound_ws:
            return "Hook de frontend com realtime"
        if info.outbound_http:
            return "Hook de frontend com consumo de API"
        return "Hook de frontend"
    if info.category == "component":
        return "Componente visual"
    if info.category == "config":
        return "Centraliza configurações"
    if info.category == "schema":
        return "Define contratos de dados"
    if info.category == "model":
        return "Define modelos de domínio ou base de dados"
    if "test" in path_lower:
        return "Ficheiro de testes"
    if name == "readme.md":
        return "Documentação principal do projeto"
    if info.outbound_ws:
        return "Consome WebSocket"
    if info.outbound_http:
        return "Consome HTTP"
    if info.language == "markdown":
        return "Documentação"
    return "Lógica de suporte do projeto"


def detect_probable_role_trader_bot(info: FileInfo, text: str) -> tuple[str, list[str]]:
    path = info.path
    tags: list[str] = []
    exact_roles = {
        "app/main.py": "Inicializa a API FastAPI do backend Trader-Bot",
        "app/core/settings.py": "Centraliza settings globais do backend",
        "app/storage/database.py": "Configura engine SQLAlchemy e sessões da base de dados",
        "app/storage/models.py": "Define tabelas e modelos persistidos em SQLite",
        "app/providers/factory.py": "Resolve e instancia o provider de dados de mercado",
        "app/providers/twelvedata.py": "Busca candles históricos no TwelveData e converte para o formato interno",
        "app/api/v1/router.py": "Agrega os routers versionados da API /api/v1",
        "app/api/v1/endpoints/candles.py": "Expõe leitura de candles persistidos",
        "app/api/v1/endpoints/runs.py": "Executa runs históricas e aciona fallback ao provider quando faltam candles locais",
        "app/api/v1/endpoints/providers.py": "Lista providers disponíveis e o provider ativo",
        "app/api/v1/endpoints/run_history.py": "Lista histórico de runs persistidas",
        "app/api/v1/endpoints/run_metrics.py": "Devolve métricas de um run específico",
        "app/api/v1/endpoints/run_cases.py": "Devolve casos de um run específico",
        "app/api/v1/endpoints/run_details.py": "Consolida run, métricas e casos num único payload",
        "app/api/v1/endpoints/strategies.py": "Lista estratégias registadas",
        "app/engine/run_engine.py": "Orquestra a execução candle a candle de um run",
        "app/engine/case_engine.py": "Atualiza e fecha casos abertos durante a execução",
        "app/engine/metrics_engine.py": "Calcula métricas finais do run",
        "app/storage/repositories/candle_repository.py": "Grava candles na base com tratamento de duplicados",
        "app/storage/repositories/candle_queries.py": "Consulta candles persistidos por símbolo, timeframe e intervalo",
        "app/storage/repositories/run_repository.py": "Grava runs na base de dados",
        "app/storage/repositories/run_queries.py": "Consulta runs persistidos",
        "app/storage/repositories/case_repository.py": "Grava casos fechados do run",
        "app/storage/repositories/case_queries.py": "Consulta casos persistidos por run",
        "app/storage/repositories/metrics_repository.py": "Grava métricas do run",
        "app/storage/repositories/metrics_queries.py": "Consulta métricas persistidas por run",
        "app/registry/strategy_registry.py": "Regista e disponibiliza estratégias ativas do backend",
    }
    role = exact_roles.get(path, detect_probable_role_generic(info, text))
    if "app/api/v1/endpoints/" in path:
        tags.append("api")
    if "app/providers/" in path:
        tags.append("provider")
    if "app/storage/repositories/" in path:
        tags.append("repository")
    if "app/engine/" in path:
        tags.append("engine")
    if "app/strategies/" in path:
        tags.append("strategy")
    if "stage_test" in path.lower():
        tags.append("stage-test")
    if "candle" in path.lower():
        tags.append("candles")
    if "run" in path.lower():
        tags.append("runs")
    return role, sorted(set(tags))


def detect_workflow_generic(info: FileInfo) -> str:
    if info.endpoints:
        return "Recebe pedido externo, chama a camada interna associada e devolve resposta."
    if info.category == "repository":
        return "Recebe objetos ou filtros, executa leitura/escrita na base e devolve o resultado persistido."
    if info.category == "provider":
        return "Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno."
    if info.category == "engine":
        return "Recebe entidades de domínio, coordena a lógica principal e produz um resultado agregado."
    if info.category == "hook":
        return "Reage ao estado do frontend, consome dados e devolve estado pronto para a UI."
    if info.category == "component":
        return "Recebe props e renderiza a parte visual correspondente."
    return "Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte."


def detect_workflow_trader_bot(info: FileInfo, text: str) -> str:
    path = info.path
    workflows = {
        "app/api/v1/endpoints/candles.py": "Fluxo: request HTTP -> SessionLocal -> CandleQueryRepository.list_by_filters -> transformação para CandleResponse -> resposta da API.",
        "app/api/v1/endpoints/runs.py": "Fluxo: request HTTP -> validar strategy no registry -> tentar ler candles locais -> se não existirem, usar provider configurado -> gravar candles com CandleRepository -> executar RunEngine -> gravar run/cases/métricas -> devolver HistoricalRunResponse.",
        "app/api/v1/endpoints/providers.py": "Fluxo: ler settings -> instanciar MarketDataProviderFactory -> listar providers -> devolver provider ativo e lista disponível.",
        "app/api/v1/endpoints/run_history.py": "Fluxo: request HTTP -> SessionLocal -> StrategyRunQueryRepository.list_runs_by_filters -> mapear linhas para StrategyRunResponse -> resposta.",
        "app/api/v1/endpoints/run_metrics.py": "Fluxo: request HTTP -> SessionLocal -> StrategyMetricsQueryRepository.get_by_run_id -> validar existência -> devolver StrategyMetricsResponse.",
        "app/api/v1/endpoints/run_cases.py": "Fluxo: request HTTP -> SessionLocal -> StrategyCaseQueryRepository.list_by_run_id -> desserializar metadata_json -> devolver lista de casos.",
        "app/api/v1/endpoints/run_details.py": "Fluxo: request HTTP -> SessionLocal -> ler run + métricas + casos -> agregar tudo em RunDetailsResponse -> resposta única.",
        "app/providers/factory.py": "Fluxo: receber nome do provider -> procurar na tabela interna -> instanciar a classe concreta -> devolver provider pronto a usar.",
        "app/providers/twelvedata.py": "Fluxo: receber símbolo/timeframe/intervalo -> montar request HTTP ao TwelveData -> tratar erros -> converter payload em objetos Candle -> devolver candles normalizados.",
        "app/storage/repositories/candle_repository.py": "Fluxo: receber candles de domínio -> tentar inserir cada candle -> em duplicado usar o existente -> commit final -> devolver lista persistida.",
        "app/storage/repositories/candle_queries.py": "Fluxo: receber filtros -> montar query SQLAlchemy por símbolo/timeframe/intervalo -> ordenar por open_time -> devolver candles persistidos.",
        "app/engine/run_engine.py": "Fluxo: receber run + strategy + config + candles -> aplicar warmup -> percorrer candles -> atualizar open cases -> abrir novos casos quando houver trigger -> fechar o run -> calcular métricas -> devolver run/open_cases/closed_cases/metrics.",
        "app/engine/case_engine.py": "Fluxo: receber case aberto + candle -> strategy.update_case -> strategy.should_close_case -> se necessário strategy.close_case -> devolver case atualizado.",
        "app/engine/metrics_engine.py": "Fluxo: receber closed_cases -> contar hits/fails/timeouts -> calcular taxas e médias -> devolver StrategyMetrics.",
        "app/registry/strategy_registry.py": "Fluxo: instanciar estratégias concretas -> registar por chave -> disponibilizar lookup, listagem e validação de strategies.",
    }
    if path in workflows:
        return workflows[path]
    if "app/strategies/" in path:
        return "Fluxo: a estratégia recebe candles e config, calcula indicadores, decide trigger, cria casos, atualiza casos abertos e define quando devem ser fechados."
    if "stage_test" in path.lower():
        return "Fluxo: recebe parâmetros de teste, prepara catálogo ou execução do stage test e devolve resultado compatível com a interface/manual runner."
    return detect_workflow_generic(info)


def build_summary(info: FileInfo) -> str:
    parts: list[str] = [info.probable_role]
    if info.workflow:
        parts.append(info.workflow)
    if info.endpoints:
        parts.append(f"Rotas detectadas: {', '.join(f'{item.method} {item.path}' for item in info.endpoints[:5])}")
    if info.classes:
        parts.append(f"Classes principais: {', '.join(info.classes[:6])}")
    if info.functions:
        parts.append(f"Funções principais: {', '.join(info.functions[:6])}")
    if info.outbound_http:
        parts.append(f"Integrações HTTP: {', '.join(info.outbound_http[:4])}")
    if info.outbound_ws:
        parts.append(f"Integrações WS: {', '.join(info.outbound_ws[:4])}")
    if info.uses_files:
        parts.append(f"Depende de: {', '.join(info.uses_files[:6])}")
    if info.imported_by:
        parts.append(f"Referenciado por: {', '.join(info.imported_by[:6])}")
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


def enrich_infos(root: Path, file_infos: dict[str, FileInfo], max_bytes: int) -> set[str]:
    profiles = infer_project_profiles(file_infos)
    for path, info in file_infos.items():
        full_path = root / path
        text = safe_read_text(full_path) if full_path.exists() and full_path.stat().st_size <= max_bytes else ""
        if "trader_bot_backend" in profiles:
            role, tags = detect_probable_role_trader_bot(info, text)
            info.probable_role = role
            info.tags = tags
            info.workflow = detect_workflow_trader_bot(info, text)
        else:
            info.probable_role = detect_probable_role_generic(info, text)
            info.workflow = detect_workflow_generic(info)
        info.summary = build_summary(info)
    return profiles


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
    hot_spots = sorted(file_infos.values(), key=lambda item: (len(item.imported_by), len(item.uses_files), item.path.lower()), reverse=True)
    return {
        "total_files": len(file_infos),
        "by_language": by_language,
        "by_category": by_category,
        "endpoint_files": endpoint_files,
        "outbound_http_files": outbound_http_files,
        "outbound_ws_files": outbound_ws_files,
        "hot_spots": hot_spots[:15],
    }


def build_trader_bot_critical_workflows(file_infos: dict[str, FileInfo]) -> list[str]:
    paths = set(file_infos.keys())
    items: list[str] = []
    if {"app/api/v1/endpoints/runs.py", "app/providers/factory.py", "app/providers/twelvedata.py", "app/storage/repositories/candle_repository.py", "app/engine/run_engine.py"}.issubset(paths):
        items.append("Run histórica: `app/api/v1/endpoints/runs.py` -> `app/storage/repositories/candle_queries.py` -> fallback para `app/providers/factory.py` + `app/providers/twelvedata.py` -> `app/storage/repositories/candle_repository.py` -> `app/engine/run_engine.py` -> persistência em `run_repository.py`, `case_repository.py`, `metrics_repository.py`.")
    if {"app/api/v1/endpoints/candles.py", "app/storage/repositories/candle_queries.py"}.issubset(paths):
        items.append("Leitura de candles: `app/api/v1/endpoints/candles.py` -> `SessionLocal` -> `app/storage/repositories/candle_queries.py` -> resposta `CandleResponse`.")
    if {"app/api/v1/endpoints/providers.py", "app/providers/factory.py", "app/core/settings.py"}.issubset(paths):
        items.append("Providers: `app/api/v1/endpoints/providers.py` -> `app/core/settings.py` -> `app/providers/factory.py` -> devolução do provider ativo e providers suportados.")
    if {"app/api/v1/endpoints/run_details.py", "app/storage/repositories/run_queries.py", "app/storage/repositories/case_queries.py", "app/storage/repositories/metrics_queries.py"}.issubset(paths):
        items.append("Detalhe de run: `app/api/v1/endpoints/run_details.py` -> `run_queries.py` + `case_queries.py` + `metrics_queries.py` -> payload único para UI/diagnóstico.")
    if {"app/registry/strategy_registry.py", "app/strategies/base.py"}.issubset(paths):
        items.append("Estratégias: `app/registry/strategy_registry.py` regista classes concretas em `app/strategies/`, que são consumidas por `app/api/v1/endpoints/runs.py` e `app/engine/run_engine.py`.")
    if not items:
        items.append("Nenhum workflow crítico Trader-Bot conseguiu ser fechado automaticamente com as heurísticas atuais.")
    return items


def render_markdown(root: Path, file_infos: dict[str, FileInfo], output_name: str, profiles: set[str]) -> str:
    overview = build_overview(file_infos)
    endpoint_lines: list[str] = []
    for info in sorted(overview["endpoint_files"], key=lambda item: item.path.lower()):
        for endpoint in info.endpoints:
            endpoint_lines.append(f"- `{endpoint.method} {endpoint.path}` -> `{info.path}` ({endpoint.source})")
    http_lines = [f"- `{info.path}` -> {', '.join(f'`{item}`' for item in info.outbound_http[:8])}" for info in sorted(overview["outbound_http_files"], key=lambda item: item.path.lower())]
    ws_lines = [f"- `{info.path}` -> {', '.join(f'`{item}`' for item in info.outbound_ws[:8])}" for info in sorted(overview["outbound_ws_files"], key=lambda item: item.path.lower())]
    lang_table = "\n".join(f"| {language} | {count} |" for language, count in sorted(overview["by_language"].items(), key=lambda item: item[0])) or "| - | 0 |"
    category_table = "\n".join(f"| {category} | {count} |" for category, count in sorted(overview["by_category"].items(), key=lambda item: item[0])) or "| - | 0 |"
    hot_spot_lines = [f"- `{item.path}` | referenciado por `{len(item.imported_by)}` ficheiro(s) | usa `{len(item.uses_files)}` ficheiro(s) | papel: {item.probable_role}" for item in overview["hot_spots"]]

    lines: list[str] = []
    lines.append("# MAPA DO PROJETO")
    lines.append("")
    lines.append(f"- **Raiz analisada:** `{root.as_posix()}`")
    lines.append(f"- **Gerado em:** {utc_now_iso()}")
    lines.append(f"- **Ficheiro de saída:** `{output_name}`")
    lines.append(f"- **Total de ficheiros analisados:** {overview['total_files']}")
    lines.append(f"- **Perfis detectados:** {', '.join(sorted(profiles)) if profiles else 'nenhum perfil específico'}")
    lines.append("")
    lines.append("## Objetivo deste ficheiro")
    lines.append("")
    lines.append("Este documento é reescrito automaticamente e tenta explicar o papel de cada ficheiro, os workflows críticos, as ligações internas, endpoints e integrações externas.")
    lines.append("")
    if "trader_bot_backend" in profiles:
        lines.append("## Workflows críticos detectados (Trader-Bot)")
        lines.append("")
        lines.extend(f"- {item}" for item in build_trader_bot_critical_workflows(file_infos))
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
        lines.append(f"- **Workflow provável:** {info.workflow}")
        lines.append(f"- **Categoria:** `{info.category}`")
        lines.append(f"- **Linguagem:** `{info.language}`")
        if info.tags:
            lines.append(f"- **Tags:** {', '.join(f'`{item}`' for item in info.tags)}")
        lines.append(f"- **Tamanho:** {info.size_bytes} bytes")
        lines.append(f"- **Linhas:** {info.line_count} totais | {info.non_empty_line_count} não vazias | {info.comment_line_count} comentários")
        lines.append(f"- **Hash lógico:** `{info.sha1}`")
        if info.classes:
            lines.append(f"- **Classes principais:** {', '.join(f'`{item}`' for item in info.classes[:20])}")
        if info.functions:
            lines.append(f"- **Funções principais:** {', '.join(f'`{item}`' for item in info.functions[:30])}")
        if info.endpoints:
            lines.append("- **Endpoints:** " + "; ".join(f"`{item.method} {item.path}` ({item.source})" for item in info.endpoints))
        if info.outbound_http:
            lines.append("- **Integrações HTTP:** " + ", ".join(f"`{item}`" for item in info.outbound_http[:20]))
        if info.outbound_ws:
            lines.append("- **Integrações WebSocket:** " + ", ".join(f"`{item}`" for item in info.outbound_ws[:20]))
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
    return {"generated_at": utc_now_iso(), "files": {path: {"sha1": info.sha1, "language": info.language, "category": info.category} for path, info in sorted(file_infos.items())}}


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def load_previous_cache(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def analyze_project(root: Path, output_name: str, include_extensions: set[str], ignore_dirs: set[str], max_bytes: int, cache_name: str) -> tuple[str, dict[str, FileInfo], set[str]]:
    file_infos: dict[str, FileInfo] = {}
    for path in iter_project_files(root, include_extensions=include_extensions, ignore_dirs=ignore_dirs):
        rel = normalize_posix(path, root)
        if rel == output_name or rel == cache_name:
            continue
        info = analyze_file(root, path, max_bytes=max_bytes)
        if info is not None:
            file_infos[info.path] = info
    build_relationships(file_infos)
    profiles = enrich_infos(root, file_infos, max_bytes=max_bytes)
    markdown = render_markdown(root, file_infos, output_name, profiles)
    return markdown, file_infos, profiles


def print_run_summary(previous_cache: dict[str, object], current_infos: dict[str, FileInfo], profiles: set[str]) -> None:
    previous_files = previous_cache.get("files", {}) if isinstance(previous_cache, dict) else {}
    previous_files = previous_files if isinstance(previous_files, dict) else {}
    current_map = {path: info.sha1 for path, info in current_infos.items()}
    added = sorted(path for path in current_map if path not in previous_files)
    removed = sorted(path for path in previous_files if path not in current_map)
    changed = sorted(path for path, sha in current_map.items() if path in previous_files and isinstance(previous_files.get(path), dict) and previous_files[path].get("sha1") != sha)

    print(f"[mapa-v2] perfis detetados: {', '.join(sorted(profiles)) if profiles else 'nenhum'}")
    print(f"[mapa-v2] ficheiros analisados: {len(current_infos)}")
    print(f"[mapa-v2] novos: {len(added)} | alterados: {len(changed)} | removidos: {len(removed)}")
    if added:
        print("[mapa-v2] novos:", ", ".join(added[:10]) + (" ..." if len(added) > 10 else ""))
    if changed:
        print("[mapa-v2] alterados:", ", ".join(changed[:10]) + (" ..." if len(changed) > 10 else ""))
    if removed:
        print("[mapa-v2] removidos:", ", ".join(removed[:10]) + (" ..." if len(removed) > 10 else ""))


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
    markdown, infos, profiles = analyze_project(root=root, output_name=args.output, include_extensions=include_extensions, ignore_dirs=ignore_dirs, max_bytes=args.max_bytes, cache_name=args.cache)
    write_text(output_path, markdown)
    write_text(cache_path, json.dumps(build_cache_payload(infos), ensure_ascii=False, indent=2))
    print_run_summary(previous_cache, infos, profiles)
    print(f"[mapa-v2] escrito em: {output_path}")
    return 0


def watch_loop(args: argparse.Namespace) -> int:
    last_fingerprint = None
    print("[mapa-v2] modo watch ativo. Prima Ctrl+C para terminar.")
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
            print(f"[mapa-v2] alteração detetada em {utc_now_iso()}. A regenerar...")
            exit_code = run_once(args)
            if exit_code != 0:
                return exit_code
            last_fingerprint = current_fingerprint
        time.sleep(max(1, int(args.watch_interval)))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera um mapa técnico do projeto e reescreve o ficheiro de saída.")
    parser.add_argument("root", nargs="?", default=".", help="Raiz do projeto a analisar. Padrão: diretório atual.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Nome do ficheiro de saída na raiz do projeto. Padrão: {DEFAULT_OUTPUT}")
    parser.add_argument("--cache", default=DEFAULT_CACHE, help=f"Nome do ficheiro de cache na raiz do projeto. Padrão: {DEFAULT_CACHE}")
    parser.add_argument("--include-ext", nargs="*", default=sorted(DEFAULT_INCLUDE_EXTENSIONS), help="Extensões a analisar. Ex.: .py .ts .tsx .js .md")
    parser.add_argument("--ignore-dir", nargs="*", default=[], help="Diretórios adicionais para ignorar.")
    parser.add_argument("--max-bytes", type=int, default=512_000, help="Tamanho máximo por ficheiro para análise textual. Padrão: 512000 bytes.")
    parser.add_argument("--watch", action="store_true", help="Fica a observar alterações e regenera o mapa automaticamente.")
    parser.add_argument("--watch-interval", type=int, default=3, help="Intervalo de polling em segundos no modo --watch. Padrão: 3.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.watch:
        try:
            return watch_loop(args)
        except KeyboardInterrupt:
            print("\n[mapa-v2] watch terminado pelo utilizador.")
            return 0
    return run_once(args)


if __name__ == "__main__":
    raise SystemExit(main())
