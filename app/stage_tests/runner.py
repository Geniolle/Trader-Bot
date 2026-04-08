import argparse
import os
import sqlite3
from datetime import datetime


def normalize_symbol(symbol: str) -> str:
    value = symbol.upper().strip()
    for ch in ["/", "-", "_", " "]:
        value = value.replace(ch, "")
    return value


def get_db_path() -> str:
    db_path = os.getenv("DB_PATH", "").strip()
    if not db_path:
        raise RuntimeError("DB_PATH não configurado.")
    return db_path


def load_candles(symbol: str, timeframe: str):
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row

    sql = """
    SELECT
        open_time,
        close_time,
        open,
        high,
        low,
        close,
        source
    FROM candles
    WHERE UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) = ?
      AND timeframe = ?
    ORDER BY open_time ASC
    """

    rows = conn.execute(sql, (normalize_symbol(symbol), timeframe)).fetchall()
    conn.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage Testes runner")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--strategy", required=True)
    args, extra = parser.parse_known_args()

    candles = load_candles(args.symbol, args.timeframe)

    print("============================================================")
    print("STAGE TESTES")
    print("============================================================")
    print(f"DATA/HORA      : {datetime.now().isoformat()}")
    print(f"SYMBOL         : {normalize_symbol(args.symbol)}")
    print(f"TIMEFRAME      : {args.timeframe}")
    print(f"STRATEGY       : {args.strategy}")
    print(f"EXTRA ARGS     : {extra}")
    print(f"TOTAL CANDLES  : {len(candles)}")

    if not candles:
        print("RESULTADO      : SEM DADOS")
        raise SystemExit(2)

    first = candles[0]
    last = candles[-1]

    print(f"PRIMEIRO       : {first['open_time']}")
    print(f"ÚLTIMO         : {last['open_time']}")
    print("RESULTADO      : RUN EXECUTADO COM SUCESSO")
    print("============================================================")


if __name__ == "__main__":
    main()