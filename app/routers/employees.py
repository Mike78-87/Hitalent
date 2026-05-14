"""
Эндпоинты для создания сотрудников.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/departments", tags=["employees"])

@router.post("/{dept_id}/employees/", response_model=schemas.EmployeeResponse)
def create_employee(dept_id: int, emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = crud.create_employee(db, dept_id, emp)
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    return db_emp
