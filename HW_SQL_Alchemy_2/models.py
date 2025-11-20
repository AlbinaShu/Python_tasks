from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    faculty = Column(String(50), nullable=False)
    course = Column(String(100), nullable=False)
    grade = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Student(id={self.id}, last_name='{self.last_name}', first_name='{self.first_name}', faculty='{self.faculty}', course='{self.course}', grade={self.grade})>"
