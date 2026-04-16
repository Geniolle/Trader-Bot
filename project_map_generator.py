from __future__ import annotations

import argparse
import ast
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".env",
    ".txt",
    ".css",
    ".scss",
    ".html",
    ".sql",
    ".sh",
    ".bat",
}

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".output",
    ".cache",
    ".turbo",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".parcel-cache",
    "target",
    ".DS_Store",
}

IGNORE_FILES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "MAPA_DO_PROJETO.md",
}

MAX_FILE_SIZE = 700_000
MAX_PREVIEW_CHARS = 160


@dataclass
class FileInfo:
    path: Path
    rel_path: str
    suffix: str
    size: int
    kind: str = "other"
    role: str = ""
    summary: str = ""
    workflow: str = ""
    doc_hint: str = ""
    imports_raw: list[str] = field(default_factory=list)
    imports_resolved: list[str] = field(default_factory=list)
    imported_by: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    routes: list[str] = field(default_factory=list)
    fetches: list[str] = field(default_factory=list)
    ws_urls: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    preview: str = ""


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name in {"Dockerfile", ".env", ".env.example", "Makefile"}:
        return True
    return False


def should_ignore(path: Path) -> bool:
    if path.name in IGNORE_FILES:
        return True
    parts = set(path.parts)
    return any(part in IGNORE_DIRS for part in parts)


def read_text_safe(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            continue
    return ""


def clean_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def first_meaningful_lines(text: str, max_lines: int = 6) -> str:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lines.append(line)
        if len(lines) >= max_lines:
            break
    joined = " | ".join(lines)
    return joined[:MAX_PREVIEW_CHARS]


def extract_leading_comment(text: str, suffix: str) -> str:
    lines = text.splitlines()
    collected: list[str] = []
    in_block = False
    block_end = ""

    for raw in lines[:30]:
        line = raw.strip()
        if not line and not collected:
            continue

        if suffix == ".py" and line.startswith("#"):
            collected.append(line.lstrip("# ").strip())
            continue

        if suffix in {".js", ".jsx", ".ts", ".tsx", ".css", ".scss"}:
            if line.startswith("//"):
                collected.append(line[2:].strip())
                continue
            if line.startswith("/*"):
                in_block = True
                block_end = "*/"
                cleaned = line[2:]
                if cleaned.endswith("*/"):
                    cleaned = cleaned[:-2]
                    in_block = False
                collected.append(cleaned.strip(" *"))
                continue
            if in_block:
                cleaned = line
                if block_end and cleaned.endswith(block_end):
                    cleaned = cleaned[: -len(block_end)]
                    in_block = False
                collected.append(cleaned.strip(" *"))
                continue

        if collected:
            break
        if line:
            break

    result = clean_line(" ".join(item for item in collected if item))
    return result[:MAX_PREVIEW_CHARS]


def normalize_module_to_path(module: str) -> str:
    return module.replace(".", "/")


def try_candidates(root: Path, candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists() and path.is_file():
            return path.as_posix()
    return None


def resolve_python_import(root: Path, current_file: Path, module: str | None, level: int) -> str | None:
    if level == 0 and not module:
        return None

    if level > 0:
        current_pkg = current_file.parent
        for _ in range(level - 1):
            current_pkg = current_pkg.parent
        rel_module = normalize_module_to_path(module or "")
        base = (current_pkg / rel_module).as_posix().strip("/")
        candidates = []
        if base:
            candidates.extend([f"{base}.py", f"{base}/__init__.py"])
        else:
            candidates.append(f"{current_pkg.as_posix()}/__init__.py")
        resolved = try_candidates(root, candidates)
        if resolved:
            return str(Path(resolved).relative_to(root).as_posix())
        return None

    mod_path = normalize_module_to_path(module or "")
    candidates = [f"{mod_path}.py", f"{mod_path}/__init__.py"]
    resolved = try_candidates(root, candidates)
    if resolved:
        return str(Path(resolved).relative_to(root).as_posix())
    return None


def resolve_js_import(root: Path, current_file: Path, spec: str) -> str | None:
    if not spec.startswith((".", "/")):
        return None

    base = (current_file.parent / spec).resolve() if spec.startswith(".") else (root / spec.lstrip("/"))

    candidates = []
    if base.suffix:
        candidates.append(base)
    else:
        for ext in (".ts", ".tsx", ".js", ".jsx", ".json"):
            candidates.append(Path(str(base) + ext))
        for name in ("index.ts", "index.tsx", "index.js", "index.jsx"):
            candidates.append(base / name)

    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_file():
                return candidate.relative_to(root).as_posix()
        except Exception:
            continue
    return None


def classify_role(rel_path: str) -> tuple[str, str]:
    path = rel_path.replace("\\", "/")

    if path in {"app/main.py", "web/src/main.tsx"}:
        return ("entrypoint", "ponto de entrada")
    if path.endswith("/router.py"):
        return ("router", "router principal")
    if "/api/" in path and "/endpoints/" in path:
        return ("endpoint", "endpoint HTTP")
    if "/providers/" in path and path.endswith("factory.py"):
        return ("provider_factory", "fábrica de providers")
    if "/providers/" in path:
        return ("provider", "provider de dados")
    if "/storage/repositories/" in path and "queries" in Path(path).stem:
        return ("query_repository", "repositório de leitura")
    if "/storage/repositories/" in path:
        return ("repository", "repositório de escrita")
    if "/storage/" in path and Path(path).name == "database.py":
        return ("database", "configuração de base de dados")
    if "/storage/" in path and Path(path).name == "models.py":
        return ("orm_models", "modelos ORM")
    if "/schemas/" in path:
        return ("schema", "schemas / contratos")
    if "/engine/" in path:
        return ("engine", "motor de execução")
    if "/registry/" in path:
        return ("registry", "registo / catálogo")
    if "/strategies/" in path and Path(path).name == "base.py":
        return ("strategy_base", "contrato base de estratégia")
    if "/strategies/" in path:
        return ("strategy", "implementação de estratégia")
    if "/indicators/" in path:
        return ("indicator", "indicador técnico")
    if "/hooks/" in path and Path(path).name.startswith("use"):
        return ("hook", "hook React")
    if "/components/" in path:
        return ("component", "componente UI")
    if "/pages/" in path:
        return ("page", "página UI")
    if "/services/" in path:
        return ("service", "serviço")
    if "/constants/" in path:
        return ("config", "configuração")
    if "/types/" in path:
        return ("types", "tipos / contratos TS")
    if Path(path).name.lower().startswith("readme") or path.endswith(".md"):
        return ("documentation", "documentação")
    return ("file", "ficheiro")


def summarize_from_role(info: FileInfo) -> tuple[str, str]:
    p = info.rel_path
    role = info.role
    imports = ", ".join(info.imports_resolved[:4]) if info.imports_resolved else ""
    routes = ", ".join(info.routes[:4]) if info.routes else ""
    fetches = ", ".join(info.fetches[:3]) if info.fetches else ""

    if role == "ponto de entrada":
        return (
            "Inicializa a aplicação e liga os módulos principais.",
            "Arranque da app -> carrega configuração -> liga routers/componentes -> disponibiliza o sistema.",
        )
    if role == "router principal":
        return (
            "Agrupa e expõe os routers/endpoints do sistema.",
            f"Recebe routers parciais -> monta a API principal -> expõe prefixos e tags.{' Rotas: ' + routes if routes else ''}",
        )
    if role == "endpoint HTTP":
        return (
            "Recebe pedidos HTTP, valida parâmetros e devolve dados ou aciona lógica de negócio.",
            f"Entrada HTTP -> chama camadas importadas -> devolve resposta.{' Rotas detectadas: ' + routes if routes else ''}{' Dependências: ' + imports if imports else ''}",
        )
    if role == "provider de dados":
        return (
            "Busca dados numa origem externa e converte para o formato interno.",
            "Recebe símbolo/timeframe/período -> consulta API externa -> normaliza o retorno -> entrega candles/dados ao backend.",
        )
    if role == "fábrica de providers":
        return (
            "Escolhe qual provider concreto será usado pela aplicação.",
            "Recebe o nome do provider -> instancia a classe correta -> entrega o provider para o fluxo de mercado.",
        )
    if role == "repositório de leitura":
        return (
            "Lê dados persistidos da base segundo filtros específicos.",
            "Recebe sessão e filtros -> monta query -> devolve linhas ordenadas para as camadas superiores.",
        )
    if role == "repositório de escrita":
        return (
            "Persiste dados de domínio na base de dados.",
            "Recebe objetos vindos da lógica de negócio -> grava/atualiza na base -> devolve objetos persistidos.",
        )
    if role == "configuração de base de dados":
        return (
            "Configura engine, sessão e acesso central à base de dados.",
            "Lê settings -> cria engine -> cria SessionLocal -> fornece sessão para queries e gravações.",
        )
    if role == "modelos ORM":
        return (
            "Define as tabelas e colunas persistidas na base.",
            "Mapeia entidades para tabelas -> impõe constraints -> serve de base às queries e repositórios.",
        )
    if role == "motor de execução":
        return (
            "Coordena a lógica central de execução do domínio.",
            "Recebe dados e configuração -> processa casos/regras -> produz resultado agregado para persistência ou resposta.",
        )
    if role == "registo / catálogo":
        return (
            "Mantém o catálogo de estratégias ou módulos disponíveis.",
            "Regista implementações -> permite listar/obter por chave -> serve a API e os motores internos.",
        )
    if role == "contrato base de estratégia":
        return (
            "Define a interface comum que todas as estratégias precisam implementar.",
            "Declara métodos obrigatórios -> padroniza trigger, criação, atualização e fecho de casos.",
        )
    if role == "implementação de estratégia":
        return (
            "Implementa uma estratégia concreta de análise/decisão.",
            "Recebe candles e parâmetros -> calcula indicadores -> valida trigger -> cria e fecha casos conforme a regra.",
        )
    if role == "indicador técnico":
        return (
            "Calcula um indicador técnico reutilizável por estratégias e análises.",
            "Recebe séries/candles -> calcula indicador -> devolve valor ou série derivada.",
        )
    if role == "hook React":
        return (
            "Encapsula estado, efeitos e integração do frontend.",
            f"Recebe seleção/estado -> consome API ou WebSocket -> normaliza dados -> devolve estado para componentes.{' Fetch/WS: ' + (fetches or ', '.join(info.ws_urls[:2])) if (fetches or info.ws_urls) else ''}",
        )
    if role == "componente UI":
        return (
            "Renderiza uma parte da interface com base em props e hooks.",
            "Recebe dados do estado/hook -> monta bloco visual -> apresenta informação ou ações ao utilizador.",
        )
    if role == "página UI":
        return (
            "Organiza uma página completa do frontend.",
            "Recebe dados de hooks/serviços -> compõe componentes -> mostra o fluxo de uma área da aplicação.",
        )
    if role == "serviço":
        return (
            "Fornece funções reutilizáveis de integração, transformação ou acesso a dados.",
            f"Recebe parâmetros -> executa tarefa especializada -> devolve resultado para hooks/componentes/outros módulos.{' Integrações: ' + fetches if fetches else ''}",
        )
    if role == "configuração":
        return (
            "Centraliza constantes e configuração consumidas por outros ficheiros.",
            "Define URLs, flags, limites ou parâmetros globais -> é lido por múltiplos módulos.",
        )
    if role == "tipos / contratos TS":
        return (
            "Define tipos usados para garantir consistência entre módulos do frontend.",
            "Modela contratos de dados -> é importado por hooks, serviços e componentes.",
        )
    if role == "schemas / contratos":
        return (
            "Define contratos de entrada e saída da API.",
            "Recebe modelos/domínio -> valida serialização -> padroniza respostas para os clientes.",
        )
    if role == "documentação":
        return (
            "Documenta a estrutura, execução ou arquitetura do projeto.",
            "Serve como referência humana para entender o sistema, execução e dependências.",
        )

    return (
        "Ficheiro utilitário ou de suporte dentro do projeto.",
        "Participa de forma auxiliar no fluxo global; a função exata deve ser lida em conjunto com os imports e símbolos detectados.",
    )


def parse_python(root: Path, file_info: FileInfo, text: str) -> None:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        file_info.notes.append(f"Falha ao analisar AST Python: {exc}")
        return

    docstring = ast.get_docstring(tree)
    if docstring:
        file_info.doc_hint = clean_line(docstring.splitlines()[0])[:MAX_PREVIEW_CHARS]

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            file_info.functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            file_info.classes.append(node.name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                file_info.imports_raw.append(mod)
                resolved = resolve_python_import(root, file_info.path, mod, 0)
                if resolved:
                    file_info.imports_resolved.append(resolved)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            dotted = "." * node.level + module
            file_info.imports_raw.append(dotted or ".")
            resolved = resolve_python_import(root, file_info.path, module, node.level)
            if resolved:
                file_info.imports_resolved.append(resolved)
        elif isinstance(node, ast.Call):
            func_text = ast.unparse(node.func) if hasattr(ast, "unparse") else ""
            if re.search(r"router\.(get|post|put|delete|patch|websocket)$", func_text):
                if node.args and isinstance(node.args[0], ast.Constant):
                    route = f"{func_text.split('.')[-1].upper()} {node.args[0].value}"
                    file_info.routes.append(str(route))

    file_info.imports_resolved = sorted(set(file_info.imports_resolved))
    file_info.imports_raw = sorted(set(file_info.imports_raw))
    file_info.classes = sorted(set(file_info.classes))
    file_info.functions = sorted(set(file_info.functions))
    file_info.routes = sorted(set(file_info.routes))


JS_IMPORT_RE = re.compile(
    r"(?:import\s+.*?from\s+['\"](?P<imp1>[^'\"]+)['\"]|require\(\s*['\"](?P<imp2>[^'\"]+)['\"]\s*\))"
)
FETCH_RE = re.compile(r"fetch\(\s*[`'\"](?P<url>[^`'\"]+)[`'\"]")
WS_RE = re.compile(r"new\s+WebSocket\(\s*(?P<expr>[^\)]+)\)")
EXPORT_RE = re.compile(r"export\s+(?:default\s+)?(?:function|const|class|type|interface)\s+(?P<name>[A-Za-z0-9_]+)")
FUNC_RE = re.compile(r"(?:function|const)\s+(?P<name>[A-Za-z0-9_]+)")
ROUTE_HINT_RE = re.compile(r"/api/v\d+/[A-Za-z0-9_\-/{}/]+")


def parse_jsts(root: Path, file_info: FileInfo, text: str) -> None:
    for match in JS_IMPORT_RE.finditer(text):
        spec = match.group("imp1") or match.group("imp2")
        if not spec:
            continue
        file_info.imports_raw.append(spec)
        resolved = resolve_js_import(root, file_info.path, spec)
        if resolved:
            file_info.imports_resolved.append(resolved)

    for match in FETCH_RE.finditer(text):
        file_info.fetches.append(match.group("url"))

    for match in WS_RE.finditer(text):
        file_info.ws_urls.append(clean_line(match.group("expr")))

    for match in EXPORT_RE.finditer(text):
        file_info.exports.append(match.group("name"))

    for match in FUNC_RE.finditer(text):
        name = match.group("name")
        if name not in {"if", "for", "while", "switch", "return"}:
            file_info.functions.append(name)

    for route in ROUTE_HINT_RE.findall(text):
        file_info.routes.append(route)

    file_info.imports_resolved = sorted(set(file_info.imports_resolved))
    file_info.imports_raw = sorted(set(file_info.imports_raw))
    file_info.fetches = sorted(set(file_info.fetches))
    file_info.ws_urls = sorted(set(file_info.ws_urls))
    file_info.exports = sorted(set(file_info.exports))
    file_info.functions = sorted(set(file_info.functions))
    file_info.routes = sorted(set(file_info.routes))


def collect_files(root: Path) -> dict[str, FileInfo]:
    result: dict[str, FileInfo] = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_ignore(path.relative_to(root)):
            continue
        if path.stat().st_size > MAX_FILE_SIZE:
            continue
        if not is_text_file(path):
            continue

        rel = path.relative_to(root).as_posix()
        kind, role = classify_role(rel)
        info = FileInfo(
            path=path,
            rel_path=rel,
            suffix=path.suffix.lower(),
            size=path.stat().st_size,
            kind=kind,
            role=role,
        )

        text = read_text_safe(path)
        info.preview = first_meaningful_lines(text)
        comment_hint = extract_leading_comment(text, info.suffix)
        if comment_hint:
            info.doc_hint = comment_hint

        if info.suffix == ".py":
            parse_python(root, info, text)
        elif info.suffix in {".js", ".jsx", ".ts", ".tsx"}:
            parse_jsts(root, info, text)
        else:
            for route in ROUTE_HINT_RE.findall(text):
                info.routes.append(route)
            info.routes = sorted(set(info.routes))

        summary, workflow = summarize_from_role(info)
        info.summary = summary
        info.workflow = workflow
        result[rel] = info

    return result


def build_reverse_graph(files: dict[str, FileInfo]) -> None:
    reverse: dict[str, set[str]] = defaultdict(set)
    for rel, info in files.items():
        for dep in info.imports_resolved:
            if dep in files:
                reverse[dep].add(rel)

    for rel, users in reverse.items():
        files[rel].imported_by = sorted(users)


def section_global_overview(root: Path, files: dict[str, FileInfo]) -> str:
    total = len(files)
    by_role: dict[str, int] = defaultdict(int)
    for info in files.values():
        by_role[info.role] += 1

    lines = [
        "# MAPA DO PROJETO",
        "",
        f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Raiz analisada: {root.as_posix()}",
        f"Total de ficheiros analisados: {total}",
        "",
        "## O que este ficheiro faz",
        "",
        "Este documento tenta responder, para cada ficheiro:",
        "- o que ele parece ser dentro da arquitetura",
        "- qual workflow ele executa",
        "- com que outros ficheiros ele se liga",
        "- quem o usa e quem ele usa",
        "",
        "## Limites da leitura",
        "",
        "- Dependências e rotas são lidas de forma determinística.",
        "- O resumo funcional é heurístico; melhora muito quando os ficheiros têm nomes claros, comentários e docstrings.",
        "- Sempre que executar de novo, o ficheiro será reescrito com o estado atual do projeto.",
        "",
        "## Resumo por tipo",
        "",
    ]

    for role, count in sorted(by_role.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- {role}: {count}")

    return "\n".join(lines)


def section_detected_workflows(files: dict[str, FileInfo]) -> str:
    lines = ["## Workflows detectados", ""]

    def exists(rel: str) -> bool:
        return rel in files

    if exists("app/api/v1/endpoints/runs.py"):
        lines.extend(
            [
                "### Fluxo histórico de runs",
                "1. `app/api/v1/endpoints/runs.py` recebe o pedido histórico.",
                "2. Tenta ler candles já gravados na base por `app/storage/repositories/candle_queries.py`.",
                "3. Se não existirem candles locais, escolhe o provider em `app/providers/factory.py`.",
                "4. O provider concreto, como `app/providers/twelvedata.py`, busca os dados externos.",
                "5. `app/storage/repositories/candle_repository.py` grava os candles no SQLite.",
                "6. `app/engine/run_engine.py` executa a estratégia.",
                "7. `app/storage/repositories/run_repository.py`, `case_repository.py` e `metrics_repository.py` persistem o resultado.",
                "",
            ]
        )

    if exists("app/api/v1/endpoints/candles.py"):
        lines.extend(
            [
                "### Fluxo de leitura de candles pela API",
                "1. `app/api/v1/endpoints/candles.py` recebe símbolo, timeframe e intervalo.",
                "2. `app/storage/repositories/candle_queries.py` consulta a base local.",
                "3. Os dados são serializados por `app/schemas/run.py` e devolvidos ao cliente.",
                "",
            ]
        )

    if exists("web/src/hooks/useCandles.ts"):
        lines.extend(
            [
                "### Fluxo HTTP do frontend para candles",
                "1. `web/src/hooks/useCandles.ts` chama a API `/candles`.",
                "2. Normaliza, deduplica e preserva o último snapshot válido.",
                "3. Entrega os candles prontos ao gráfico e aos componentes do dashboard.",
                "",
            ]
        )

    if exists("web/src/hooks/useRealtimeFeed.ts"):
        lines.extend(
            [
                "### Fluxo realtime do frontend",
                "1. `web/src/hooks/useRealtimeFeed.ts` abre WebSocket.",
                "2. Processa `initial_candles`, `candle_tick`, `candles_refresh` e `provider_error`.",
                "3. Atualiza o estado do gráfico e tenta confirmar persistência no backend.",
                "",
            ]
        )

    if len(lines) == 2:
        lines.append("Nenhum workflow padrão reconhecido pelas regras atuais.")

    return "\n".join(lines)


def format_list(items: list[str], max_items: int = 8) -> str:
    if not items:
        return "-"
    shown = items[:max_items]
    suffix = "" if len(items) <= max_items else f" ... (+{len(items) - max_items})"
    return ", ".join(shown) + suffix


def file_section(info: FileInfo) -> str:
    lines = [f"## {info.rel_path}", ""]
    lines.append(f"- Tipo: {info.role}")
    lines.append(f"- Tamanho: {info.size} bytes")
    lines.append(f"- Função provável: {info.summary}")
    lines.append(f"- Workflow provável: {info.workflow}")
    if info.doc_hint:
        lines.append(f"- Dica encontrada no próprio ficheiro: {info.doc_hint}")
    lines.append(f"- Usa: {format_list(info.imports_resolved)}")
    lines.append(f"- É usado por: {format_list(info.imported_by)}")
    if info.routes:
        lines.append(f"- Rotas / endpoints detectados: {format_list(info.routes)}")
    if info.fetches:
        lines.append(f"- Fetch / URLs detectadas: {format_list(info.fetches)}")
    if info.ws_urls:
        lines.append(f"- WebSocket detectado: {format_list(info.ws_urls)}")
    if info.classes:
        lines.append(f"- Classes detectadas: {format_list(info.classes)}")
    if info.functions:
        lines.append(f"- Funções detectadas: {format_list(info.functions)}")
    if info.exports:
        lines.append(f"- Exports detectados: {format_list(info.exports)}")
    if info.preview:
        lines.append(f"- Pré-visualização: {info.preview}")
    if info.notes:
        lines.append(f"- Notas: {format_list(info.notes)}")
    lines.append("")
    return "\n".join(lines)


def build_document(root: Path, files: dict[str, FileInfo]) -> str:
    sections = [
        section_global_overview(root, files),
        "",
        section_detected_workflows(files),
        "",
        "## Mapa ficheiro a ficheiro",
        "",
    ]

    for rel in sorted(files):
        sections.append(file_section(files[rel]))

    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera um mapa textual do projeto com função, workflow e ligações por ficheiro."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Raiz do projeto a analisar. Ex.: .",
    )
    parser.add_argument(
        "--output",
        default="MAPA_DO_PROJETO.md",
        help="Nome do ficheiro de saída a criar/atualizar na raiz do projeto.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Raiz inválida: {root}")

    files = collect_files(root)
    build_reverse_graph(files)
    content = build_document(root, files)

    output_path = root / args.output
    output_path.write_text(content, encoding="utf-8")

    print(f"Mapa gerado com sucesso: {output_path}")
    print(f"Ficheiros analisados: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
