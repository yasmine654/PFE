# app/api/conflicts.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.conflict_detection.engine import detect_all_conflicts

router = APIRouter()

@router.get("/conflicts")
def get_conflicts(db: Session = Depends(get_db)):
    return detect_all_conflicts(db)