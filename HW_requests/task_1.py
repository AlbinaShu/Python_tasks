# Задание 1. Получение данных из публичного API

# Выберите публичный API. Например, JSONPlaceholder.
# Напишите скрипт, который:
# · отправляет GET-запрос к /posts,
# · извлекает и выводит заголовки и тела первых 5 постов.


import requests
import json

def get_posts():
    # url для получения API
    url = "https://jsonplaceholder.typicode.com/posts"

    try:
        # Отправка GET запроса
        response = requests.get(url)

        # Проверка, что запрос успешен (статус 200)
        if response.status_code == 200:
            # Парсинг JSON
            posts = response.json()

            print("Первые 5 постов:\n")

            # Проход по первым 5 постам
            for i, post in enumerate(posts[:5], start=1):
                print(f"Пост #{i}:")
                print(f"Заголовок: {post['title']}")
                print(f"Тело: {post['body']}")
                print("-" * 50)  
            # Разделитель между постами

        else:
            print(f"Ошибка: HTTP {responce.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")


# Запуск функции
if __name__ == "__main__":
    get_posts()