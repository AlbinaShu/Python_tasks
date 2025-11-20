from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from db_manager import StudentDataManager

# Инициализация приложения
app = FastAPI()

# URL базы данных
DATABASE_URL = "sqlite:///./students.db"

# Создаём менеджер БД
db_manager = StudentDataManager(DATABASE_URL)

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

# Dependency для передачи менеджера в маршруты
def get_db():
    return db_manager

# CRUD-эндпоинты

@app.post("/students/", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: StudentDataManager = Depends(get_db)):
    try:
        new_student = Student(**student.dict())
        created_student = db.insert_student(new_student)
        return created_student
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/", response_model=list[StudentResponse])
def read_students(db: StudentDataManager = Depends(get_db)):
    students = db.select_all_students()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
def read_student(student_id: int, db: StudentDataManager = Depends(get_db)):
    student = db.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: StudentDataManager = Depends(get_db)
):
    updated_student = db.update_student(student_id, **student.dict(exclude_unset=True))
    if not updated_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return updated_student

@app.delete("/students/{student_id}", response_model=dict)
def delete_student(student_id: int, db: StudentDataManager = Depends(get_db)):
    if db.delete_student(student_id):
        return {"message": "Студент удалён"}
    else:
        raise HTTPException(status_code=404, detail="Студент не найден")

