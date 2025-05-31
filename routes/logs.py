from models import LogAcesso
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar_logs(db: Session = Depends(get_db)):
    return db.query(LogAcesso).all()
