from sqlalchemy.orm import Session
from typing import List, Optional  # <--- 1. 导入 Optional

import models
import schemas

# --- Institution CRUD Functions ---

# 2. 使用 Optional[models.Institution] 代替 models.Institution | None
def get_institution_by_name(db: Session, name: str) -> Optional[models.Institution]:
    """
    Retrieves an institution from the database by its exact name.
    """
    return db.query(models.Institution).filter(models.Institution.name == name).first()

def create_institution(db: Session, institution: schemas.InstitutionBase) -> models.Institution:
    """
    Creates a new institution in the database.
    """
    db_institution = models.Institution(name=institution.name)
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    return db_institution

def get_or_create_institution(db: Session, name: str) -> models.Institution:
    """
    A helper function to either get an existing institution by name or create a new one.
    This prevents creating duplicate institutions.
    """
    db_institution = get_institution_by_name(db, name=name)
    if not db_institution:
        institution_schema = schemas.InstitutionBase(name=name)
        db_institution = create_institution(db, institution=institution_schema)
    return db_institution


# --- Paper CRUD Functions ---

# 3. 同样，在这里也使用 Optional
def get_paper_by_arxiv_id(db: Session, arxiv_id: str) -> Optional[models.Paper]:
    """
    Retrieves a paper from the database by its unique arXiv ID.
    """
    return db.query(models.Paper).filter(models.Paper.arxiv_id == arxiv_id).first()

def create_paper(db: Session, paper: schemas.PaperBase, institution_names: List[str]) -> models.Paper:
    """
    Creates a new paper in the database and associates it with given institutions.
    """
    db_paper_exists = get_paper_by_arxiv_id(db, arxiv_id=paper.arxiv_id)
    if db_paper_exists:
        return db_paper_exists

    db_paper = models.Paper(**paper.model_dump())

    for inst_name in institution_names:
        institution_obj = get_or_create_institution(db, name=inst_name)
        db_paper.institutions.append(institution_obj)

    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper