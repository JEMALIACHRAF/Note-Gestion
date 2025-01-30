# main.py
import sys
import os

# Add the root directory of the project to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI
from indexing_service.indexing_service import router as indexing_router
from media_service.media_service import router as media_router
from chat_agent_service.chat_agent_service import router as chat_router



# Create the main FastAPI app
app = FastAPI(
    title="Document Management and Query Application",
    description="A modular FastAPI application for managing documents, handling multimedia, and interactive responses.",
    version="1.0.0",
)
@app.on_event("shutdown")
async def shutdown():
    print("Application is shutting down.")



# Include routers
app.include_router(indexing_router, prefix="/indexing", tags=["Indexing"])
app.include_router(media_router, prefix="/media", tags=["Media"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])


@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'application de gestion et de requêtes de documents!"}
