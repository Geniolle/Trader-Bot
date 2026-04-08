from __future__ import annotations

import os
import shlex
import sqlite3
import subprocess
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote, urlparse

from app.core.logging import get_logger
from app.core.settings import get_settings

logger = get_logger(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_symbol(symbol: str) -> str:
    if symbol is None:
        return ""
    value = symbol.upper().strip()
    for ch in ["/", "-", "_", " "]:
        value = value.replace(ch, "")
    return value


def get_db_path() -> str:
    settings = get_settings()

    env_db_path = os.getenv("DB_PATH", "").strip()
    if env_db_path:
        logger.info("[STAGE_TESTS] DB_PATH encontrado no ambiente: %s", env_db_path)
        return env_db_path

    database_url = (settings.database_url or "").strip()
    logger.info("[STAGE_TESTS] database_url lida das settings: %s", database_url)

    if not database_url:
        raise RuntimeError("database_url não configurada.")

    if database_url.startswith("sqlite:///"):
        raw_path = database_url.replace("sqlite:///", "", 1)
        raw_path = unquote(raw_path).strip()

        if not raw_path:
            raise RuntimeError("database_url SQLite inválida.")

        logger.info("[STAGE_TESTS] DB path derivado de database_url: %s", raw_path)
        return raw_path

    parsed = urlparse(database_url)
    if parsed.scheme == "sqlite":
        raw_path = unquote(parsed.path or "").strip()
        if raw_path.startswith("/"):
            raw_path = raw_path[1:]

        if not raw_path:
            raise RuntimeError("database_url SQLite inválida.")

        logger.info("[STAGE_TESTS] DB path derivado via urlparse: %s", raw_path)
        return raw_path

    raise RuntimeError(
        "Stage Tests suporta apenas SQLite neste momento. "
        f"database_url atual: {database_url}"
    )


def connect_db() -> sqlite3.Connection:
    db_path = get_db_path()
    logger.info("[STAGE_TESTS] A abrir ligação SQLite: %s", db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def list_stage_test_options(min_candles: int = 1) -> dict[str, Any]:
    logger.info("[STAGE_TESTS] list_stage_test_options | min_candles=%s", min_candles)

    sql = """
    SELECT
        UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) AS normalized_symbol,
        timeframe,
        COUNT(*) AS candles_count,
        MIN(open_time) AS first_candle,
        MAX(open_time) AS last_candle
    FROM candles
    WHERE symbol IS NOT NULL
      AND TRIM(symbol) <> ''
      AND timeframe IS NOT NULL
      AND TRIM(timeframe) <> ''
    GROUP BY normalized_symbol, timeframe
    HAVING COUNT(*) >= ?
    ORDER BY normalized_symbol ASC, timeframe ASC
    """

    with connect_db() as conn:
        rows = conn.execute(sql, (min_candles,)).fetchall()

    items: list[dict[str, Any]] = []
    for row in rows:
        items.append(
            {
                "symbol": row["normalized_symbol"],
                "timeframe": row["timeframe"],
                "candles_count": int(row["candles_count"]),
                "first_candle": row["first_candle"],
                "last_candle": row["last_candle"],
            }
        )

    logger.info("[STAGE_TESTS] options carregadas | total=%s", len(items))

    return {
        "items": items,
        "refreshed_at": utc_now_iso(),
    }


def validate_symbol_timeframe(symbol: str, timeframe: str, min_candles: int = 1) -> None:
    normalized = normalize_symbol(symbol)

    logger.info(
        "[STAGE_TESTS] validate_symbol_timeframe | symbol=%s | timeframe=%s | min_candles=%s",
        normalized,
        timeframe,
        min_candles,
    )

    sql = """
    SELECT COUNT(*) AS total
    FROM candles
    WHERE UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) = ?
      AND timeframe = ?
    """

    with connect_db() as conn:
        row = conn.execute(sql, (normalized, timeframe)).fetchone()

    total = int(row["total"]) if row else 0

    logger.info(
        "[STAGE_TESTS] validate_symbol_timeframe | encontrados=%s",
        total,
    )

    if total < min_candles:
        raise ValueError(
            f"Não existem candles suficientes para {normalized} {timeframe}. "
            f"Encontrados: {total}, mínimo exigido: {min_candles}."
        )


def build_stage_test_command(
    symbol: str,
    timeframe: str,
    strategy: str,
    extra_args: list[str],
) -> list[str]:
    base_command = os.getenv("STAGE_TEST_RUN_COMMAND", "").strip()

    if not base_command:
        raise RuntimeError(
            "STAGE_TEST_RUN_COMMAND não configurado. "
            "Exemplo: python -m app.stage_tests.runner"
        )

    command = shlex.split(base_command)
    command.extend(
        [
            "--symbol",
            normalize_symbol(symbol),
            "--timeframe",
            timeframe,
            "--strategy",
            strategy,
        ]
    )

    if extra_args:
        command.extend(extra_args)

    logger.info("[STAGE_TESTS] command=%s", command)
    return command


def run_stage_test(
    symbol: str,
    timeframe: str,
    strategy: str,
    min_candles: int = 1,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    extra_args = extra_args or []

    logger.info(
        "[STAGE_TESTS] run_stage_test | symbol=%s | timeframe=%s | strategy=%s | min_candles=%s | extra_args=%s",
        symbol,
        timeframe,
        strategy,
        min_candles,
        extra_args,
    )

    validate_symbol_timeframe(
        symbol=symbol,
        timeframe=timeframe,
        min_candles=min_candles,
    )

    command = build_stage_test_command(
        symbol=symbol,
        timeframe=timeframe,
        strategy=strategy,
        extra_args=extra_args,
    )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    logger.info(
        "[STAGE_TESTS] run concluído | return_code=%s | ok=%s",
        result.returncode,
        result.returncode == 0,
    )

    return {
        "ok": result.returncode == 0,
        "command": command,
        "symbol": normalize_symbol(symbol),
        "timeframe": timeframe,
        "strategy": strategy,
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
        "return_code": int(result.returncode),
    }