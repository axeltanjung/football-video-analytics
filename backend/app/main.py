from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, OUTPUT_DIR, UPLOAD_DIR
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.database import engine, Base


app = FastAPI(
    title="Football Video Analytics",
    version="1.0.0",
    description="AI-powered football match analysis platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok"}
