import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Настройка тестового окружения"""
    # Используем тестовую базу данных
    test_db_url = "sqlite:///./test_students.db"
    os.environ["DATABASE_URL"] = test_db_url
    
    # Создаем тестовые таблицы
    engine = create_engine(test_db_url)
    Base.metadata.drop_all(bind=engine)  # Очищаем перед тестами
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Очистка после тестов
    if os.path.exists("./test_students.db"):
        os.remove("./test_students.db")

@pytest.fixture
def test_client():
    """Фикстура для тестового клиента"""
    from main import app
    from fastapi.testclient import TestClient
    
    # Временно меняем URL базы данных для тестов
    original_db_url = app.extra.get("original_db_url")
    if not original_db_url:
        from main import DATABASE_URL
        app.extra["original_db_url"] = DATABASE_URL
    
    return TestClient(app)