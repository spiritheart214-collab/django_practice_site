from typing import List

from django.contrib.sitemaps import Sitemap

from .models import Article

class BlogSiteMap(Sitemap):
    """
    Sitemap для статей блога.

    Генерирует XML карту сайта для поисковых систем (Google, Яндекс).
    Сообщает поисковикам какие страницы индексировать, их приоритет
    и частоту обновлений.
    """
    changefreq = "never"
    priority = 0.5

    def items(self) -> List[Article]:
        """Возвращает список объектов для включения в sitemap."""
        atricles =  Article.objects.filter(pub_date__isnull=False).order_by("-pub_date")
        return atricles

    def lastmode(self, model: Article):
        """Дата последнего изменения статьи."""
        pub_date = model.pub_date
        return pub_date
