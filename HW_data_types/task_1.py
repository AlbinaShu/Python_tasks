from pydantic import BaseModel, field_validator

class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool

Book(title='jbj', author='ddhjd', year=12, available=True)

class User(BaseModel):
    name: str
    email: str
    membership_id: int

    @field_validator('email', mode='before')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('email должен содержать @')
        return v

validate_email = User(name='Vasya', email='sjhjs', membership_id=0)
