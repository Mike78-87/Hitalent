"""
SQLAlchemy модели: Department (подразделение) и Employee (сотрудник).
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)                 # название, не пустое
    parent_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Связи: родитель, дети, сотрудники
    parent = relationship("Department", remote_side=[id], backref="children", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    hired_at = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    department = relationship("Department", back_populates="employees")
