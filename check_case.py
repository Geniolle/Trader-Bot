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
    close_time
FROM strategy_cases
WHERE id = ?
""", ("case-1",))

rows = cur.fetchall()

for row in rows:
    print(row)

con.close()
