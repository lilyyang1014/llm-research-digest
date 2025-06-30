# schemas.py (修改后)

from pydantic import BaseModel
from datetime import date
from typing import List, Optional 

# --- Schema for creating/representing an Institution ---
class InstitutionBase(BaseModel):
    name: str

class Institution(InstitutionBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Schema for creating/representing a Paper ---
class PaperBase(BaseModel):
    arxiv_id: str
    title: str
    abstract: Optional[str] = None 
    publish_date: Optional[date] = None
    llm_summary: Optional[str] = None

class Paper(PaperBase):
    id: int
    institutions: List[Institution] = []

    class Config:
        from_attributes = True