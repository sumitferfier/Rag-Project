from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.rag import router as rag_router

from app.auth.database import Base, engine
from app.auth import models
from app.auth.auth_router import router as auth_router


# Create database tables
Base.metadata.create_all(
    bind=engine
)

# Create FastAPI application
app = FastAPI(
    title="RAG API"
)

# CORS
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:4200"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication routes
app.include_router(
    auth_router
)

# RAG routes
app.include_router(
    rag_router
)

# Root endpoint
@app.get("/")
def root():

    return {"message": "PDF RAG API is running"}