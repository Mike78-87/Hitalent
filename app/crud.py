"""
CRUD операции с проверками бизнес-логики и уникальности.
"""
from sqlalchemy.orm import Session
from app import models, schemas
from typing import Optional, List

def get_department(db: Session, dept_id: int) -> Optional[models.Department]:
    """Вернуть подразделение по id или None."""
    return db.query(models.Department).filter(models.Department.id == dept_id).first()

def get_department_with_children(db: Session, dept_id: int, depth: int, include_employees: bool):
    """
    Рекурсивно собирает дерево подразделений до заданной глубины.
    depth: максимальная глубина вложенности.
    include_employees: включать ли сотрудников в ответ.
    """
    def _load_children(dept: models.Department, current_depth: int):
        if current_depth > depth:
            return []
        children = []
        for child in dept.children:
            child_data = {
                "id": child.id,
                "name": child.name,
                "parent_id": child.parent_id,
                "created_at": child.created_at,
                "employees": [e.__dict__ for e in child.employees] if include_employees else [],
                "children": _load_children(child, current_depth + 1)
            }
            children.append(child_data)
        return children

    dept = get_department(db, dept_id)
    if not dept:
        return None
    result = {
        "id": dept.id,
        "name": dept.name,
        "parent_id": dept.parent_id,
        "created_at": dept.created_at,
        "employees": [e.__dict__ for e in dept.employees] if include_employees else [],
        "children": _load_children(dept, 1)
    }
    return result

def create_department(db: Session, dept: schemas.DepartmentCreate):
    """Создать подразделение с проверкой уникальности имени внутри одного parent."""
    parent_id = dept.parent_id
    existing = db.query(models.Department).filter(
        models.Department.parent_id == parent_id,
        models.Department.name == dept.name
    ).first()
    if existing:
        raise ValueError(f"Подразделение с именем '{dept.name}' уже существует на уровне parent={parent_id}")
    db_dept = models.Department(name=dept.name, parent_id=dept.parent_id)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

def update_department(db: Session, dept_id: int, update: schemas.DepartmentUpdate):
    """Обновить название или родителя, проверяя циклы и уникальность имени."""
    dept = get_department(db, dept_id)
    if not dept:
        return None

    # Обновление имени
    if update.name is not None:
        existing = db.query(models.Department).filter(
            models.Department.parent_id == dept.parent_id,
            models.Department.name == update.name,
            models.Department.id != dept_id
        ).first()
        if existing:
            raise ValueError(f"Подразделение с именем '{update.name}' уже существует на уровне parent={dept.parent_id}")
        dept.name = update.name

    # Обновление родителя
    if update.parent_id is not None:
        if update.parent_id == dept_id:
            raise ValueError("Нельзя сделать подразделение родителем самого себя")
        # Проверка цикла: новый родитель не должен быть потомком текущего подразделения
        parent = get_department(db, update.parent_id)
        if parent:
            def is_descendant(p: models.Department, target_id: int) -> bool:
                while p:
                    if p.id == target_id:
                        return True
                    p = p.parent
                return False
            if is_descendant(parent, dept_id):
                raise ValueError("Нельзя переместить подразделение внутрь своего же поддерева")
        dept.parent_id = update.parent_id

    db.commit()
    db.refresh(dept)
    return dept

def delete_department(db: Session, dept_id: int, mode: str, reassign_to: Optional[int] = None):
    """
    Удаление подразделения.
    mode = 'cascade' — удалить всё дерево.
    mode = 'reassign' — перевести сотрудников и дочерние подразделения в reassign_to.
    """
    dept = get_department(db, dept_id)
    if not dept:
        return False

    if mode == "cascade":
        db.delete(dept)
        db.commit()
        return True

    elif mode == "reassign":
        if reassign_to is None:
            raise ValueError("Для mode=reassign необходимо указать reassign_to_department_id")
        target = get_department(db, reassign_to)
        if not target:
            raise ValueError("Целевое подразделение не найдено")
        # Переназначить сотрудников
        db.query(models.Employee).filter(models.Employee.department_id == dept_id).update(
            {models.Employee.department_id: reassign_to}
        )
        # Переназначить дочерние подразделения
        db.query(models.Department).filter(models.Department.parent_id == dept_id).update(
            {models.Department.parent_id: reassign_to}
        )
        db.delete(dept)
        db.commit()
        return True
    else:
        raise ValueError("Неверный mode. Допустимо: cascade, reassign")

def create_employee(db: Session, dept_id: int, emp: schemas.EmployeeCreate):
    """Создать сотрудника в указанном подразделении, проверив его существование."""
    dept = get_department(db, dept_id)
    if not dept:
        return None
    db_emp = models.Employee(
        department_id=dept_id,
        full_name=emp.full_name,
        position=emp.position,
        hired_at=emp.hired_at
    )
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp
