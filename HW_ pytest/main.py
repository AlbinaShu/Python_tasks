from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from db_manager import StudentDataManager
from models import User as UserModel  # Переименовываем для избежания конфликта
import secrets

# Инициализация приложения
app = FastAPI()

# URL базы данных
DATABASE_URL = "sqlite:///./students.db"

# Создаём менеджер БД
db_manager = StudentDataManager(DATABASE_URL)

# Настройка базовой аутентификации
security = HTTPBasic()

# Pydantic-модели для валидации
class StudentCreate(BaseModel):
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: float

class StudentUpdate(BaseModel):
    last_name: str = None
    first_name: str = None
    faculty: str = None
    course: str = None
    grade: float = None

class StudentResponse(BaseModel):
    id: int
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: float

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# Dependency для передачи менеджера в маршруты
def get_db():
    return db_manager

# Хранилище активных сессий (в реальном приложении используйте Redis или БД)
active_sessions = {}

# Функция для аутентификации пользователя
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: StudentDataManager = Depends(get_db)):
    user = db.get_user_by_username(credentials.username)
    if not user or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

# Функция для проверки активной сессии
def get_current_user(session_token: str = Depends(security)):
    if session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительная сессия",
        )
    return active_sessions[session_token]

# Эндпоинты аутентификации
@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate, db: StudentDataManager = Depends(get_db)):
    try:
        # Проверяем, существует ли пользователь
        existing_user = db.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
        
        # Создаем нового пользователя
        new_user = db.create_user(user.username, user.password)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
def login_user(user: UserModel = Depends(authenticate_user)):  # Используем переименованную модель
    # Создаем сессионный токен
    session_token = secrets.token_urlsafe(32)
    active_sessions[session_token] = user
    
    return {
        "message": "Успешный вход в систему",
        "session_token": session_token,
        "user_id": user.id,
        "username": user.username
    }

@app.post("/auth/logout")
def logout_user(current_user: UserModel = Depends(get_current_user), session_token: str = Depends(security)):
    if session_token in active_sessions:
        del active_sessions[session_token]
    
    return {"message": "Успешный выход из системы"}

# Защищенные CRUD-эндпоинты

@app.post("/students/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate, 
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    try:
        from models import Student  # Импортируем здесь чтобы избежать циклического импорта
        new_student = Student(**student.dict())
        created_student = db.insert_student(new_student)
        return created_student
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/", response_model=list[StudentResponse])
def read_students(
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    students = db.select_all_students()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
def read_student(
    student_id: int, 
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    updated_student = db.update_student(student_id, **student.dict(exclude_unset=True))
    if not updated_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return updated_student

@app.delete("/students/{student_id}", response_model=dict)
def delete_student(
    student_id: int, 
    db: StudentDataManager = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if db.delete_student(student_id):
        return {"message": "Студент удалён"}
    else:
        raise HTTPException(status_code=404, detail="Студент не найден")

# Дополнительные эндпоинты для удобства тестирования
@app.get("/")
def read_root():
    return {"message": "Сервер работает! Перейдите на /docs для тестирования API"}

@app.get("/auth/check")
def check_auth(current_user: UserModel = Depends(get_current_user)):
    return {
        "message": "Аутентификация успешна",
        "user_id": current_user.id,
        "username": current_user.username
    }
