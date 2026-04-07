from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.logging import get_logger, setup_logging
from app.core.settings import get_settings

setup_logging()

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Application starting")
    logger.info("Environment: %s", settings.app_env)
    logger.info("Timezone: %s", settings.timezone)