from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, products, users
from app.core.config import settings
from app.db.database import Base, engine
from app import models
from app.services.user_service import EmailJaCadastradoError 
from app.api.exception_handlers import register_exception_handlers

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="API do marketplace de desapego: autenticação JWT e CRUD de anúncios.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)


register_exception_handlers(app)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ola", tags=["ola"])
def say_ola() -> dict[str, str]:
    return {"mensagem": "Olá, sou a Desapego API!"}