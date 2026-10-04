from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Evidence-backed AI assistant for SRE incident investigation.",
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
