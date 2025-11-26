from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from db_manager import StudentDataManager
from models import User as UserModel, Student
import secrets
import asyncio
from typing import Dict, Any, List
import uuid
import logging
import os
import time
import redis  # Добавляем Redis

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(title="Student Management API", version="1.0.0")

# URL базы данных
DATABASE_URL = "sqlite:///./students.db"

# Redis конфигурация
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# Создаём менеджер БД
db_manager = StudentDataManager(DATABASE_URL)

# Инициализация Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Настройка базовой аутентификации
security = HTTPBasic()

# Pydantic-модели для валидации
class StudentCreate(BaseModel):
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: float

class StudentResponse(BaseModel):
    id: int
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: float

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class CSVImportRequest(BaseModel):
    csv_file_path: str

class DeleteStudentsRequest(BaseModel):
    student_ids: List[int]

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    message: str
    processed_count: int = 0

# Dependency для передачи менеджера в маршруты
def get_db():
    return db_manager

# Dependency для Redis
def get_redis():
    return redis_client

# Хранилище активных сессий и статусов задач
active_sessions: Dict[str, Dict[str, Any]] = {}
background_tasks: Dict[str, Dict[str, Any]] = {}

# Функция для аутентификации пользователя по сессионному токену
def authenticate_by_token(token: str) -> UserModel:
    """Аутентификация по сессионному токену"""
    if token in active_sessions:
        user_data = active_sessions[token]
        user = db_manager.get_user_by_id(user_data["user_id"])
        if user:
            return user
    return None

# Основная функция аутентификации
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: StudentDataManager = Depends(get_db)):
    try:
        logger.info(f"Аутентификация для: {credentials.username}")
        
        # Сначала пробуем аутентифицировать по сессионному токену
        user = authenticate_by_token(credentials.username)
        if user:
            logger.info("Аутентификация по сессионному токену успешна")
            return user
        
        # Если не сработало, пробуем по логину/паролю
        user = db.get_user_by_username(credentials.username)
        if not user:
            logger.warning("Пользователь не найден")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
            )
        
        if user.password != credentials.password:
            logger.warning("Неверный пароль")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
            )
            
        logger.info("Аутентификация по логину/паролю успешна")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при аутентификации"
        )

# Функция для инвалидации кеша
def invalidate_students_cache():
    """Удаляет все кешированные данные о студентах"""
    try:
        keys = redis_client.keys("students:*")
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Инвалидирован кеш: {len(keys)} ключей")
    except Exception as e:
        logger.error(f"Ошибка при инвалидации кеша: {e}")

# Фоновые задачи
async def load_csv_background(task_id: str, csv_file_path: str, db: StudentDataManager):
    try:
        background_tasks[task_id] = {
            "status": "running", 
            "message": "Начата загрузка данных из CSV файла",
            "processed_count": 0,
            "started_at": time.time()
        }
        
        logger.info(f"Фоновая задача {task_id}: начало загрузки из {csv_file_path}")
        
        # Загрузка данных из CSV
        processed_count = db.load_from_csv(csv_file_path)
        
        # Инвалидируем кеш после загрузки
        invalidate_students_cache()
        
        background_tasks[task_id] = {
            "status": "completed", 
            "message": f"Успешно загружено {processed_count} записей из CSV файла",
            "processed_count": processed_count,
            "completed_at": time.time()
        }
        
        logger.info(f"Фоновая задача {task_id}: завершена, загружено {processed_count} записей")
        
    except FileNotFoundError:
        error_msg = f"Файл {csv_file_path} не найден"
        logger.error(error_msg)
        background_tasks[task_id] = {
            "status": "error", 
            "message": error_msg,
            "processed_count": 0,
            "error_at": time.time()
        }
    except Exception as e:
        error_msg = f"Ошибка при загрузке CSV: {str(e)}"
        logger.error(error_msg)
        background_tasks[task_id] = {
            "status": "error", 
            "message": error_msg,
            "processed_count": 0,
            "error_at": time.time()
        }

async def delete_students_background(task_id: str, student_ids: List[int], db: StudentDataManager):
    try:
        background_tasks[task_id] = {
            "status": "running", 
            "message": "Начато удаление студентов",
            "processed_count": 0,
            "started_at": time.time()
        }
        
        logger.info(f"Фоновая задача {task_id}: удаление {len(student_ids)} студентов")
        
        # Удаляем студентов
        deleted_count = db.delete_students_by_ids(student_ids)
        
        # Инвалидируем кеш после удаления
        invalidate_students_cache()
        
        background_tasks[task_id] = {
            "status": "completed", 
            "message": f"Успешно удалено {deleted_count} записей",
            "processed_count": deleted_count,
            "completed_at": time.time()
        }
        
        logger.info(f"Фоновая задача {task_id}: завершена, удалено {deleted_count} записей")
        
    except Exception as e:
        error_msg = f"Ошибка при удалении студентов: {str(e)}"
        logger.error(error_msg)
        background_tasks[task_id] = {
            "status": "error", 
            "message": error_msg,
            "processed_count": 0,
            "error_at": time.time()
        }

# Эндпоинты аутентификации
@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate, db: StudentDataManager = Depends(get_db)):
    try:
        logger.info(f"Регистрация пользователя: {user.username}")
        
        # Создаем нового пользователя
        new_user = db.create_user(user.username, user.password)
        
        if not new_user:
            logger.warning("Пользователь уже существует")
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
        
        logger.info(f"Пользователь создан: {new_user.id}")
        return UserResponse(id=new_user.id, username=new_user.username)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при регистрации: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.post("/auth/login")
def login_user(user: UserModel = Depends(authenticate_user)):
    try:
        # Создаем сессионный токен
        session_token = secrets.token_urlsafe(32)
        
        # Сохраняем информацию о сессии
        active_sessions[session_token] = {
            "user_id": user.id,
            "username": user.username,
            "created_at": time.time()
        }
        
        logger.info(f"Успешный вход, создана сессия: {session_token}")
        
        return {
            "message": "Успешный вход в систему",
            "session_token": session_token,
            "user_id": user.id,
            "username": user.username
        }
    except Exception as e:
        logger.error(f"Ошибка при входе: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/logout")
def logout_user(credentials: HTTPBasicCredentials = Depends(security)):
    session_token = credentials.username
    if session_token in active_sessions:
        del active_sessions[session_token]
        logger.info(f"Пользователь вышел из системы: {session_token}")
        return {"message": "Успешный выход из системы"}
    else:
        raise HTTPException(status_code=400, detail="Сессия не найдена")

# Эндпоинт для фоновой загрузки CSV
@app.post("/admin/load-csv", response_model=TaskStatusResponse)
async def load_csv_from_file(
    request: CSVImportRequest,
    background_tasks_module: BackgroundTasks,
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(authenticate_user)
):
    try:
        # Проверяем существование файла перед запуском задачи
        if not os.path.exists(request.csv_file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Файл {request.csv_file_path} не найден"
            )
        
        task_id = str(uuid.uuid4())
        
        logger.info(f"Запуск фоновой задачи загрузки CSV: {request.csv_file_path} пользователем {current_user.username}")
        
        # Запускаем фоновую задачу
        background_tasks_module.add_task(load_csv_background, task_id, request.csv_file_path, db)
        
        return TaskStatusResponse(
            task_id=task_id,
            status="started",
            message=f"Задача загрузки CSV запущена. ID задачи: {task_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинт для фонового удаления студентов
@app.post("/admin/delete-students", response_model=TaskStatusResponse)
async def delete_students(
    request: DeleteStudentsRequest,
    background_tasks_module: BackgroundTasks,
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(authenticate_user)
):
    try:
        if not request.student_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Список ID студентов не может быть пустым"
            )
        
        task_id = str(uuid.uuid4())
        
        logger.info(f"Запуск фоновой задачи удаления {len(request.student_ids)} студентов пользователем {current_user.username}")
        
        # Запускаем фоновую задачу
        background_tasks_module.add_task(delete_students_background, task_id, request.student_ids, db)
        
        return TaskStatusResponse(
            task_id=task_id,
            status="started",
            message=f"Задача удаления студентов запущена. ID задачи: {task_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи удаления: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинт для проверки статуса задачи
@app.get("/admin/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    current_user: UserModel = Depends(authenticate_user)
):
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return TaskStatusResponse(**background_tasks[task_id])

# Защищенные CRUD-эндпоинты с кешированием
@app.post("/students/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate, 
    db: StudentDataManager = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: UserModel = Depends(authenticate_user)
):
    try:
        new_student = Student(
            last_name=student.last_name,
            first_name=student.first_name,
            faculty=student.faculty,
            course=student.course,
            grade=student.grade
        )
        created_student = db.insert_student(new_student)
        
        # Инвалидируем кеш после создания нового студента
        invalidate_students_cache()
        
        return StudentResponse(
            id=created_student.id,
            last_name=created_student.last_name,
            first_name=created_student.first_name,
            faculty=created_student.faculty,
            course=created_student.course,
            grade=created_student.grade
        )
    except Exception as e:
        logger.error(f"Ошибка при создании студента: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/", response_model=list[StudentResponse])
def read_students(
    db: StudentDataManager = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: UserModel = Depends(authenticate_user)
):
    cache_key = "students:all"
    
    try:
        # Пробуем получить данные из кеша
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info("Данные получены из кеша")
            # Здесь нужно реализовать десериализацию, например, используя json.loads
            # Для простоты пока пропустим и всегда будем получать из БД
            pass
    except Exception as e:
        logger.error(f"Ошибка при работе с Redis: {e}")
    
    # Получаем данные из БД
    students = db.select_all_students()
    result = [
        StudentResponse(
            id=student.id,
            last_name=student.last_name,
            first_name=student.first_name,
            faculty=student.faculty,
            course=student.course,
            grade=student.grade
        )
        for student in students
    ]
    
    try:
        # Сохраняем в кеш на 5 минут
        # Здесь нужно реализовать сериализацию, например, используя json.dumps
        # redis_client.setex(cache_key, 300, serialized_data)
        pass
    except Exception as e:
        logger.error(f"Ошибка при сохранении в кеш: {e}")
    
    return result

@app.get("/students/{student_id}", response_model=StudentResponse)
def read_student(
    student_id: int, 
    db: StudentDataManager = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: UserModel = Depends(authenticate_user)
):
    cache_key = f"students:{student_id}"
    
    # Здесь также можно добавить логику кеширования для отдельного студента
    
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return StudentResponse(
        id=student.id,
        last_name=student.last_name,
        first_name=student.first_name,
        faculty=student.faculty,
        course=student.course,
        grade=student.grade
    )

# Корневой эндпоинт
@app.get("/")
def read_root():
    return {"message": "Student Management API работает! Перейдите на /docs для тестирования API"}

@app.get("/auth/check")
def check_auth(current_user: UserModel = Depends(authenticate_user)):
    return {
        "message": "Аутентификация успешна",
        "user_id": current_user.id,
        "username": current_user.username
    }

# Эндпоинт для отладки - показывает активные сессии
@app.get("/auth/debug-sessions")
def debug_sessions(current_user: UserModel = Depends(authenticate_user)):
    return {
        "active_sessions": active_sessions,
        "current_user": {
            "id": current_user.id,
            "username": current_user.username
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)