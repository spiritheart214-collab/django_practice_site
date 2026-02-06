from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file):
    csv_file = TextIOWrapper(
        file.cleaned_data["csv_file"].file,
        encoding="utf-8"  #  Фиксированная кодировка
    )
    reader = DictReader(csv_file)
    # Собираем продукты
    products = []
    for row in reader:
        # Пропускаем пустые строки
        if row and any(row.values()):
            products.append(Product(**row))

    imported_count = 0
    for product in products:
        try:
            product.save()  # Сохраняем по одному
            imported_count += 1
        except Exception as e:
            print(f"Error saving product: {e}")
            continue

    return products

def save_csv_orders(file):
    csv_file = TextIOWrapper(
        file.cleaned_data["csv_file"].file,
        encoding="utf-8"  #  Фиксированная кодировка
    )
    reader = DictReader(csv_file)
    # Собираем продукты
    orders = []
    for row in reader:
        # Пропускаем пустые строки
        if row and any(row.values()):
            orders.append(Order(**row))

    imported_count = 0
    for order in orders:
        try:
            order.save()  # Сохраняем по одному
            imported_count += 1
        except Exception as e:
            print(f"Error saving product: {e}")
            continue

    return orders


