from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import csv
from typing import List

# Импортируем модель и Base из models.py
from models import Base, Student, User

class StudentDataManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Создаёт таблицы
        self.Session = sessionmaker(bind=self.engine)

    # Метод для загрузки данных из CSV
    def load_from_csv(self, csv_file_path):
        session = self.Session()
        try:
            # Очищаем существующие данные (опционально)
            session.query(Student).delete()
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                students = []
                
                for row in csv_reader:
                    student = Student(
                        last_name=row['Фамилия'],
                        first_name=row['Имя'],
                        faculty=row['Факультет'],
                        course=row['Курс'],
                        grade=float(row['Оценка'])
                    )
                    students.append(student)
                
                session.bulk_save_objects(students)
                session.commit()
                
            return len(students)
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # Метод для удаления студентов по списку ID
    def delete_students_by_ids(self, student_ids: List[int]):
        session = self.Session()
        try:
            result = session.query(Student).filter(Student.id.in_(student_ids)).delete()
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # Методы для работы со студентами
    def insert_student(self, student):
        session = self.Session()
        try:
            session.add(student)
            session.commit()
            session.refresh(student)
            return student
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def select_all_students(self):
        session = self.Session()
        try:
            return session.query(Student).all()
        finally:
            session.close()

    def get_student(self, student_id):
        session = self.Session()
        try:
            return session.query(Student).filter(Student.id == student_id).first()
        finally:
            session.close()

    # Методы для работы с пользователями
    def create_user(self, username, password):
        session = self.Session()
        try:
            # Проверяем, существует ли пользователь
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                return None
                
            user = User(username=username, password=password)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_by_username(self, username):
        session = self.Session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user
        finally:
            session.close()

    def get_user_by_id(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return user
        finally:
            session.close()