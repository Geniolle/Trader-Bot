import sqlite3

db = r"G:\O meu disco\python\Trader-bot\market_research_lab.db"
con = sqlite3.connect(db)
cur = con.cursor()

cur.execute("""
SELECT
    symbol,
    timeframe,
    COUNT(*) AS total,
    MIN(open_time),
    MAX(open_time)
FROM candles
WHERE UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) = ?
  AND timeframe = ?
GROUP BY symbol, timeframe
ORDER BY symbol
""", ("EURUSD", "5m"))

rows = cur.fetchall()

if not rows:
    print("SEM_ROWS")
else:
    for row in rows:
        print(row)

con.close()
