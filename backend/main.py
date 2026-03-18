from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.campaigns import router as campaigns_router
from api.content import router as content_router
from api.images import router as images_router
from api.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AI Marketing System",
    description="AI-powered marketing automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(content_router)
app.include_router(images_router)
app.include_router(analytics_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-marketing-system"}
