from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Book(BaseModel):
    """Модель книги с валидацией."""
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    categories: List[str] = Field(default_factory=list)
    is_borrowed: bool = False
    borrowed_by: Optional[int] = None
    borrow_date: Optional[datetime] = None

    @field_validator('categories')
    def validate_categories(cls, categories: List[str]) -> List[str]:
        """Валидация категорий книги."""
        # Проверяем, что каждая категория не пустая
        for category in categories:
            if not category.strip():
                raise ValueError('Категория не может быть пустой строкой')

            if len(category) > 50:
                raise ValueError('Название категории не может превышать 50 символов')

        # Проверяем максимальное количество категорий
        if len(categories) > 5:
            raise ValueError('Книга не может иметь более 5 категорий')

        return [category.strip().title() for category in categories]

    @field_validator('title', 'author')
    def validate_string_fields(cls, value: str) -> str:
        """Валидация строковых полей."""
        if not value.strip():
            raise ValueError('Поле не может быть пустым')
        return value.strip()


class User(BaseModel):
    """Модель пользователя библиотеки."""
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    borrowed_books: List[int] = Field(default_factory=list)

    @field_validator('email')
    def validate_email(cls, email: str) -> str:
        """Простая валидация email."""
        if '@' not in email:
            raise ValueError('Некорректный формат email')
        return email.lower().strip()


class Library(BaseModel):
    """Модель библиотеки с книгами и пользователями."""
    books: Dict[int, Book] = Field(default_factory=dict)
    users: Dict[int, User] = Field(default_factory=dict)

    def total_books(self) -> int:
        """
        Возвращает общее количество книг в библиотеке.

        Returns:
            Количество книг в библиотеке
        """
        return len(self.books)