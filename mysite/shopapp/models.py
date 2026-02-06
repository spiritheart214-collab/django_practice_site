from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    directory_path = "products/product_{pk}/preview/{filename}".format(pk=instance.pk, filename=filename)
    return directory_path


class Product(models.Model):
    """
    Модель Product описывает продукт для продажи в магазине

    Заказы тут: :model:`shopapp.Order`
    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = "products"


    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)


    created_by = models.ForeignKey(User,
                                   on_delete=models.PROTECT,
                                   null=True,
                                   blank=True,
                                   verbose_name="Creator",
                                   related_name="created_products"
                                   )


    def __str__(self) -> str:
        admin_panel_info = f"PRODUCT(pk={self.pk} name={self.name!r})"
        return admin_panel_info

    def get_absolute_url(self):
        """Возвращает канонический URL для статьи."""
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    directory_path ="products/product_{pk}/preview/{filename}".format(pk=instance.product.pk, filename=filename)
    return directory_path


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "order"
        verbose_name_plural = "orders"

    delivery_adress = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(null=True, upload_to="orders/receipts")

    user: User = models.ForeignKey(User, on_delete=models.PROTECT)
    products: Product = models.ManyToManyField(Product, related_name="orders")
