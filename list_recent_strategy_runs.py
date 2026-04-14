import sqlite3

db = r"G:\O meu disco\python\Trader-bot\market_research_lab.db"
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute("""
SELECT
    id,
    strategy_key,
    symbol,
    timeframe,
    start_at,
    end_at,
    status,
    started_at,
    finished_at
FROM strategy_runs
WHERE symbol = ?
  AND timeframe = ?
ORDER BY started_at DESC
LIMIT 20
""", ("EUR/USD", "5m"))

rows = cur.fetchall()

if not rows:
    print("SEM_ROWS")
else:
    for row in rows:
        print(row)

con.close()
