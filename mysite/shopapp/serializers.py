from typing import List, Optional

from rest_framework import serializers

from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор продуктов."""
    class Meta:
        model = Product
        fields = ('pk', 'name', 'price', 'description', 'discount', 'preview', 'archived', "created_at")


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор заказов."""

    user_name = serializers.SerializerMethodField()
    product_names = serializers.SerializerMethodField()


    class Meta:
        model = Order
        fields = "user", "delivery_adress", "promocode", "created_at", "receipt", "user_name", "product_names"

    def get_product_names(self, obj) -> List[str]:
        """Получить список названий продуктов"""
        return [product.name for product in obj.products.all()]

    def get_user_name(self, obj) -> Optional[str]:
        """Получить пользователя"""
        if obj.user:
            return obj.user.username
        return None
