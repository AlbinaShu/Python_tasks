from typing import Dict, List, Optional, Union

# Типы для аннотаций
BookID = int
BookTitle = str
BookAuthor = str
BookInfo = Dict[str, Union[BookTitle, BookAuthor, bool]]
Library = Dict[BookID, BookInfo]

# Глобальная переменная для хранения книг
library: Library = {}

def add_book(book_id: BookID, title: BookTitle, author: BookAuthor) -> None:
    """
    Добавляет книгу в библиотеку.

    Args:
        book_id: Уникальный идентификатор книги
        title: Название книги
        author: Автор книги
    """
    library[book_id] = {
        'title': title,
        'author': author,
        'is_borrowed': False
    }


def find_book(search_term: Union[BookID, BookTitle, BookAuthor]) -> Optional[BookInfo]:
    """
    Находит книгу по ID, названию или автору.

    Args:
        search_term: ID, название или автор книги для поиска

    Returns:
        Информация о книге или None, если книга не найдена
    """
    # Поиск по ID
    if isinstance(search_term, int) and search_term in library:
        return library[search_term]

    # Поиск по названию или автору
    for book_info in library.values():
        if book_info['title'] == search_term or book_info['author'] == search_term:
            return book_info

    return None


def is_book_borrowed(book_id: BookID) -> bool:
    """
    Проверяет, взята ли книга.

    Args:
        book_id: ID книги для проверки

    Returns:
        True если книга взята, False если доступна
    """
    if book_id not in library:
        raise ValueError(f"Книга с ID {book_id} не найдена в библиотеке")

    return library[book_id]['is_borrowed']


def return_book(book_id: BookID) -> bool:
    """
    Возвращает книгу в библиотеку.

    Args:
        book_id: ID возвращаемой книги

    Returns:
        True если операция успешна, False если книга уже была в библиотеке
    """
    if book_id not in library:
        raise ValueError(f"Книга с ID {book_id} не найдена в библиотеке")

    if not library[book_id]['is_borrowed']:
        return False  # Книга уже была в библиотеке

    library[book_id]['is_borrowed'] = False
    return True


