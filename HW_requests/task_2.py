# Задание 2. Работа с параметрами запроса

# Используйте API OpenWeather для получения данных о погоде.
# Напишите программу, которая:
# · принимает название города от пользователя,
# · отправляет GET-запрос к API и выводит текущую температуру и описание погоды.

import requests

def get_weather(city, api_key):
    # URL
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Параметры запроса
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "ru"
    }

    try:
        # Отправляем GET-запрос
        response = requests.get(url, params=params)
        
        # Проверяем статус
        if response.status_code == 200:
            data = response.json()
            
            # Извлекаем нужные данные
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            
            # Выводим результат
            print(f"\nПогода в {city}:")
            print(f"Температура: {temp} °C")
            print(f"Описание: {description.capitalize()}")
        else:
            print(f"Ошибка: город не найден или неверный API-ключ (HTTP {response.status_code})")
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")

def main():
    # API-ключ 
    API_KEY = "56db8f0e047fcf078925c6cae4f9e631"
    
    # Ввод города от пользователя
    city = input("Введите название города: ").strip()
    
    if city:
        get_weather(city, API_KEY)
    else:
        print("Город не указан!")

if __name__ == "__main__":
    main()
