import sqlite3

db = r"G:\O meu disco\python\Trader-bot\market_research_lab.db"
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute("""
SELECT
    id,
    symbol,
    timeframe,
    trigger_time,
    trigger_candle_time,
    entry_time,
    close_time,
    outcome,
    status
FROM strategy_cases
WHERE symbol = ?
  AND timeframe = ?
  AND date(trigger_time) = ?
ORDER BY trigger_time ASC
""", ("EUR/USD", "5m", "2026-04-03"))

rows = cur.fetchall()

if not rows:
    print("SEM_ROWS")
else:
    for row in rows:
        print(row)

con.close()
