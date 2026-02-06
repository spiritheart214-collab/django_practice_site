from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Класс создания продуктов
    """

    def handle(self, *args, **options):
        self.stdout.write("Create products")

        priducts_names = [
            "Laptop",
            "Desktop",
            "Smartphone",
            "Tablet",
            "Headphones",
        ]


        for product_name in priducts_names:
            product, created = Product.objects.get_or_create(name=product_name)
            if created:
                self.stdout.write(f"Created product {product.name}")
                self.stdout.write(self.style.SUCCESS("Products creates"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Product {product.name} already exist"))
