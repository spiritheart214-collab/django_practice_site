from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product

class Command(BaseCommand):
    """
    Класс создания заказа
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create orders with products")

        user = User.objects.get(username="root")
        products: Sequence[Product] = Product.objects.only("id", "name").all()

        order, _ = Order.objects.get_or_create(
            delivery_adress="SPASSKAYA 6a xxx_XXX",
            promocode="SALE_XXX_XXX",
            user=user
        )

        for product in products:
            order.products.add(product)

        self.stdout.write(f"Created order: {order}")

