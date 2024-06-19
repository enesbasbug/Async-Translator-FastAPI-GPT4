from fastapi import FastAPI, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_session, init_db
from app.models import TranslationTask
from app.schemas import TranslationRequest
from app.tasks import start_translation_task
from uuid import uuid4
import asyncio
from app.loging_config import setup_logging

# Set up logging configuration
setup_logging()

# Initialize FastAPI application
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    """
    Event handler for the startup event.
    This will initialize the database schema when the application starts.
    """
    await init_db()

@app.post("/api/v1/translate")
async def translate(request: TranslationRequest, session: AsyncSession = Depends(get_session)):
    """
    Endpoint to start a new translation task.
    
    Args:
        request (TranslationRequest): The translation request containing text and target languages.
        session (AsyncSession): Database session dependency.
    
    Returns:
        dict: Contains the task ID of the created translation task.
    """
    # Generate a unique task ID - random unique ids are used for task tracking
    task_id = str(uuid4())
    # Create a new translation task instance
    task = TranslationTask(id=task_id, text=request.text, status="in_progress")
    # Set the target languages for the task
    task.set_languages(request.languages)
    # Add the task instance to the database session
    session.add(task)
    # Commit the session to save the task in the database
    await session.commit()
    # Refresh the task instance to get the updated state
    await session.refresh(task)
    # Start the translation task asynchronously
    asyncio.create_task(start_translation_task(task_id, request.text, request.languages))
    # Return the task ID to the client
    return {"task_id": task_id}

@app.get("/api/v1/translate/{task_id}")
async def get_translation_status(task_id: str, session: AsyncSession = Depends(get_session)):
    """
    Endpoint to get the status and result of a translation task.
    
    Args:
        task_id (str): The ID of the translation task.
        session (AsyncSession): Database session dependency.
    
    Returns:
        dict: Contains the task status and translations if the task is completed.
    
    Raises:
        HTTPException: If the task is not found.
    """
    # Retrieve the translation task from the database
    task = await session.get(TranslationTask, task_id)
    # If the task is not found, raise a 404 exception
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # If the task is completed, return the translations
    if task.status == "completed":
        return {
            "task_id": task_id,
            "status": task.status,
            "translations": task.get_translations()
        }
    # Otherwise, return the task status
    return {"task_id": task_id, "status": task.status}
