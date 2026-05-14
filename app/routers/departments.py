"""
Эндпоинты для работы с подразделениями.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=schemas.DepartmentResponse)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_department(db, dept)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/{dept_id}", response_model=schemas.DepartmentResponse)
def get_department(
    dept_id: int,
    depth: int = Query(1, ge=1, le=5, description="Глубина вложенности подразделений (1..5)"),
    include_employees: bool = Query(True, description="Включить сотрудников в ответ"),
    db: Session = Depends(get_db)
):
    result = crud.get_department_with_children(db, dept_id, depth, include_employees)
    if result is None:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    return result

@router.patch("/{dept_id}", response_model=schemas.DepartmentResponse)
def update_department(dept_id: int, update: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    try:
        dept = crud.update_department(db, dept_id, update)
        if not dept:
            raise HTTPException(status_code=404, detail="Подразделение не найдено")
        return dept
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{dept_id}", status_code=204)
def delete_department(
    dept_id: int,
    mode: str = Query(..., regex="^(cascade|reassign)$"),
    reassign_to_department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    if mode == "reassign" and reassign_to_department_id is None:
        raise HTTPException(status_code=400, detail="Параметр reassign_to_department_id обязателен при mode=reassign")
    try:
        success = crud.delete_department(db, dept_id, mode, reassign_to_department_id)
        if not success:
            raise HTTPException(status_code=404, detail="Подразделение не найдено")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
