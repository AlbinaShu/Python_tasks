import pytest
from fastapi.testclient import TestClient
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

class TestAuthEndpoints:
    """Тесты для эндпоинтов аутентификации"""
    
    def test_register_user_success(self, test_client: TestClient):
        """Тест успешной регистрации нового пользователя"""
        user_data = {
            "username": "testuser_new",
            "password": "testpass123"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == user_data["username"]
        assert "password" not in data

    def test_register_user_duplicate(self, test_client: TestClient):
        """Тест регистрации с существующим именем пользователя"""
        user_data = {
            "username": "testuser_duplicate",
            "password": "testpass123"
        }
        
        # Первая регистрация - должна быть успешной
        response1 = test_client.post("/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Вторая регистрация с тем же именем - должна вернуть ошибку
        response2 = test_client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "уже существует" in response2.json()["detail"]

    def test_login_user_success(self, test_client: TestClient):
        """Тест успешного входа пользователя"""
        # Сначала регистрируем пользователя
        user_data = {
            "username": "login_test_user",
            "password": "loginpass123"
        }
        test_client.post("/auth/register", json=user_data)
        
        # Пытаемся войти
        response = test_client.post("/auth/login", data={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert data["username"] == user_data["username"]
        assert "user_id" in data
        assert data["message"] == "Успешный вход в систему"

    def test_login_user_invalid_credentials(self, test_client: TestClient):
        """Тест входа с неверными учетными данными"""
        response = test_client.post("/auth/login", data={
            "username": "nonexistent_user",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Неверное имя пользователя или пароль" in response.json()["detail"]

    def test_create_student_authenticated(self, test_client: TestClient):
        """Тест создания студента с аутентификацией"""
        # Регистрируем и логиним пользователя
        user_data = {"username": "student_creator", "password": "pass123"}
        test_client.post("/auth/register", json=user_data)
        
        login_response = test_client.post("/auth/login", data=user_data)
        session_token = login_response.json()["session_token"]
        
        # Создаем студента с токеном сессии
        student_data = {
            "last_name": "Иванов",
            "first_name": "Петр",
            "faculty": "ФТФ",
            "course": "Физика",
            "grade": 85.5
        }
        
        response = test_client.post(
            "/students/",
            json=student_data,
            headers={"Authorization": f"Bearer {session_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["last_name"] == student_data["last_name"]
        assert data["first_name"] == student_data["first_name"]
        assert data["faculty"] == student_data["faculty"]
        assert data["grade"] == student_data["grade"]

    def test_create_student_unauthenticated(self, test_client: TestClient):
        """Тест создания студента без аутентификации"""
        student_data = {
            "last_name": "Петров",
            "first_name": "Иван",
            "faculty": "ФПМИ",
            "course": "Мат. Анализ",
            "grade": 90.0
        }
        
        response = test_client.post("/students/", json=student_data)
        
        assert response.status_code == 401
        assert "Недействительная сессия" in response.json()["detail"]

    def test_get_students_authenticated(self, test_client: TestClient):
        """Тест получения списка студентов с аутентификацией"""
        # Регистрируем и логиним пользователя
        user_data = {"username": "student_viewer", "password": "viewpass123"}
        test_client.post("/auth/register", json=user_data)
        
        login_response = test_client.post("/auth/login", data=user_data)
        session_token = login_response.json()["session_token"]
        
        # Получаем список студентов
        response = test_client.get(
            "/students/",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_students_unauthenticated(self, test_client: TestClient):
        """Тест получения списка студентов без аутентификации"""
        response = test_client.get("/students/")
        
        assert response.status_code == 401
        assert "Недействительная сессия" in response.json()["detail"]

    def test_logout_user_success(self, test_client: TestClient):
        """Тест успешного выхода пользователя"""
        # Регистрируем и логиним пользователя
        user_data = {"username": "logout_test_user", "password": "logoutpass123"}
        test_client.post("/auth/register", json=user_data)
        
        login_response = test_client.post("/auth/login", data=user_data)
        session_token = login_response.json()["session_token"]
        
        # Выходим из системы
        response = test_client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Успешный выход из системы"

    def test_logout_user_invalid_token(self, test_client: TestClient):
        """Тест выхода с недействительным токеном"""
        response = test_client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        assert response.status_code == 401
        assert "Недействительная сессия" in response.json()["detail"]