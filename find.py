# G:\O meu disco\python\Trader-bot\find_usage.py
from pathlib import Path

ROOT = Path(r"G:\O meu disco\python\Trader-bot")
PATTERNS = [
    "build_candlestick_intelligence(",
    "entry_location",
]

for file_path in ROOT.rglob("*.py"):
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        continue

    lines = content.splitlines()
    matched = False

    for line_number, line in enumerate(lines, start=1):
        if any(pattern in line for pattern in PATTERNS):
            if not matched:
                print(f"\nFILE: {file_path}")
                matched = True
            print(f"  {line_number}: {line.strip()}")