from typing import List

from django.contrib.sitemaps import Sitemap

from .models import Product

class ShopSiteMap(Sitemap):
    """
    Sitemap для продуктов.

    Генерирует XML карту сайта для поисковых систем (Google, Яндекс).
    Сообщает поисковикам какие страницы индексировать, их приоритет
    и частоту обновлений.
    """
    changefreq = "monthly"
    priority = 0.5

    def items(self) -> List[Product]:
        """Возвращает список объектов для включения в sitemap."""
        products = Product.objects.order_by("-created_at")
        return products

    def lastmod(self, model: Product):
        """Дата последнего изменения статьи."""
        pub_date = model.created_at
        return pub_date
