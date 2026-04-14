import sqlite3

db = r"G:\O meu disco\python\Trader-bot\market_research_lab.db"
con = sqlite3.connect(db)
cur = con.cursor()

print("PRIMEIROS:")
cur.execute("""
SELECT
    symbol,
    open_time,
    close_time,
    open,
    high,
    low,
    close
FROM candles
WHERE UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) = ?
  AND timeframe = ?
ORDER BY open_time ASC
LIMIT 15
""", ("EURUSD", "5m"))

for row in cur.fetchall():
    print(row)

print()
print("ULTIMOS:")
cur.execute("""
SELECT
    symbol,
    open_time,
    close_time,
    open,
    high,
    low,
    close
FROM candles
WHERE UPPER(REPLACE(REPLACE(REPLACE(REPLACE(symbol, '/', ''), '-', ''), '_', ''), ' ', '')) = ?
  AND timeframe = ?
ORDER BY open_time DESC
LIMIT 15
""", ("EURUSD", "5m"))

for row in cur.fetchall():
    print(row)

con.close()
