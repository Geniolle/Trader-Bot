import os
from pathlib import Path

from app.core.settings import get_settings
from app.storage.database import engine

settings = get_settings()

print("CWD:", os.getcwd())
print("SETTINGS.database_url:", settings.database_url)
print("ENGINE.url:", engine.url)

engine_url = str(engine.url)

if engine_url.startswith("sqlite:///"):
    raw_path = engine_url.replace("sqlite:///", "", 1)
    print("SQLITE path bruto:", raw_path)
    print("SQLITE path resolvido:", Path(raw_path).resolve())
else:
    print("Nao e SQLite local")