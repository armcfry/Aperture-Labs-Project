"""
Aperture Labs API - Main Application Entry Point
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.detection import router

app = FastAPI(
    title="Aperture Labs API",
) 

# Configure CORS middleware: This allows the frontend to make requests to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Adds all the API endpoints from routers folder
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Aperture Labs Defect Detection API",
        "docs": "/docs", # Swagger docs
    }
