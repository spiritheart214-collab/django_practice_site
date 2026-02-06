from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Bulk actions")

        result = Product.objects.filter(
            name__contains="TEST"
        ).update(discount=10)


        print(result)
        self.stdout.write("Done")