from django.core.management import BaseCommand
from django.db.models import Avg, Min, Max, Count, Sum
from shopapp.models import Product, Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("AGG")

        result = Product.objects.aggregate(
            avg=Avg("price"),
            max=Max("price"),
            min=Min("price"),
            count=Count("price"),
        )

        print(result)

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count('products')
        )

        for order in orders:
            print(f"ORDER #{order.id}")
            print(f"with {order.products_count}")
            print(f"products worth {order.total}")


        self.stdout.write("Done")
