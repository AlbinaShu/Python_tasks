from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
import csv


Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)  # Фамилия
    first_name = Column(String(50), nullable=False)  # Имя
    faculty = Column(String(50), nullable=False)  # Факультет
    course = Column(String(100), nullable=False)  # Курс
    grade = Column(Float, nullable=False)  # Оценка

    def __repr__(self):
        return f"<Student(last_name='{self.last_name}', first_name='{self.first_name}', faculty='{self.faculty}', course='{self.course}', grade={self.grade})>"


class StudentDataManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_student(self, student):
        session = self.Session()
        try:
            session.add(student)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def select_all_students(self):
        session = self.Session()
        students = session.query(Student).all()
        session.close()
        return students

    def load_from_csv(self, csv_file_path):
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                student = Student(
                    last_name=row['Фамилия'],
                    first_name=row['Имя'],
                    faculty=row['Факультет'],
                    course=row['Курс'],
                    grade=float(row['Оценка'])
                )
                self.insert_student(student)

    def get_students_by_faculty(self, faculty_name):
        session = self.Session()
        students = session.query(Student).filter(Student.faculty == faculty_name).all()
        session.close()
        return students

    def get_unique_courses(self):
        session = self.Session()
        courses = session.query(Student.course).distinct().all()
        session.close()
        return [course[0] for course in courses]

    def get_average_grade_by_faculty(self, faculty_name):
        session = self.Session()
        average_grade = session.query(func.avg(Student.grade)).filter(Student.faculty == faculty_name).scalar()
        session.close()
        return average_grade


# main.py
if __name__ == "__main__":
    # Инициализируем менеджер данных (используем SQLite для простоты)
    manager = StudentDataManager('sqlite:///students.db')

    # 1. Загружаем данные из CSV
    manager.load_from_csv('students.csv')
    print("Данные загружены из CSV.")

    # 2. Получаем всех студентов
    all_students = manager.select_all_students()
    print("\nВсе студенты:")
    for student in all_students:
        print(student)

    # 3. Тестируем метод получения студентов по факультету
    avt_students = manager.get_students_by_faculty('АВТФ')
    print(f"\nСтуденты факультета АВТФ: {avt_students}")

    # 4. Получаем список уникальных курсов
    unique_courses = manager.get_unique_courses()
    print(f"\nУникальные курсы: {unique_courses}")

    # 5. Считаем средний балл по факультету
    avg_grade_rze = manager.get_average_grade_by_faculty('РЭФ')
    print(f"\nСредний балл по факультету РЭФ: {avg_grade_rze}")

