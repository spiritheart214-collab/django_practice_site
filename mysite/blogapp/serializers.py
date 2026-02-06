from typing import List

from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Article.

    Преобразует объекты Article в JSON и обратно.
    Включает все поля модели для создания/чтения статей.
    """

    author_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    all_tags = serializers.SerializerMethodField()

    class Meta:
        """Настройка"""
        model = Article
        fields = ("pk", "title", "content", "pub_date", "author",
                  "author_name", "category", "category_name", "tags", "all_tags")

    def get_author_name(self, article: Article) -> str:
        """Получить имя автора"""
        author_name = article.author.name
        return author_name

    def get_category_name(self, article: Article) -> str:
        """Получить категорию"""
        category_name = article.category.name
        return category_name

    def get_all_tags(self, article: Article) -> List[str]:
        """Получить теги"""
        all_tags = [tag.name for tag in article.tags.all()]
        return all_tags
