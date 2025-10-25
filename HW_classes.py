class Product:
    # Инициализация класса
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

    # Метод обновление количества товаров на складе
    def update_stock(self, quantity: int):
        new_stock = self.stock + quantity

        if new_stock < 0:
            raise ValueError('Количество товаров не может быть отрицательным')

        self.stock = new_stock


class Order:
    # Инициализация класса
    def __init__(self):
        self.products = {}

    # Метод добавление товаров в заказ
    def add_product(self, product, quantity: int):
        # Добавление исключений
        if quantity < 0:
            raise ValueError('Количество товаров не может быть отрицательным')

        if product.stock < quantity:
            raise ValueError('Недостаточно товара на складе')

        # Обновление товаров на складе
        product.update_stock(-quantity)

        if product in self.products:
            self.products[product] += quantity
        else:
            self.products[product] = quantity


    def calculate_total(self):
        total_sum =0
        for product, quantity in self.products.items():
            total_sum += product.price * quantity
        return total_sum



class Store:
    # Инициализация класса
    def __init__(self):
       self.products = []

    def add_product(self, product):
        if not isinstance(product, Product):
            raise TypeError("Можно добавлять только объекты класса Product")

        if product in self.products:
            raise ValueError(f"Товар {product.name} уже присутствует в магазине")

        self.products.append(product)

    def list_products(self):
        if not self.products:
            print("В магазине нет товаров")
            return

        for product in self.products:
            print(f"Товар: {product.name}")
            print(f"  Цена: {product.price} руб.")
            print(f"  На складе: {product.stock} шт.")
            print("-" * 30)

    def create_order(self) -> Order:
        return Order() # Создаем магазин


try:
    store = Store()

    # Создаем товары
    product1 = Product("Ноутбук", 1000, 5)
    product2 = Product("Смартфон", 500, 10)

    # Добавляем товары в магазин
    store.add_product(product1)
    store.add_product(product2)

    # Список всех товаров
    store.list_products()

    # Создаем заказ
    order = store.create_order()

    # Добавляем товары в заказ
    order.add_product(product1, 2)
    order.add_product(product2, 3)

    # Выводим общую стоимость заказа
    total = order.calculate_total()
    print(f"Общая стоимость заказа: {total}")

    # Проверяем остатки на складе после заказа
    store.list_products()

# Отображение ошибки
except ValueError as e:
        print(f"Ошибка: {e}")





