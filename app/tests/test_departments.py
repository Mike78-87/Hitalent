"""
Тесты для эндпоинтов подразделений.
"""
from app.main import app

def test_create_department(client, db):
    """Создание подразделения"""
    response = client.post("/departments/", json={"name": "IT", "parent_id": None})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "IT"
    assert data["id"] is not None

def test_create_duplicate_name_same_parent(client, db):
    """Запрет на дубликат имени внутри одного родителя"""
    client.post("/departments/", json={"name": "HR", "parent_id": None})
    response = client.post("/departments/", json={"name": "HR", "parent_id": None})
    assert response.status_code == 409

def test_get_department_with_children(client, db):
    """Получение дерева подразделений"""
    dept1 = client.post("/departments/", json={"name": "Parent"}).json()
    client.post("/departments/", json={"name": "Child", "parent_id": dept1["id"]}).json()
    response = client.get(f"/departments/{dept1['id']}?depth=2")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Parent"
    assert len(data["children"]) == 1

def test_move_department_cycle(client, db):
    """Запрет на создание цикла в дереве"""
    root = client.post("/departments/", json={"name": "Root"}).json()
    child = client.post("/departments/", json={"name": "Child", "parent_id": root["id"]}).json()
    # Пытаемся переместить root внутрь child (цикл)
    response = client.patch(f"/departments/{root['id']}", json={"parent_id": child["id"]})
    assert response.status_code == 409

def test_delete_cascade(client, db):
    """Каскадное удаление подразделения"""
    dept = client.post("/departments/", json={"name": "ToDelete"}).json()
    client.post(f"/departments/{dept['id']}/employees/", json={"full_name": "John", "position": "Dev"})
    response = client.delete(f"/departments/{dept['id']}?mode=cascade")
    assert response.status_code == 204
    # Проверяем, что подразделение удалено
    get_resp = client.get(f"/departments/{dept['id']}")
    assert get_resp.status_code == 404

def test_delete_reassign(client, db):
    """Удаление с переназначением сотрудников в другое подразделение"""
    dept1 = client.post("/departments/", json={"name": "Old"}).json()
    dept2 = client.post("/departments/", json={"name": "New"}).json()
    client.post(f"/departments/{dept1['id']}/employees/", json={"full_name": "Jane", "position": "Manager"})
    response = client.delete(f"/departments/{dept1['id']}?mode=reassign&reassign_to_department_id={dept2['id']}")
    assert response.status_code == 204
    # Проверяем, что сотрудник переместился
    get_dept2 = client.get(f"/departments/{dept2['id']}?include_employees=true")
    assert get_dept2.status_code == 200
    employees = get_dept2.json()["employees"]
    assert any(e["full_name"] == "Jane" for e in employees)
