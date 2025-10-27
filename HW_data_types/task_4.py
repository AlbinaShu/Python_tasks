from typing import Dict, Optional


# Простое исключение для книги
class BookNotAvailable(Exception):
    pass


# Глобальная переменная для хранения книг
library: Dict[int, Dict] = {}


def add_book(book_id: int, title: str, author: str) -> None:
    """Добавляет книгу в библиотеку."""
    library[book_id] = {
        'title': title,
        'author': author,
        'is_borrowed': False
    }


def is_book_borrowed(book_id: int) -> bool:
    """
    Проверяет, взята ли книга.

    Raises:
        BookNotAvailable: если книга уже взята
    """
    if book_id not in library:
        raise ValueError(f"Книга с ID {book_id} не найдена")

    if library[book_id]['is_borrowed']:
        raise BookNotAvailable(f"Книга '{library[book_id]['title']}' уже взята")

    return False


def borrow_book(book_id: int) -> None:
    """Берет книгу из библиотеки."""
    # Проверяем доступность книги
    is_book_borrowed(book_id)  # Вызовет BookNotAvailable если книга взята

    # Если исключение не вызвано, книга доступна - берем её
    library[book_id]['is_borrowed'] = True


def return_book(book_id: int) -> None:
    """Возвращает книгу в библиотеку."""
    if book_id not in library:
        raise ValueError(f"Книга с ID {book_id} не найдена")

    library[book_id]['is_borrowed'] = False


# Пример использования
if __name__ == "__main__":
    # Добавляем книги
    add_book(1, "Война и мир", "Лев Толстой")
    add_book(2, "1984", "Джордж Оруэлл")

    # Пробуем взять книгу
    try:
        borrow_book(1)
        print("✓ Книга 1 успешно взята")
    except BookNotAvailable as e:
        print(f"✗ {e}")

    # Пробуем взять ту же книгу еще раз
    try:
        borrow_book(1)
        print("✓ Книга 1 успешно взята")
    except BookNotAvailable as e:
        print(f"✗ {e}")  # Выведет ошибку - книга уже взята

    # Проверяем статус книги
    try:
        result = is_book_borrowed(1)
        print(f"Книга 1 доступна: {not result}")
    except BookNotAvailable as e:
        print(f"✗ {e}")

    # Возвращаем книгу
    return_book(1)
    print("✓ Книга 1 возвращена")
