from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import contracts, generate, health

app = FastAPI(
    title="API Contract Generator",
    description=(
        "AI-powered service that generates OpenAPI 3.1.0 contracts and Markdown documentation "
        "from a live API endpoint or a source code repository."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(generate.router, prefix="/api/v1")
app.include_router(contracts.router, prefix="/api/v1")
