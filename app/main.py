"""
Точка входа FastAPI.
"""
from fastapi import FastAPI
from app.routers import departments, employees

app = FastAPI(title="API организационной структуры", version="1.0")

app.include_router(departments.router)
app.include_router(employees.router)
