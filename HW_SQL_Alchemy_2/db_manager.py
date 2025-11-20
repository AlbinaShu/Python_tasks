from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import csv

# Импортируем модель и Base из models.py
from models import Base, Student

class StudentDataManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Создаёт таблицы
        self.Session = sessionmaker(bind=self.engine)

    def insert_student(self, student):
        session = self.Session()
        try:
            session.add(student)
            session.commit()
            return student  # Возвращаем объект для возврата в API
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def select_all_students(self):
        session = self.Session()
        try:
            students = session.query(Student).all()
            return students
        finally:
            session.close()

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
        try:
            students = session.query(Student).filter(Student.faculty == faculty_name).all()
            return students
        finally:
            session.close()

    def get_unique_courses(self):
        session = self.Session()
        try:
            courses = session.query(Student.course).distinct().all()
            return [course[0] for course in courses]
        finally:
            session.close()

    def get_average_grade_by_faculty(self, faculty_name):
        session = self.Session()
        try:
            avg_grade = session.query(func.avg(Student.grade))\
                .filter(Student.faculty == faculty_name).scalar()
            return avg_grade
        finally:
            session.close()

    def update_student(self, student_id, **kwargs):
        session = self.Session()
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return None

            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)

            session.commit()
            return student
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_student(self, student_id):
        session = self.Session()
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False
            session.delete(student)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_students_by_faculty(self, faculty_name):
        session = self.Session()
        try:
            query = session.query(Student).filter(Student.faculty == faculty_name)
            count = query.count()
            query.delete()
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
