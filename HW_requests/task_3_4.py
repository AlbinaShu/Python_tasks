import requests
import json

def post_posts():
    # URL
    url = "https://jsonplaceholder.typicode.com/posts"

    # Параметры запроса
    params = {
        "userId": "",
        "title": "qui est esse",
        "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Отправка POST-запроса
        response = requests.post(url, json = params, headers = headers)

        # Проверка статуса ответа
        if response.status_code == 201:
            # Парсим ответ
            created_post = response.json()

            print("Пост успешно создан!")
            print(f"ID поста: {created_post['id']}")
            print(f"Заголовок: {created_post['title']}")
            print(f"Тело: {created_post['body']}")
            print(f"ID пользователя: {created_post['userId']}")

        elif response.status_code == 400:
            return {
                "success": False,
                "status_code": 400,
                "message": (
                    "Ошибка запроса: некорректный формат ID или параметры запроса. "
                    "Проверьте правильность передаваемого ID."
                ),
                "data": None
            }
        
        elif response.status_code == 404:
            return {
                "success": False,
                "status_code": 404,
                "message": (
                    f"Ресурс с ID {resource_id} не найден. "
                    "Возможно, ресурс не был создан или был удалён."
                ),
                "data": None
            }

        else:
            print(f"Ошибка: HTTP {response.status_code}")
            print(f"Ответ сервера: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")

if __name__ == "__main__":
    post_posts()
