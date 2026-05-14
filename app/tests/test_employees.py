"""
Тесты для эндпоинтов сотрудников.
"""

def test_create_employee(client, db):
    """Создание сотрудника в существующем подразделении"""
    # Сначала создаём подразделение
    dept = client.post("/departments/", json={"name": "Sales"}).json()
    # Теперь создаём сотрудника
    response = client.post(f"/departments/{dept['id']}/employees/", json={
        "full_name": "Alice Smith",
        "position": "Sales Lead",
        "hired_at": "2023-01-15"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Alice Smith"
    assert data["position"] == "Sales Lead"
    assert data["department_id"] == dept["id"]

def test_create_employee_nonexistent_department(client, db):
    """Ошибка при создании сотрудника в несуществующем подразделении"""
    response = client.post("/departments/999/employees/", json={
        "full_name": "Bob",
        "position": "Tester"
    })
    assert response.status_code == 404

def test_create_employee_invalid_data(client, db):
    """Ошибка при пустых полях сотрудника"""
    dept = client.post("/departments/", json={"name": "R&D"}).json()
    response = client.post(f"/departments/{dept['id']}/employees/", json={
        "full_name": "",
        "position": "Engineer"
    })
    assert response.status_code == 422  # Validation error
