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
WHERE symbol = ?
  AND timeframe = ?
GROUP BY symbol, timeframe
""", ("EUR/USD", "5m"))

for row in cur.fetchall():
    print(row)

print()
cur.execute("""
SELECT
    date(open_time) AS dia,
    COUNT(*) AS total
FROM candles
WHERE symbol = ?
  AND timeframe = ?
GROUP BY date(open_time)
ORDER BY dia
""", ("EUR/USD", "5m"))

for row in cur.fetchall():
    print(row)

con.close()
