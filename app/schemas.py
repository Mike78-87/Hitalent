"""
Pydantic схемы для валидации входящих/исходящих данных.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List

# ---------- Базовые схемы с общими валидаторами ----------
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[int] = None

    @field_validator('name')
    def trim_and_not_empty(cls, v: str) -> str:
        """Удаляем пробелы по краям, проверяем, что не пусто."""
        v = v.strip()
        if not v:
            raise ValueError('Название не может быть пустым')
        return v

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = None

    @field_validator('name')
    def trim_and_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Название не может быть пустым')
        return v

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    hired_at: Optional[date] = None

    @field_validator('full_name', 'position')
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Поле не может быть пустым')
        return v

# ---------- Схемы для ответов ----------
class EmployeeResponse(EmployeeBase):
    id: int
    department_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    employees: List[EmployeeResponse] = []
    children: List['DepartmentResponse'] = []

    class Config:
        from_attributes = True

# Разрешаем рекурсивную ссылку
DepartmentResponse.model_rebuild()
