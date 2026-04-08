import sqlite3
from pathlib import Path


DB_PATH = Path("market_research_lab.db")


def print_title(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main() -> None:
    print_title("VALIDAÇÃO DA BASE")
    print(f"DB_PATH={DB_PATH.resolve()}")
    print(f"EXISTS={DB_PATH.exists()}")
    if DB_PATH.exists():
        print(f"SIZE_BYTES={DB_PATH.stat().st_size}")
    else:
        print("A base não existe.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        print_title("TABELAS")
        tables = cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        for row in tables:
            print(row[0])

        print_title("CONTAGEM POR SÍMBOLO / TIMEFRAME")
        rows = cur.execute(
            """
            SELECT
                symbol,
                timeframe,
                COUNT(*) AS total,
                MIN(open_time) AS first_open_time,
                MAX(open_time) AS last_open_time
            FROM candles
            GROUP BY symbol, timeframe
            ORDER BY symbol, timeframe
            """
        ).fetchall()

        if not rows:
            print("Nenhum candle encontrado.")
        else:
            for row in rows:
                print(row)

        print_title("EUR/USD 5m")
        row = cur.execute(
            """
            SELECT
                COUNT(*) AS total,
                MIN(open_time) AS first_open_time,
                MAX(open_time) AS last_open_time
            FROM candles
            WHERE symbol = ? AND timeframe = ?
            """,
            ("EUR/USD", "5m"),
        ).fetchone()

        print(row)

        print_title("ÚLTIMOS 10 CANDLES DE EUR/USD 5m")
        rows = cur.execute(
            """
            SELECT
                open_time,
                close_time,
                open,
                high,
                low,
                close,
                source
            FROM candles
            WHERE symbol = ? AND timeframe = ?
            ORDER BY open_time DESC
            LIMIT 10
            """,
            ("EUR/USD", "5m"),
        ).fetchall()

        if not rows:
            print("Nenhum candle encontrado para EUR/USD 5m.")
        else:
            for row in rows:
                print(row)

        print_title("COBERTURA")
        coverage_exists = cur.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table' AND name = 'candle_coverages'
            """
        ).fetchone()[0]

        if coverage_exists:
            rows = cur.execute(
                """
                SELECT
                    symbol,
                    timeframe,
                    covered_from,
                    covered_to,
                    last_synced_at,
                    last_provider
                FROM candle_coverages
                ORDER BY symbol, timeframe
                """
            ).fetchall()

            if not rows:
                print("Sem linhas na tabela candle_coverages.")
            else:
                for row in rows:
                    print(row)
        else:
            print("Tabela candle_coverages não existe.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()