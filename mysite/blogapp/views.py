from typing import List

from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from .models import Article
from .serializers import ArticleSerializer


@extend_schema(description="Представление для работы со статьями")
class ArticleViewSet(ModelViewSet):
    """API endpoint для работы со статьями"""
    queryset = Article.objects.select_related("author", "category").prefetch_related("tags").all()
    serializer_class = ArticleSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["title", "author__name"]
    filterset_fields = ["title", "content", "pub_date", "author", "category", "tags"]
    ordering_fields = ["pub_date"]

    @extend_schema(summary="Получить статью",
                   description="Возвращает 404 ошибку если статья не найдена",
                   responses={404: OpenApiResponse(description="Пусто"), 200: ArticleSerializer})
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class ArticleListView(ListView):
    """Представление для отображения списка всех статей блога"""
    queryset = (Article.objects.
                select_related("author", "category").
                prefetch_related("tags").
                defer("content").
                filter(pub_date__isnull=False).
                order_by("-pub_date"))

    context_object_name = "articles"


class ArticleDetailView(DetailView):
    """Отображение деталей статьи"""
    model = Article


class LatestArticlesFeed(Feed):
    """
    RSS/Atom фид последних 5 статей блога.

    Предоставляет автоматически обновляемую ленту новых статей
    для RSS-ридеров и агрегаторов.
    """

    # Основные метаданные фида
    title = "Блог: последние статьи"
    description = "Обновления о новых публикациях в блоге"
    link = reverse_lazy("blogapp:articles")

    def items(self) -> List[Article]:
        """
        Возвращает 5 последних опубликованных статей.

        Returns:
            List[Article]: Список из 5 статей, отсортированных по дате публикации
            (новые первыми).
        """
        return (
            Article.objects
            .select_related("author", "category")  # Загружаем связанные модели
            .prefetch_related("tags")  # Загружаем теги
            .defer("content")  # Пропускаем тяжелый контент
            .filter(pub_date__isnull=False)  # Только опубликованные
            .order_by("-pub_date")  # Сортировка: новые первыми
            [:5]  # Берем только 5 записей
        )

    def item_title(self, item: Article) -> str:
        """Заголовок для каждого элемента фида."""
        return item.title

    def item_description(self, item: Article) -> str:
        """
        Описание/контент для каждого элемента фида.
        Возвращает первые 100 символов контента.
        """
        return item.content[:100] if item.content else ""

    def item_link(self, item: Article) -> str:
        """Ссылка на полную версию статьи."""
        return reverse("blogapp:article", kwargs={"pk": item.pk})
