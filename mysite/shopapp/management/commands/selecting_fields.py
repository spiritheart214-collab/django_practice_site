from django.contrib.auth.models import User
from django.core.management import BaseCommand


from shopapp.models import Product

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")

        users_info = User.objects.values_list("username", flat=True)

        for user_indo in users_info:
            print(user_indo)

        # product_values = Product.objects.values("pk", "name")
        #
        # for product_value in product_values:
        #     print(product_value)
        #     print(product_value)

        self.stdout.write(f"Done")
