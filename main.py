from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

# --- Component Imports ---
# Import all the components we have built
from database import get_db
import models
import schemas
# Import the new task function that will run in the background
from tasks import process_and_save_papers


# --- FastAPI App Instance ---
# Create the FastAPI app instance with metadata
app = FastAPI(
    title="LLM Research Paper Digest API",
    description="An API to fetch and process LLM-related research papers from arXiv.",
    version="0.1.0",
)


# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    A welcome endpoint for the API.
    """
    return {"message": "Welcome to the LLM Research Paper Digest API!"}


@app.get("/api/papers", response_model=List[schemas.Paper])
def get_all_papers(db: Session = Depends(get_db)):
    """
    Retrieves a list of all papers currently stored in the database.
    
    This endpoint demonstrates reading data from the database and returning it
    in a structured format defined by Pydantic schemas.
    """
    papers = db.query(models.Paper).order_by(models.Paper.publish_date.desc()).all()
    return papers


# --- NEW ENDPOINT TO TRIGGER BACKGROUND TASK ---
@app.post("/api/papers/trigger-processing", status_code=202)
def trigger_daily_processing(background_tasks: BackgroundTasks):
    """
    Triggers the background task to fetch and process papers for yesterday.
    
    This endpoint immediately returns a 202 "Accepted" response while the 
    actual processing happens in the background.
    """
    # Calculate yesterday's date in UTC, which is what arXiv uses.
    """ yesterday_utc = datetime.now() - timedelta(days=1)
    date_str_for_task = yesterday_utc.strftime('%Y%m%d') """

    date_str_for_task = "20250626" 
    
    # Add the long-running function to be executed in the background
    background_tasks.add_task(process_and_save_papers, date_str_for_task)
    
    return {
        "message": "Processing task for yesterday's papers has been triggered.", 
        "processing_date": date_str_for_task
    }