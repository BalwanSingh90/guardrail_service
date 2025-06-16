# src/app/main.py

from importlib import reload

from dotenv import load_dotenv
from fastapi import FastAPI

import src.app.core.config as config_module
from src.app.core.logging import get_logger
from src.app.routers.aggregator_result import router as aggregation_router
from src.app.routers.scan import router as scan_router

logger = get_logger(__name__)
load_dotenv(override=True)
reload(config_module)
settings = config_module.Settings()

app = FastAPI(
    title="Guardrail Compliance Pipeline",
    version="1.0.0",
    description="A service that checks user prompts/documents against compliance rules"
)




# Include the /scan router
app.include_router(scan_router)
app.include_router(aggregation_router)

@app.get("/", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}
