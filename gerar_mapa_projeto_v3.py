#!/usr/bin/env python3
"""
Gerador automático de mapa do projeto - versão 3 com ligação backend <-> frontend.

Objetivo:
- analisar a raiz atual do projeto
- detetar ficheiros, imports, funções, classes, endpoints e integrações
- detetar automaticamente um repositório ligado (ex.: Trader-Bot <-> TRADERBOTWEB)
- escrever no mapa as ligações de contrato entre frontend e backend
- reescrever tudo sempre que for executado

Exemplos:
    python gerar_mapa_projeto_v3.py .
    python gerar_mapa_projeto_v3.py . --linked-root "C:/TraderBotWeb"
    python gerar_mapa_projeto_v3.py . --watch
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
    r"""(?:fetch|axios\.(?:get|post|put|patch|delete)|axios)\s*\(\s*([\"'`])(.*?)\1""",
    re.MULTILINE | re.DOTALL,
)
WEBSOCKET_RE = re.compile(
    r"""new\s+WebSocket\s*\(\s*([\"'`])(.*?)\1""",
    re.MULTILINE | re.DOTALL,
)
HTTP_URL_RE = re.compile(r"""https?://[^\s\"'`)>]+""")
WS_URL_RE = re.compile(r"""wss?://[^\s\"'`)>]+""")
COMMENT_LINE_RE = re.compile(r"^\s*(#|//)")
FASTAPI_ROUTER_PREFIX_RE = re.compile(
    r"""APIRouter\s*\(\s*prefix\s*=\s*([\"'])(.*?)\1""",
    re.MULTILINE,
)
GENERIC_PATH_RE = re.compile(
    r"""([\"'`])((?:https?://|wss?://)?/?(?:api/v\d+/)?[A-Za-z0-9_\-${}]+(?:/[A-Za-z0-9_\-${}.:-]+)+/?(?:\?[^\1]*)?)\1""",
    re.MULTILINE,
)

COMMON_FRONTEND_NAMES = [
    "TRADERBOTWEB",
    "TraderBotWeb",
    "traderbotweb",
    "web",
]
COMMON_BACKEND_NAMES = [
    "Trader-Bot",
    "Trader-bot",
    "trader-bot",
    "TraderBot",
    "traderbot",
]


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
    path_refs: list[str] = field(default_factory=list)
    probable_role: str = ""
    workflow: str = ""
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ProjectAnalysis:
    root: Path
    label: str
    file_infos: dict[str, FileInfo]
    profiles: set[str]


@dataclass
class ContractLink:
    consumer_project: str
    consumer_file: str
    contract_path: str
    provider_project: str
    provider_file: str
    provider_endpoint: str
    note: str = ""


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
    if "endpoint" in parts or ("api" in parts and path.suffix.lower() == ".py"):
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


def normalize_url_like(value: str) -> str:
    value = value.strip()
    value = value.replace("${API_HTTP_BASE_URL}", "").replace("${API_WS_BASE_URL}", "")
    value = value.replace("${API_BASE}", "").replace("${query.toString()}", "")
    value = value.replace("${query}", "").replace("${symbol}", "{symbol}")
    value = value.replace("${timeframe}", "{timeframe}")
    value = value.replace("`", "").replace('"', "").replace("'", "")
    return value.strip()


def extract_outbound_http(text: str) -> list[str]:
    urls = {normalize_url_like(m.group(2)) for m in FETCH_URL_RE.finditer(text) if m.group(2).strip()}
    urls.update(HTTP_URL_RE.findall(text))
    path_refs = extract_path_refs(text)
    for ref in path_refs:
        if ref.startswith("/"):
            urls.add(ref)
    return sorted(item for item in urls if item)


def extract_outbound_ws(text: str) -> list[str]:
    urls = {normalize_url_like(m.group(2)) for m in WEBSOCKET_RE.finditer(text) if m.group(2).strip()}
    urls.update(WS_URL_RE.findall(text))
    return sorted(item for item in urls if item)


def extract_path_refs(text: str) -> list[str]:
    refs = set()
    for _, candidate in GENERIC_PATH_RE.findall(text):
        candidate = normalize_url_like(candidate)
        if not candidate:
            continue
        if " " in candidate:
            continue
        if candidate.startswith("http://") or candidate.startswith("https://") or candidate.startswith("ws://") or candidate.startswith("wss://"):
            continue
        if "/" not in candidate:
            continue
        if len(candidate) < 3:
            continue
        refs.add(candidate)
    return sorted(refs)


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

    if "app/api/v1/router.py" in paths and any(path.startswith("app/providers/") for path in paths):
        profiles.add("trader_bot_backend")

    if "web/src/constants/config.ts" in paths or any(path.startswith("web/src/hooks/") for path in paths):
        profiles.add("trader_bot_frontend")

    if not profiles:
        # fallback genérico
        if any(info.language == "python" for info in file_infos.values()):
            profiles.add("python_project")
        if any(info.language in {"typescript", "typescript-react", "javascript", "javascript-react"} for info in file_infos.values()):
            profiles.add("js_project")
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


def detect_probable_role_trader_bot_backend(info: FileInfo, text: str) -> tuple[str, list[str]]:
    path = info.path
    tags: list[str] = []
    exact_roles = {
        "app/main.py": "Inicializa a API FastAPI do backend Trader-Bot",
        "app/core/settings.py": "Centraliza settings globais do backend",
        "app/storage/database.py": "Configura engine SQLAlchemy e sessões da base de dados",
        "app/storage/models.py": "Define tabelas e modelos persistidos",
        "app/providers/factory.py": "Resolve e instancia o provider de dados de mercado",
        "app/providers/twelvedata.py": "Busca candles históricos no TwelveData e converte para o formato interno",
        "app/api/v1/router.py": "Agrega os routers versionados da API /api/v1",
        "app/api/v1/endpoints/candles.py": "Expõe leitura de candles persistidos",
        "app/api/v1/endpoints/providers.py": "Expõe providers disponíveis e provider ativo",
        "app/api/v1/endpoints/runs.py": "Executa runs históricas e faz fallback para provider quando faltam candles locais",
        "app/engine/run_engine.py": "Orquestra a execução integral de uma run",
        "app/engine/case_engine.py": "Atualiza e fecha casos ao longo dos candles",
        "app/engine/metrics_engine.py": "Consolida métricas de resultados",
    }
    if path in exact_roles:
        return exact_roles[path], tags

    if path.startswith("app/api/v1/endpoints/"):
        tags.append("api_endpoint")
        if "candles" in path:
            tags.append("candles")
            return "Endpoint de leitura ou suporte a candles", tags
        if "provider" in path:
            tags.append("provider")
            return "Endpoint de providers/configuração de mercado", tags
        if "run" in path:
            tags.append("runs")
            return "Endpoint ligado a runs, métricas, casos ou detalhe de execução", tags
        if "stage" in path:
            tags.append("stage_tests")
            return "Endpoint ligado a Stage Tests", tags
        return "Endpoint do backend", tags

    if path.startswith("app/providers/"):
        tags.append("provider")
        return "Provider de integração com dados de mercado", tags
    if path.startswith("app/storage/repositories/"):
        tags.append("repository")
        if "candle" in path:
            tags.append("candles")
        if "run" in path:
            tags.append("runs")
        return "Repositório de leitura/escrita na persistência", tags
    if path.startswith("app/strategies/"):
        tags.append("strategy")
        return "Implementação concreta de estratégia de trading", tags
    if path.startswith("app/registry/"):
        tags.append("registry")
        return "Regista e expõe estratégias disponíveis", tags
    if path.startswith("app/schemas/"):
        tags.append("schema")
        return "Contrato de entrada/saída da API", tags

    return detect_probable_role_generic(info, text), tags


def detect_probable_role_trader_bot_frontend(info: FileInfo, text: str) -> tuple[str, list[str]]:
    path = info.path
    tags: list[str] = []
    exact_roles = {
        "web/src/main.tsx": "Inicializa a aplicação React no browser",
        "web/src/App.tsx": "Compõe o dashboard principal e liga hooks, gráfico e cartões",
        "web/src/constants/config.ts": "Centraliza URLs base da API HTTP e WebSocket",
        "web/src/hooks/useCandles.ts": "Busca candles por HTTP e faz merge incremental para o gráfico",
        "web/src/hooks/useRealtimeFeed.ts": "Gere o WebSocket, ticks e refresh do gráfico em tempo real",
        "web/src/hooks/useMarketProviders.ts": "Carrega providers e sincroniza o provider selecionado",
        "web/src/hooks/useRunDetails.ts": "Carrega detalhe de runs a partir do backend",
        "web/src/services/stageTestsApi.ts": "Consome a API de Stage Tests",
    }
    if path in exact_roles:
        return exact_roles[path], tags

    if path.startswith("web/src/hooks/"):
        tags.append("hook")
        if "candle" in path.lower():
            tags.append("candles")
            return "Hook de frontend ligado ao fluxo de candles", tags
        if "realtime" in path.lower() or info.outbound_ws:
            tags.append("realtime")
            return "Hook de frontend ligado ao feed em tempo real", tags
        if "run" in path.lower():
            tags.append("runs")
            return "Hook de frontend ligado a runs e detalhe analítico", tags
        return "Hook de frontend", tags

    if path.startswith("web/src/components/"):
        tags.append("component")
        return "Componente visual do frontend", tags
    if path.startswith("web/src/services/"):
        tags.append("service")
        return "Serviço de frontend que consome o backend", tags
    if path.startswith("web/src/types/"):
        tags.append("types")
        return "Tipos/contratos usados pelo frontend", tags
    if path.startswith("web/src/constants/"):
        tags.append("config")
        return "Configuração e constantes do frontend", tags

    return detect_probable_role_generic(info, text), tags


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


def detect_workflow_trader_bot_backend(info: FileInfo, text: str) -> str:
    path = info.path
    workflows = {
        "app/api/v1/endpoints/candles.py": "Fluxo: request HTTP -> SessionLocal -> CandleQueryRepository.list_by_filters -> transformação para CandleResponse -> resposta da API.",
        "app/api/v1/endpoints/runs.py": "Fluxo: request HTTP -> validar strategy no registry -> tentar ler candles locais -> se não existirem, usar provider configurado -> gravar candles -> executar RunEngine -> gravar run/cases/métricas -> devolver HistoricalRunResponse.",
        "app/api/v1/endpoints/providers.py": "Fluxo: ler settings -> instanciar MarketDataProviderFactory -> listar providers -> devolver provider ativo e lista disponível.",
        "app/api/v1/endpoints/run_history.py": "Fluxo: request HTTP -> SessionLocal -> query de runs -> mapear linhas -> resposta.",
        "app/api/v1/endpoints/run_metrics.py": "Fluxo: request HTTP -> query de métricas -> validar existência -> devolver payload.",
        "app/api/v1/endpoints/run_cases.py": "Fluxo: request HTTP -> query de casos -> desserializar metadata_json -> devolver lista de casos.",
        "app/api/v1/endpoints/run_details.py": "Fluxo: request HTTP -> ler run + métricas + casos -> agregar em RunDetailsResponse.",
        "app/providers/factory.py": "Fluxo: receber nome do provider -> escolher classe concreta -> devolver instância pronta.",
        "app/providers/twelvedata.py": "Fluxo: receber symbol/timeframe/período -> construir request HTTP ao TwelveData -> validar payload -> converter para Candle interno.",
        "app/storage/repositories/candle_repository.py": "Fluxo: receber candles de domínio -> inserir em CandleModel -> deduplicar por constraint -> commit -> refresh.",
        "app/storage/repositories/candle_queries.py": "Fluxo: receber filtros de mercado/período -> consultar CandleModel -> ordenar e limitar -> devolver linhas da base.",
        "app/engine/run_engine.py": "Fluxo: iterar candles -> atualizar casos abertos -> avaliar trigger da estratégia -> abrir novos casos -> fechar run -> calcular métricas.",
        "app/engine/case_engine.py": "Fluxo: receber caso aberto + candle -> strategy.update_case -> strategy.should_close_case -> fechar quando aplicável.",
        "app/engine/metrics_engine.py": "Fluxo: receber casos fechados -> contar outcomes -> calcular taxas e médias -> devolver StrategyMetrics.",
        "app/registry/strategy_registry.py": "Fluxo: instanciar estratégias concretas -> registar por key -> permitir lookup pelas APIs e engine.",
    }
    if path in workflows:
        return workflows[path]

    if path.startswith("app/strategies/"):
        return "Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia."
    if path.startswith("app/storage/repositories/"):
        return "Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos."
    if path.startswith("app/api/v1/endpoints/"):
        return "Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada."
    return detect_workflow_generic(info)


def detect_workflow_trader_bot_frontend(info: FileInfo, text: str) -> str:
    path = info.path
    workflows = {
        "web/src/constants/config.ts": "Fluxo: centraliza base URL HTTP/WS consumida pelos hooks e serviços do frontend.",
        "web/src/hooks/useCandles.ts": "Fluxo: montar URL de candles -> fetch full/incremental -> normalizar payload -> preservar snapshot válido -> atualizar estado do gráfico.",
        "web/src/hooks/useRealtimeFeed.ts": "Fluxo: abrir WebSocket -> subscrever símbolo/timeframe -> receber ticks/eventos -> atualizar candles locais -> confirmar persistência quando aplicável.",
        "web/src/hooks/useMarketProviders.ts": "Fluxo: GET /providers -> normalizar providers -> sincronizar seleção no localStorage.",
        "web/src/hooks/useRunDetails.ts": "Fluxo: GET /run-details/{id} -> guardar run/metrics/cases -> disponibilizar detalhe ao dashboard.",
        "web/src/services/stageTestsApi.ts": "Fluxo: GET/POST de stage tests -> normalizar resposta -> devolver dados prontos para hooks/componentes.",
        "web/src/App.tsx": "Fluxo: orquestra filtros, hooks de dados, gráfico, runs e diagnósticos -> distribui estado para componentes.",
    }
    if path in workflows:
        return workflows[path]

    if path.startswith("web/src/hooks/"):
        return "Fluxo: observar seleção/estado da UI -> consumir backend ou WebSocket -> devolver estado pronto para componentes."
    if path.startswith("web/src/components/"):
        return "Fluxo: receber props e renderizar a secção visual correspondente do dashboard."
    if path.startswith("web/src/services/"):
        return "Fluxo: consumir endpoint do backend -> validar/normalizar payload -> devolver dados à camada superior."
    return detect_workflow_generic(info)


def build_summary(info: FileInfo) -> str:
    parts: list[str] = [info.probable_role]
    if info.workflow:
        parts.append(info.workflow)
    if info.endpoints:
        routes = ", ".join(f"{item.method} {item.path}" for item in info.endpoints[:5])
        parts.append(f"Rotas detectadas: {routes}")
    if info.classes:
        parts.append(f"Classes principais: {', '.join(info.classes[:6])}")
    if info.functions:
        parts.append(f"Funções principais: {', '.join(info.functions[:6])}")
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
    path_refs = extract_path_refs(text)
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
        path_refs=path_refs,
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
            role, tags = detect_probable_role_trader_bot_backend(info, text)
            info.probable_role = role
            info.tags = sorted(set(info.tags + tags))
            info.workflow = detect_workflow_trader_bot_backend(info, text)
        elif "trader_bot_frontend" in profiles:
            role, tags = detect_probable_role_trader_bot_frontend(info, text)
            info.probable_role = role
            info.tags = sorted(set(info.tags + tags))
            info.workflow = detect_workflow_trader_bot_frontend(info, text)
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


def build_trader_bot_critical_workflows(file_infos: dict[str, FileInfo]) -> list[str]:
    paths = set(file_infos.keys())
    items: list[str] = []
    if {"app/api/v1/endpoints/runs.py", "app/providers/factory.py", "app/storage/repositories/candle_repository.py", "app/engine/run_engine.py"}.issubset(paths):
        items.append("Run histórica: `app/api/v1/endpoints/runs.py` -> query local de candles -> fallback para provider -> persistência de candles -> `app/engine/run_engine.py` -> persistência de runs/cases/métricas.")
    if {"app/api/v1/endpoints/candles.py", "app/storage/repositories/candle_queries.py"}.issubset(paths):
        items.append("Leitura de candles: `app/api/v1/endpoints/candles.py` -> `SessionLocal` -> `candle_queries.py` -> resposta serializada.")
    if {"app/api/v1/endpoints/providers.py", "app/providers/factory.py", "app/core/settings.py"}.issubset(paths):
        items.append("Providers: `providers.py` -> `settings.py` -> `factory.py` -> devolução do provider ativo e lista disponível.")
    if {"app/api/v1/endpoints/run_details.py", "app/storage/repositories/run_queries.py", "app/storage/repositories/case_queries.py", "app/storage/repositories/metrics_queries.py"}.issubset(paths):
        items.append("Detalhe de run: `run_details.py` -> `run_queries.py` + `case_queries.py` + `metrics_queries.py` -> payload único para UI/diagnóstico.")
    if {"app/registry/strategy_registry.py", "app/strategies/base.py"}.issubset(paths):
        items.append("Estratégias: `strategy_registry.py` regista classes concretas em `app/strategies/`, consumidas por endpoints e engine.")
    if not items:
        items.append("Nenhum workflow crítico Trader-Bot conseguiu ser fechado automaticamente com as heurísticas atuais.")
    return items


def build_frontend_critical_workflows(file_infos: dict[str, FileInfo]) -> list[str]:
    paths = set(file_infos.keys())
    items: list[str] = []
    if {"web/src/hooks/useCandles.ts", "web/src/constants/config.ts"}.issubset(paths):
        items.append("Candles no frontend: `config.ts` define base URL -> `useCandles.ts` monta URLs `/candles` e `/candles/latest` -> normaliza payload -> preserva snapshot válido.")
    if {"web/src/hooks/useRealtimeFeed.ts", "web/src/constants/config.ts"}.issubset(paths):
        items.append("Realtime no frontend: `config.ts` define base WS -> `useRealtimeFeed.ts` abre WebSocket, subscreve símbolo/timeframe e atualiza candles locais.")
    if {"web/src/hooks/useMarketProviders.ts", "web/src/constants/config.ts"}.issubset(paths):
        items.append("Providers no frontend: `useMarketProviders.ts` consome `/providers`, normaliza lista e sincroniza seleção do utilizador.")
    if {"web/src/hooks/useRunDetails.ts"}.issubset(paths):
        items.append("Detalhe de runs no frontend: `useRunDetails.ts` consome `/run-details/{id}` e disponibiliza run, métricas e casos à interface.")
    if {"web/src/services/stageTestsApi.ts"}.issubset(paths):
        items.append("Stage Tests no frontend: `stageTestsApi.ts` consome `/stage-tests/options` e `/stage-tests/run` para suportar a UI de testes.")
    if not items:
        items.append("Nenhum workflow crítico do frontend conseguiu ser fechado automaticamente com as heurísticas atuais.")
    return items


def normalize_contract_path(value: str) -> str:
    value = normalize_url_like(value)
    if not value:
        return ""
    value = re.sub(r"^(https?://[^/]+|wss?://[^/]+)", "", value)
    value = value.replace("${API_HTTP_BASE_URL}", "").replace("${API_WS_BASE_URL}", "")
    value = value.replace("${API_BASE}", "")
    value = value.replace("//", "/")
    if "?" in value:
        value = value.split("?", 1)[0]
    if "#" in value:
        value = value.split("#", 1)[0]
    if not value.startswith("/"):
        value = "/" + value
    value = re.sub(r"/+", "/", value)
    value = re.sub(r"/\$\{[^/]+\}", "/{var}", value)
    value = re.sub(r"/:[^/]+", "/{var}", value)
    if len(value) > 1 and value.endswith("/"):
        value = value[:-1]
    return value.strip()


def route_match_score(contract_path: str, endpoint_path: str) -> int:
    cp = normalize_contract_path(contract_path)
    ep = normalize_contract_path(endpoint_path)
    if not cp or not ep:
        return 0
    if cp == ep:
        return 100
    if cp.startswith(ep + "/"):
        return 90
    if ep.startswith(cp + "/"):
        return 85
    cp_parts = [part for part in cp.split("/") if part]
    ep_parts = [part for part in ep.split("/") if part]
    if not cp_parts or not ep_parts:
        return 0
    if cp_parts[0] == ep_parts[0]:
        shared = 0
        for left, right in zip(cp_parts, ep_parts):
            if left == right or left == "{var}" or right == "{var}":
                shared += 1
            else:
                break
        return 50 + shared * 5 if shared else 0
    return 0


def gather_contract_paths(project: ProjectAnalysis) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for path, info in project.file_infos.items():
        refs = set()
        refs.update(normalize_contract_path(item) for item in info.outbound_http)
        refs.update(normalize_contract_path(item) for item in info.outbound_ws)
        refs.update(normalize_contract_path(item) for item in info.path_refs)
        refs = {item for item in refs if item and item != "/"}
        if refs:
            mapping[path] = sorted(refs)
    return mapping


def gather_endpoints(project: ProjectAnalysis) -> list[tuple[str, EndpointInfo]]:
    items: list[tuple[str, EndpointInfo]] = []
    for path, info in project.file_infos.items():
        for endpoint in info.endpoints:
            items.append((path, endpoint))
    return items


def correlate_projects(primary: ProjectAnalysis, linked: list[ProjectAnalysis]) -> tuple[list[ContractLink], list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    project_by_name = {primary.label: primary}
    for item in linked:
        project_by_name[item.label] = item

    frontend_projects = [p for p in project_by_name.values() if "trader_bot_frontend" in p.profiles]
    backend_projects = [p for p in project_by_name.values() if "trader_bot_backend" in p.profiles]

    links: list[ContractLink] = []
    unmatched_contracts: list[tuple[str, str, str]] = []
    unused_endpoints: list[tuple[str, str, str]] = []

    matched_endpoint_keys: set[tuple[str, str, str]] = set()

    for consumer in frontend_projects:
        contract_map = gather_contract_paths(consumer)
        for consumer_file, contract_paths in sorted(contract_map.items()):
            for contract_path in contract_paths:
                best: tuple[int, ProjectAnalysis | None, str | None, EndpointInfo | None] = (0, None, None, None)
                for provider in backend_projects:
                    for provider_file, endpoint in gather_endpoints(provider):
                        score = route_match_score(contract_path, endpoint.path)
                        if score > best[0]:
                            best = (score, provider, provider_file, endpoint)
                if best[0] >= 50 and best[1] and best[2] and best[3]:
                    links.append(
                        ContractLink(
                            consumer_project=consumer.label,
                            consumer_file=consumer_file,
                            contract_path=contract_path,
                            provider_project=best[1].label,
                            provider_file=best[2],
                            provider_endpoint=f"{best[3].method} {normalize_contract_path(best[3].path)}",
                            note="" if best[0] >= 90 else "correlação parcial",
                        )
                    )
                    matched_endpoint_keys.add((best[1].label, best[2], f"{best[3].method} {normalize_contract_path(best[3].path)}"))
                else:
                    unmatched_contracts.append((consumer.label, consumer_file, contract_path))

    for provider in backend_projects:
        for provider_file, endpoint in gather_endpoints(provider):
            endpoint_key = (provider.label, provider_file, f"{endpoint.method} {normalize_contract_path(endpoint.path)}")
            if endpoint_key not in matched_endpoint_keys:
                unused_endpoints.append(endpoint_key)

    links.sort(key=lambda item: (item.consumer_project, item.consumer_file, item.contract_path))
    unmatched_contracts.sort()
    unused_endpoints.sort()
    return links, unmatched_contracts, unused_endpoints


def detect_linked_roots(root: Path, explicit_linked_roots: list[str]) -> list[Path]:
    linked: list[Path] = []

    for item in explicit_linked_roots:
        path = Path(item).expanduser().resolve()
        if path.exists() and path.is_dir() and path != root:
            linked.append(path)

    parent = root.parent
    current_name = root.name.lower()

    auto_names: list[str] = []
    if "trader-bot" in current_name or "traderbot" in current_name:
        auto_names.extend(COMMON_FRONTEND_NAMES)
    if "traderbotweb" in current_name or current_name == "web":
        auto_names.extend(COMMON_BACKEND_NAMES)

    for name in auto_names:
        candidate = parent / name
        if candidate.exists() and candidate.is_dir() and candidate != root and candidate not in linked:
            linked.append(candidate)

    return linked


def analyze_project_root(root: Path, label: str, output_name: str, include_extensions: set[str], ignore_dirs: set[str], max_bytes: int, cache_name: str) -> ProjectAnalysis:
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
    return ProjectAnalysis(root=root, label=label, file_infos=file_infos, profiles=profiles)


def build_cache_payload(primary: ProjectAnalysis, linked: list[ProjectAnalysis]) -> dict[str, object]:
    payload = {"generated_at": utc_now_iso(), "projects": {}}
    for project in [primary] + linked:
        payload["projects"][project.root.as_posix()] = {
            "label": project.label,
            "files": {
                path: {
                    "sha1": info.sha1,
                    "language": info.language,
                    "category": info.category,
                }
                for path, info in sorted(project.file_infos.items())
            },
        }
    return payload


def load_previous_cache(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def compare_with_cache(previous_cache: dict[str, object], projects: list[ProjectAnalysis]) -> tuple[int, int, int]:
    old_projects = previous_cache.get("projects", {}) if isinstance(previous_cache, dict) else {}
    old_projects = old_projects if isinstance(old_projects, dict) else {}
    total_added = total_changed = total_removed = 0

    for project in projects:
        old_files = old_projects.get(project.root.as_posix(), {})
        old_files = old_files.get("files", {}) if isinstance(old_files, dict) else {}
        current_map = {path: info.sha1 for path, info in project.file_infos.items()}
        total_added += sum(1 for path in current_map if path not in old_files)
        total_removed += sum(1 for path in old_files if path not in current_map)
        total_changed += sum(
            1
            for path, sha in current_map.items()
            if path in old_files and isinstance(old_files.get(path), dict) and old_files[path].get("sha1") != sha
        )
    return total_added, total_changed, total_removed


def render_project_section(project: ProjectAnalysis) -> list[str]:
    overview = build_overview(project.file_infos)
    lang_table = "\n".join(f"| {language} | {count} |" for language, count in sorted(overview["by_language"].items(), key=lambda item: item[0])) or "| - | 0 |"
    category_table = "\n".join(f"| {category} | {count} |" for category, count in sorted(overview["by_category"].items(), key=lambda item: item[0])) or "| - | 0 |"
    hot_spot_lines = [
        f"- `{item.path}` | referenciado por `{len(item.imported_by)}` ficheiro(s) | usa `{len(item.uses_files)}` ficheiro(s) | papel: {item.probable_role}"
        for item in overview["hot_spots"]
    ]

    lines: list[str] = []
    lines.append(f"## Projeto analisado: `{project.label}`")
    lines.append("")
    lines.append(f"- **Raiz:** `{project.root.as_posix()}`")
    lines.append(f"- **Perfis detetados:** {', '.join(sorted(project.profiles)) if project.profiles else 'nenhum'}")
    lines.append(f"- **Total de ficheiros:** {overview['total_files']}")
    lines.append("")
    if "trader_bot_backend" in project.profiles:
        lines.append("### Workflows críticos detectados")
        lines.extend(f"- {item}" for item in build_trader_bot_critical_workflows(project.file_infos))
        lines.append("")
    if "trader_bot_frontend" in project.profiles:
        lines.append("### Workflows críticos detectados")
        lines.extend(f"- {item}" for item in build_frontend_critical_workflows(project.file_infos))
        lines.append("")

    lines.append("### Estrutura")
    lines.append("")
    lines.append("```text")
    lines.append(build_tree(sorted(project.file_infos.keys())))
    lines.append("```")
    lines.append("")
    lines.append("### Distribuição por linguagem")
    lines.append("")
    lines.append("| Linguagem | Quantidade |")
    lines.append("|---|---:|")
    lines.append(lang_table)
    lines.append("")
    lines.append("### Distribuição por categoria")
    lines.append("")
    lines.append("| Categoria | Quantidade |")
    lines.append("|---|---:|")
    lines.append(category_table)
    lines.append("")
    lines.append("### Pontos de maior impacto")
    lines.append("")
    lines.extend(hot_spot_lines or ["- Nenhum hot spot identificado."])
    lines.append("")
    lines.append("### Endpoints detectados")
    lines.append("")
    endpoint_lines: list[str] = []
    for info in sorted(overview["endpoint_files"], key=lambda item: item.path.lower()):
        for endpoint in info.endpoints:
            endpoint_lines.append(f"- `{endpoint.method} {normalize_contract_path(endpoint.path)}` -> `{info.path}` ({endpoint.source})")
    lines.extend(endpoint_lines or ["- Nenhum endpoint detetado automaticamente."])
    lines.append("")
    lines.append("### Integrações HTTP/WS detetadas")
    lines.append("")
    integration_lines: list[str] = []
    for info in sorted(project.file_infos.values(), key=lambda item: item.path.lower()):
        refs = []
        refs.extend(info.outbound_http[:6])
        refs.extend(info.outbound_ws[:6])
        if refs:
            integration_lines.append(f"- `{info.path}` -> " + ", ".join(f"`{item}`" for item in refs))
    lines.extend(integration_lines or ["- Nenhuma integração externa detetada automaticamente."])
    lines.append("")
    lines.append("### Mapa ficheiro a ficheiro")
    lines.append("")
    for path in sorted(project.file_infos.keys()):
        info = project.file_infos[path]
        lines.append(f"#### `{info.path}`")
        lines.append("")
        lines.append(f"- **Papel provável:** {info.probable_role}")
        lines.append(f"- **Workflow:** {info.workflow}")
        lines.append(f"- **Categoria:** `{info.category}`")
        lines.append(f"- **Linguagem:** `{info.language}`")
        lines.append(f"- **Tamanho:** {info.size_bytes} bytes")
        lines.append(f"- **Linhas:** {info.line_count} totais | {info.non_empty_line_count} não vazias | {info.comment_line_count} comentários")
        if info.tags:
            lines.append(f"- **Tags:** {', '.join(f'`{tag}`' for tag in info.tags)}")
        if info.classes:
            lines.append(f"- **Classes principais:** {', '.join(f'`{item}`' for item in info.classes[:20])}")
        if info.functions:
            lines.append(f"- **Funções principais:** {', '.join(f'`{item}`' for item in info.functions[:30])}")
        if info.endpoints:
            lines.append("- **Endpoints:** " + "; ".join(f"`{item.method} {normalize_contract_path(item.path)}` ({item.source})" for item in info.endpoints))
        if info.outbound_http:
            lines.append("- **Integrações HTTP:** " + ", ".join(f"`{item}`" for item in info.outbound_http[:20]))
        if info.outbound_ws:
            lines.append("- **Integrações WebSocket:** " + ", ".join(f"`{item}`" for item in info.outbound_ws[:20]))
        if info.path_refs:
            lines.append("- **Paths/contratos encontrados:** " + ", ".join(f"`{normalize_contract_path(item)}`" for item in info.path_refs[:25]))
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
    return lines


def render_cross_repo_section(primary: ProjectAnalysis, linked: list[ProjectAnalysis]) -> list[str]:
    lines: list[str] = []
    links, unmatched_contracts, unused_endpoints = correlate_projects(primary, linked)

    if not linked:
        lines.append("## Ligações backend <-> frontend")
        lines.append("")
        lines.append("- Nenhum repositório ligado foi analisado. Use `--linked-root` ou coloque o repositório irmão ao lado desta raiz.")
        lines.append("")
        return lines

    lines.append("## Ligações backend <-> frontend")
    lines.append("")
    lines.append("Esta secção tenta correlacionar ficheiros consumidores de contrato (frontend) com endpoints expostos (backend).")
    lines.append("")

    lines.append("### Repositórios ligados analisados")
    lines.append("")
    for project in linked:
        lines.append(f"- `{project.label}` -> `{project.root.as_posix()}` | perfis: {', '.join(sorted(project.profiles)) if project.profiles else 'nenhum'}")
    lines.append("")

    lines.append("### Contratos correlacionados")
    lines.append("")
    if links:
        for item in links:
            extra = f" | {item.note}" if item.note else ""
            lines.append(
                f"- `{item.consumer_project}:{item.consumer_file}` consome `{item.contract_path}` -> `{item.provider_project}:{item.provider_file}` expõe `{item.provider_endpoint}`{extra}"
            )
    else:
        lines.append("- Nenhuma correlação automática foi encontrada.")
    lines.append("")

    lines.append("### Contratos do frontend sem match no backend")
    lines.append("")
    if unmatched_contracts:
        for project_name, file_path, contract_path in unmatched_contracts[:100]:
            lines.append(f"- `{project_name}:{file_path}` -> `{contract_path}`")
    else:
        lines.append("- Nenhum contrato sem match detetado.")
    lines.append("")

    lines.append("### Endpoints do backend sem consumidor detetado")
    lines.append("")
    if unused_endpoints:
        for project_name, file_path, endpoint in unused_endpoints[:100]:
            lines.append(f"- `{project_name}:{file_path}` -> `{endpoint}`")
    else:
        lines.append("- Todos os endpoints detetados tiveram algum consumidor ou referência correlacionada.")
    lines.append("")
    return lines


def render_markdown(primary: ProjectAnalysis, linked: list[ProjectAnalysis], output_name: str) -> str:
    lines: list[str] = []
    lines.append("# MAPA DO PROJETO")
    lines.append("")
    lines.append(f"- **Gerado em:** {utc_now_iso()}")
    lines.append(f"- **Ficheiro de saída:** `{output_name}`")
    lines.append(f"- **Raiz principal:** `{primary.root.as_posix()}`")
    lines.append("")
    lines.append("## Objetivo deste ficheiro")
    lines.append("")
    lines.append("Este documento é reescrito automaticamente e tenta explicar o papel de cada ficheiro, os workflows críticos, as ligações internas, endpoints, integrações externas e, quando possível, o contrato backend <-> frontend.")
    lines.append("")
    lines.extend(render_cross_repo_section(primary, linked))
    lines.extend(render_project_section(primary))
    for project in linked:
        lines.extend(render_project_section(project))
    return "\n".join(lines).rstrip() + "\n"


def print_run_summary(previous_cache: dict[str, object], primary: ProjectAnalysis, linked: list[ProjectAnalysis]) -> None:
    added, changed, removed = compare_with_cache(previous_cache, [primary] + linked)
    print(f"[mapa-v3] projeto principal: {primary.label}")
    print(f"[mapa-v3] perfis principais: {', '.join(sorted(primary.profiles)) if primary.profiles else 'nenhum'}")
    print(f"[mapa-v3] repositórios ligados: {len(linked)}")
    if linked:
        print("[mapa-v3] ligados:", ", ".join(f"{item.label} ({item.root.as_posix()})" for item in linked))
    print(f"[mapa-v3] ficheiros analisados (principal): {len(primary.file_infos)}")
    print(f"[mapa-v3] novos: {added} | alterados: {changed} | removidos: {removed}")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def analyze_all(args: argparse.Namespace) -> tuple[ProjectAnalysis, list[ProjectAnalysis], str]:
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Raiz inválida: {root}")

    include_extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.include_ext}
    ignore_dirs = set(DEFAULT_IGNORE_DIRS) | set(args.ignore_dir)

    primary = analyze_project_root(
        root=root,
        label=root.name,
        output_name=args.output,
        include_extensions=include_extensions,
        ignore_dirs=ignore_dirs,
        max_bytes=args.max_bytes,
        cache_name=args.cache,
    )
    linked_roots = detect_linked_roots(root, args.linked_root)
    linked_projects = [
        analyze_project_root(
            root=item,
            label=item.name,
            output_name=args.output,
            include_extensions=include_extensions,
            ignore_dirs=ignore_dirs,
            max_bytes=args.max_bytes,
            cache_name=args.cache,
        )
        for item in linked_roots
    ]
    markdown = render_markdown(primary, linked_projects, args.output)
    return primary, linked_projects, markdown


def run_once(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    output_path = root / args.output
    cache_path = root / args.cache
    previous_cache = load_previous_cache(cache_path)

    try:
        primary, linked_projects, markdown = analyze_all(args)
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2

    write_text(output_path, markdown)
    write_text(cache_path, json.dumps(build_cache_payload(primary, linked_projects), ensure_ascii=False, indent=2))
    print_run_summary(previous_cache, primary, linked_projects)
    print(f"[mapa-v3] escrito em: {output_path}")
    return 0


def watch_loop(args: argparse.Namespace) -> int:
    last_fingerprint = None
    print("[mapa-v3] modo watch ativo. Prima Ctrl+C para terminar.")
    while True:
        root = Path(args.root).expanduser().resolve()
        include_extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.include_ext}
        ignore_dirs = set(DEFAULT_IGNORE_DIRS) | set(args.ignore_dir)

        all_roots = [root] + detect_linked_roots(root, args.linked_root)
        fingerprint_items: list[str] = []
        for base_root in all_roots:
            for path in iter_project_files(base_root, include_extensions=include_extensions, ignore_dirs=ignore_dirs):
                rel = normalize_posix(path, base_root)
                if rel in {args.output, args.cache}:
                    continue
                try:
                    stat = path.stat()
                    fingerprint_items.append(f"{base_root.as_posix()}::{rel}:{int(stat.st_mtime)}:{stat.st_size}")
                except OSError:
                    continue

        current_fingerprint = sha1_text("|".join(sorted(fingerprint_items)))
        if current_fingerprint != last_fingerprint:
            print(f"[mapa-v3] alteração detetada em {utc_now_iso()}. A regenerar...")
            exit_code = run_once(args)
            if exit_code != 0:
                return exit_code
            last_fingerprint = current_fingerprint
        time.sleep(max(1, int(args.watch_interval)))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera um mapa técnico do projeto e reescreve o ficheiro de saída.")
    parser.add_argument("root", nargs="?", default=".", help="Raiz do projeto a analisar. Padrão: diretório atual.")
    parser.add_argument("--linked-root", nargs="*", default=[], help="Raízes adicionais para correlacionar com a raiz principal.")
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
            print("\n[mapa-v3] watch terminado pelo utilizador.")
            return 0
    return run_once(args)


if __name__ == "__main__":
    raise SystemExit(main())
