# app/stage_tests/runner.py
# Executado por:
# - POST /api/v1/stage-tests/run
#
# Argumentos:
# - --symbol
# - --timeframe
# - --strategy
#
# Saída:
# - logs humanos em stdout
# - uma linha final STAGE_TEST_RESULT_JSON=<json> para a API extrair métricas

from __future__ import annotations

import argparse
import inspect
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from urllib.parse import unquote, urlparse

from app.core.settings import get_settings
from app.models.domain.candle import Candle
from app.models.domain.strategy_config import StrategyConfig
from app.models.domain.strategy_run import StrategyRun
from app.registry.strategy_registry import build_strategy_registry
from app.stage_tests.strategy_mapper import (
    get_default_parameters,
    resolve_runtime_strategy_key,
)


def normalize_symbol(symbol: str) -> str:
    value = symbol.upper().strip()
    for ch in ["/", "-", "_", " "]:
        value = value.replace(ch, "")
    return value


def get_db_path() -> str:
    env_db_path = os.getenv("DB_PATH", "").strip()
    if env_db_path:
        return env_db_path

    settings = get_settings()
    database_url = (settings.database_url or "").strip()

    if not database_url:
        raise RuntimeError("database_url não configurada e DB_PATH não definido.")

    if database_url.startswith("sqlite:///"):
        raw_path = database_url.replace("sqlite:///", "", 1)
        raw_path = unquote(raw_path).strip()
        if not raw_path:
            raise RuntimeError("database_url SQLite inválida.")
        return raw_path

    parsed = urlparse(database_url)
    if parsed.scheme == "sqlite":
        raw_path = unquote(parsed.path or "").strip()
        if raw_path.startswith("/"):
            raw_path = raw_path[1:]
        if not raw_path:
            raise RuntimeError("database_url SQLite inválida.")
        return raw_path

    raise RuntimeError(
        "Stage Tests suporta apenas SQLite neste momento. "
        f"database_url atual: {database_url}"
    )


def get_existing_candle_columns(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("PRAGMA table_info(candles)").fetchall()
    return {str(row[1]) for row in rows}


def load_candles_rows(symbol: str, timeframe: str) -> list[sqlite3.Row]:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row

    existing_columns = get_existing_candle_columns(conn)

    required_columns = [
        "open_time",
        "close_time",
        "open",
        "high",
        "low",
        "close",
        "symbol",
        "timeframe",
    ]

    missing_required = [col for col in required_columns if col not in existing_columns]
    if missing_required:
        conn.close()
        raise RuntimeError(
            f"A tabela candles não contém as colunas obrigatórias: {missing_required}"
        )

    candidate_columns = [
        "id",
        "asset_id",
        "symbol",
        "timeframe",
        "open_time",
        "close_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "provider",
        "market_session",
        "timezone",
        "is_delayed",
        "is_mock",
    ]

    selected_columns = [col for col in candidate_columns if col in existing_columns]
    select_clause = ",\n        ".join(selected_columns)

    sql = f"""
    SELECT
        {select_clause}
    FROM candles
    WHERE UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) = ?
      AND timeframe = ?
    ORDER BY open_time ASC
    """

    rows = conn.execute(sql, (normalize_symbol(symbol), timeframe)).fetchall()
    conn.close()
    return rows


def parse_value(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (int, float, bool, Decimal)):
        return value

    if isinstance(value, str):
        raw = value.strip()

        if raw == "":
            return raw

        lower = raw.lower()
        if lower in {"true", "false"}:
            return lower == "true"

        try:
            if any(ch in raw for ch in [".", ","]):
                normalized = raw.replace(",", ".")
                return Decimal(normalized)
            return int(raw)
        except Exception:
            return raw

    return value


def get_constructor_fields(cls: type) -> set[str]:
    try:
        signature = inspect.signature(cls)
        return {
            name
            for name, parameter in signature.parameters.items()
            if name != "self"
            and parameter.kind
            in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            )
        }
    except Exception:
        annotations = getattr(cls, "__annotations__", {})
        if isinstance(annotations, dict):
            return set(annotations.keys())
        return set()


def instantiate_model(cls: type, candidate_values: dict[str, Any]) -> Any:
    accepted_fields = get_constructor_fields(cls)

    if accepted_fields:
        filtered = {
            key: value
            for key, value in candidate_values.items()
            if key in accepted_fields
        }
        return cls(**filtered)

    instance = cls()
    for key, value in candidate_values.items():
        if hasattr(instance, key):
            setattr(instance, key, value)
    return instance


def build_candle(row: sqlite3.Row) -> Candle:
    raw = dict(row)

    candidate_values = {
        "id": raw.get("id"),
        "asset_id": raw.get("asset_id"),
        "symbol": raw.get("symbol"),
        "timeframe": raw.get("timeframe"),
        "open_time": raw.get("open_time"),
        "close_time": raw.get("close_time"),
        "open": parse_value(raw.get("open")),
        "high": parse_value(raw.get("high")),
        "low": parse_value(raw.get("low")),
        "close": parse_value(raw.get("close")),
        "volume": parse_value(raw.get("volume")),
        "source": raw.get("source"),
        "provider": raw.get("provider"),
        "market_session": raw.get("market_session"),
        "timezone": raw.get("timezone"),
        "is_delayed": raw.get("is_delayed"),
        "is_mock": raw.get("is_mock"),
    }

    return instantiate_model(Candle, candidate_values)


def parse_extra_args(extra: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}

    i = 0
    while i < len(extra):
        token = extra[i].strip()

        if not token.startswith("--"):
            i += 1
            continue

        key = token[2:].strip().replace("-", "_")
        if not key:
            i += 1
            continue

        next_value: Any = True
        if i + 1 < len(extra) and not extra[i + 1].startswith("--"):
            next_value = parse_value(extra[i + 1])
            i += 1

        parsed[key] = next_value
        i += 1

    return parsed


def build_strategy_config(
    stage_test_strategy: str,
    runtime_strategy: str,
    symbol: str,
    timeframe: str,
    extra_parameters: dict[str, Any],
) -> StrategyConfig:
    defaults = get_default_parameters(stage_test_strategy)
    parameters = {**defaults, **extra_parameters}
    now_iso = datetime.now(timezone.utc).isoformat()

    candidate_values = {
        "id": str(uuid.uuid4()),
        "strategy_key": runtime_strategy,
        "symbol": normalize_symbol(symbol),
        "timeframe": timeframe,
        "name": f"stage-test::{stage_test_strategy}",
        "label": f"stage-test::{stage_test_strategy}",
        "parameters": parameters,
        "is_enabled": True,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    return instantiate_model(StrategyConfig, candidate_values)


def build_strategy_run(
    runtime_strategy: str,
    strategy_config_id: str,
    symbol: str,
    timeframe: str,
    start_at: str,
    end_at: str,
) -> StrategyRun:
    now_iso = datetime.now(timezone.utc).isoformat()

    candidate_values = {
        "id": str(uuid.uuid4()),
        "strategy_key": runtime_strategy,
        "strategy_config_id": strategy_config_id,
        "symbol": normalize_symbol(symbol),
        "timeframe": timeframe,
        "status": "running",
        "mode": "historical",
        "start_at": start_at,
        "end_at": end_at,
        "started_at": now_iso,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    return instantiate_model(StrategyRun, candidate_values)


def safe_attr(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def decision_is_triggered(decision: Any) -> bool:
    candidates = [
        safe_attr(decision, "triggered"),
        safe_attr(decision, "is_triggered"),
        safe_attr(decision, "should_trigger"),
        safe_attr(decision, "open_case"),
        safe_attr(decision, "fired"),
    ]
    return any(value is True for value in candidates)


def decision_should_close(decision: Any) -> bool:
    candidates = [
        safe_attr(decision, "should_close"),
        safe_attr(decision, "close_case"),
        safe_attr(decision, "closed"),
        safe_attr(decision, "is_closed"),
    ]
    return any(value is True for value in candidates)


def summarize_case_outcome(case: Any) -> str:
    outcome = safe_attr(case, "outcome")
    status = safe_attr(case, "status")
    close_reason = safe_attr(case, "close_reason")

    joined = " | ".join(
        str(v).lower()
        for v in [outcome, status, close_reason]
        if v is not None and str(v).strip()
    )

    if any(word in joined for word in ["hit", "win", "target", "tp", "profit"]):
        return "hit"

    if any(word in joined for word in ["fail", "loss", "stop", "sl"]):
        return "fail"

    if any(word in joined for word in ["timeout", "expired", "time_out"]):
        return "timeout"

    return "other"


def pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage Testes runner")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--strategy", required=True)
    args, extra = parser.parse_known_args()

    requested_strategy = args.strategy
    runtime_strategy = resolve_runtime_strategy_key(requested_strategy)
    extra_parameters = parse_extra_args(extra)

    registry = build_strategy_registry()

    if not registry.has(runtime_strategy):
        raise RuntimeError(
            f"Strategy mapeada não existe no registry: {runtime_strategy}"
        )

    strategy_impl = registry.get(runtime_strategy)

    rows = load_candles_rows(args.symbol, args.timeframe)
    candles = [build_candle(row) for row in rows]

    print("============================================================")
    print("STAGE TESTES V2")
    print("============================================================")
    print(f"DATA/HORA              : {datetime.now().isoformat()}")
    print(f"DB_PATH                : {get_db_path()}")
    print(f"SYMBOL                 : {normalize_symbol(args.symbol)}")
    print(f"TIMEFRAME              : {args.timeframe}")
    print(f"STAGE_TEST_STRATEGY    : {requested_strategy}")
    print(f"RUNTIME_STRATEGY       : {runtime_strategy}")
    print(f"STRATEGY_CLASS         : {strategy_impl.__class__.__name__}")
    print(f"EXTRA ARGS             : {extra}")
    print(f"EXTRA PARAMETERS       : {extra_parameters}")
    print(f"TOTAL CANDLES          : {len(candles)}")

    if not candles:
        print("RESULTADO              : SEM DADOS")
        raise SystemExit(2)

    first_row = rows[0]
    last_row = rows[-1]

    config = build_strategy_config(
        stage_test_strategy=requested_strategy,
        runtime_strategy=runtime_strategy,
        symbol=args.symbol,
        timeframe=args.timeframe,
        extra_parameters=extra_parameters,
    )

    config_id = safe_attr(config, "id")
    if not config_id:
        raise RuntimeError("StrategyConfig criado sem id.")

    run = build_strategy_run(
        runtime_strategy=runtime_strategy,
        strategy_config_id=str(config_id),
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_at=str(first_row["open_time"]),
        end_at=str(last_row["close_time"] or last_row["open_time"]),
    )

    warmup = strategy_impl.warmup_period(config)
    indicators = strategy_impl.calculate_indicators(candles, config)

    print(f"WARMUP                 : {warmup}")
    print(
        f"INDICATORS_TYPE        : {type(indicators).__name__ if indicators is not None else 'None'}"
    )

    open_cases: list[Any] = []
    closed_cases: list[Any] = []
    trigger_count = 0

    for index in range(max(warmup, 0), len(candles)):
        candle = candles[index]

        try:
            trigger_decision = strategy_impl.check_trigger(
                candles=candles,
                index=index,
                config=config,
            )
        except Exception as exc:
            print(f"ERRO_TRIGGER           : index={index} | erro={exc}")
            continue

        if decision_is_triggered(trigger_decision):
            trigger_count += 1
            try:
                new_case = strategy_impl.create_case(
                    candles=candles,
                    index=index,
                    config=config,
                    run=run,
                )
                open_cases.append(new_case)
            except Exception as exc:
                print(f"ERRO_CREATE_CASE       : index={index} | erro={exc}")

        still_open_cases: list[Any] = []

        for case in open_cases:
            try:
                updated_case = strategy_impl.update_case(
                    case=case,
                    candle=candle,
                    config=config,
                )
            except Exception as exc:
                print(f"ERRO_UPDATE_CASE       : index={index} | erro={exc}")
                still_open_cases.append(case)
                continue

            try:
                close_decision = strategy_impl.should_close_case(
                    case=updated_case,
                    candle=candle,
                    config=config,
                )
            except Exception as exc:
                print(f"ERRO_SHOULD_CLOSE      : index={index} | erro={exc}")
                still_open_cases.append(updated_case)
                continue

            if decision_should_close(close_decision):
                try:
                    closed_case = strategy_impl.close_case(
                        case=updated_case,
                        candle=candle,
                        config=config,
                        decision=close_decision,
                    )
                    closed_cases.append(closed_case)
                except Exception as exc:
                    print(f"ERRO_CLOSE_CASE        : index={index} | erro={exc}")
                    still_open_cases.append(updated_case)
            else:
                still_open_cases.append(updated_case)

        open_cases = still_open_cases

    hit_count = 0
    fail_count = 0
    timeout_count = 0
    other_count = 0

    for case in closed_cases:
        bucket = summarize_case_outcome(case)
        if bucket == "hit":
            hit_count += 1
        elif bucket == "fail":
            fail_count += 1
        elif bucket == "timeout":
            timeout_count += 1
        else:
            other_count += 1

    print(f"PRIMEIRO               : {first_row['open_time']}")
    print(f"ÚLTIMO                 : {last_row['open_time']}")
    print(f"TRIGGERS               : {trigger_count}")
    print(f"OPEN_CASES_FINAL       : {len(open_cases)}")
    print(f"CLOSED_CASES           : {len(closed_cases)}")
    print(f"HITS                   : {hit_count}")
    print(f"FAILS                  : {fail_count}")
    print(f"TIMEOUTS               : {timeout_count}")
    print(f"OTHERS                 : {other_count}")
    print("RESULTADO              : RUN EXECUTADO COM SUCESSO")
    print("============================================================")

    metrics = {
        "strategy_class": strategy_impl.__class__.__name__,
        "runtime_strategy": runtime_strategy,
        "total_candles": len(candles),
        "warmup": int(warmup),
        "triggers": trigger_count,
        "open_cases_final": len(open_cases),
        "closed_cases": len(closed_cases),
        "hits": hit_count,
        "fails": fail_count,
        "timeouts": timeout_count,
        "others": other_count,
        "hit_rate": pct(hit_count, len(closed_cases)),
        "fail_rate": pct(fail_count, len(closed_cases)),
        "timeout_rate": pct(timeout_count, len(closed_cases)),
        "first_candle": str(first_row["open_time"]),
        "last_candle": str(last_row["open_time"]),
    }

    print(f"STAGE_TEST_RESULT_JSON={json.dumps(metrics, ensure_ascii=False)}")


if __name__ == "__main__":
    main()