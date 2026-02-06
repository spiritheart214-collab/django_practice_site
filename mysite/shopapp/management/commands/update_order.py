from django.core.management import BaseCommand
from django.db.models import QuerySet

from shopapp.models import Product, Order


class Command(BaseCommand):
    """
    Класс обновления заказов
    """
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write("NO ORDER")
            return None

        products: QuerySet = Product.objects.all()

        for product in products:

            order.products.add(product)

        order.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successduly added products {order.products.all()} to order - {order}"
            )
        )
        # for product in products:
        #     order.products.add()


