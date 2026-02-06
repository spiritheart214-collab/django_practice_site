from django.contrib import admin

from .models import Author, Category, Tag, Article


class ArticleInline(admin.TabularInline):
    """Статья авторов в виде таблицы"""
    model = Article
    extra = 0
    fields = ["title", "content", "pub_date", "category", "tags"]
    readonly_fields = ["pub_date"]
    show_change_link = True
    classes = ["collapse", "wide"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Админ панель автора"""

    list_display = "pk", "name", "bio"
    list_display_links = "pk", "name"
    ordering = "pk", "name"
    search_fields = "name", "bio"
    inlines = [ArticleInline]
    fieldsets = [
        ("Автор", {
            "fields": ("name", "bio"),
            "classes": ("wide",)
        })
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ панель категорий"""

    list_display = "pk", "name",
    list_display_links = "pk", "name"
    ordering = "pk", "name"
    search_fields = "name",


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ панель тегов"""

    list_display = "pk", "name",
    list_display_links = "pk", "name"
    ordering = "pk", "name"
    search_fields = "name",

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Админ панель статей"""

    list_display = ("pk", "title", "short_content", "pub_date", "author_name",
                    "category_name", "display_3_tags","tags_amount")
    list_display_links = "pk", "title", "author_name", "category_name"
    ordering = ["-pub_date", "title", "pk"]
    search_fields = ["title", "content", "author__name", "category__name", "tags__name"]
    readonly_fields = ["pub_date"]
    fieldsets = [
        ("Cтатья", {
            "fields": ("title", "content", "pub_date"),
            "classes": ("wide",)
        }),

        ("Дополнительно", {
            "fields": ("author", "category", "tags"),
            "classes": ("wide", "collapse")
        }),

    ]

    def short_content(self, article: Article) -> str:
        """Функция для отображения короткой версии контента в админке"""
        if article.content:
            content = article.content[:50] + ("..." if len(article.content) >= 50 else "")
            return content
        else:
            return "-"
    short_content.short_description = "Краткое содержание"
    short_content.admin_order_field = "content"

    def tags_amount(self, article: Article) -> int:
        """
        Функция подсчитывающая кол - во тегов для вывода в админ панель
        :param article: модель авторов
        :return: кол - во тегов
        """
        tags = article.tags.count()
        return tags
    tags_amount.admin_order_field = "tags_amount"
    tags_amount.short_description = "Кол-во тегов"

    def display_3_tags(self, article: Article) -> str:
        """Функция для отображения первых трех тегов в админке"""
        tags = article.tags.all()[:3]  # QuerySet
        if not tags:
            return "Нет тегов"
        return ", ".join(tag.name for tag in tags)
    display_3_tags.short_description = "Теги"


    def author_name(self, article: Article) -> str:
        """Функция достает имя автора для последующего отображения в админ панели"""
        if article.author.name:
            return article.author.name
        else:
            return "-"

    author_name.short_description = "Автор"
    author_name.admin_order_field = "author__name"

    def category_name(self, article: Article) -> str:
        """Функция достает категорию для последующего отображения в админ панели"""
        if article.category.name:
            return article.category.name
        else:
            return "-"
    category_name.short_description = "Категория"
    category_name.admin_order_field = "category__name"
