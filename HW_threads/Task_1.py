# Напишите программу, которая создаёт 2 потока для вычисления квадратов
# и кубов целых чисел от 1 до 10.

import threading

# Общие списки для результатов
squares = []
cubes = []

# Функция для вычисления квадратов
def calculate_squares():
    for i in range(1, 11):
        squares.append(i ** 2)
    print("Квадраты вычислены:", squares)

# Функция для вычисления кубов
def calculate_cubes():
    for i in range(1, 11):
        cubes.append(i ** 3)
    print("Кубы вычислены:", cubes)

# Создаём потоки
thread1 = threading.Thread(target=calculate_squares)
thread2 = threading.Thread(target=calculate_cubes)

# Запускаем потоки
thread1.start()
thread2.start()

# Ждём завершения обоих потоков
thread1.join()
thread2.join()

# Итоговый вывод
print("\nИтоговые результаты:")
print("Числа от 1 до 10: ", list(range(1, 11)))
print("Квадраты:         ", squares)
print("Кубы:             ", cubes)


