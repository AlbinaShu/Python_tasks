# Напишите программу, которая создаёт несколько потоков
# для выполнения функции, которая выводит целые числа от 1 до 10 с задержкой в 1 секунду.
#

import threading
import time

# Функция, которую будет выполнять каждый поток
def print_numbers(thread_id):
    print(f"Поток {thread_id} начал работу")
    for i in range(1, 11):
        print(f"Поток {thread_id}: {i}")
        time.sleep(1)  # Задержка в 1 секунду
    print(f"Поток {thread_id} завершил работу")

# Количество потоков
num_threads = 3

# Создаём и запускаем потоки
threads = []
for i in range(num_threads):
    thread = threading.Thread(target=print_numbers, args=(i+1,))
    threads.append(thread)
    thread.start()

# Ждём завершения всех потоков
for thread in threads:
    thread.join()

print("Все потоки завершили работу!")
