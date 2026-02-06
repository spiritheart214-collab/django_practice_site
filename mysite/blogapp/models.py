from django.db import models
from django.urls import reverse


class Author(models.Model):
    """Модель описыабщая автора. Содержит информацию об авторе и его биографию."""
    name = models.CharField(max_length=100,
                            null=False,
                            blank=False,
                            db_index=True,
                            verbose_name="Автор",
                            help_text="Полное имя автора (максимум 100 символов)")

    bio = models.TextField(blank=True,
                           verbose_name="Биография",
                           default="",
                           help_text="Краткая биография автора")

    class Meta:
        """Настройка отображения в админке"""
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ["name",]
        indexes = [models.Index(fields=['name',]),]

    def __str__(self):
        """Строковое представление объекта"""
        return self.name

    def short_bio(self):
        """Краткая биография (первые 100 симовлов). Используется в шаблонах по имени функции"""

        if self.bio:
            bio = self.bio[:100] + ("..." if len(self.bio) > 100 else "")
            return bio
        return "Биография не указана"


class Category(models.Model):
    """Модель описывающая категорию статьи"""

    name = models.CharField(max_length=40,
                            verbose_name="Категория",
                            help_text="Категория статьи",
                            unique=True)

    class Meta:
        """Настройка отображения в админке"""
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        """Строковое представление объекта"""
        return self.name


class Tag(models.Model):
    """Класс представляет тэг, который можно назначить статье. Она имеет одно поле - имя"""

    name = models.CharField(max_length=20,
                            verbose_name="Тег",
                            help_text="Тег статьи",
                            unique=True)

    class Meta:
        """Настройка отображения в админке"""
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        """Строковое представление объекта"""
        return self.name


class Article(models.Model):
    """Класс описывающий статью"""

    title = models.CharField(max_length=200,
                             null=False,
                             blank=False,
                             db_index=True,
                             help_text="Заголовок статьи",
                             verbose_name="Заголовок статьи")

    content = models.TextField(help_text="Контент статьи", verbose_name="Контент", blank=True, default="")
    pub_date = models.DateTimeField(db_index=True, verbose_name="Дата", null=True, blank=True)

    author = models.ForeignKey(to=Author,
                               on_delete=models.CASCADE,
                               related_name="author_articles",
                               verbose_name="Автор")

    category = models.ForeignKey(to=Category,
                                 on_delete=models.CASCADE,
                                 related_name="category_articles",
                                 verbose_name="Категория")

    tags = models.ManyToManyField(to=Tag, related_name="articles", verbose_name="Теги")

    class Meta:
        """Настройка отображения в админке"""
        verbose_name = "Cтатья"
        verbose_name_plural = "Статьи"
        ordering = ["-pub_date", "title", "pk"]
        indexes = [models.Index(fields=["title", "pub_date"]), ]

    def __str__(self):
        """Строковое представление объекта"""
        return self.title

    def content_short(self):
        """Краткое содержание статьи"""

        if self.content:
            content = self.content[:100] + ("..." if len(self.content) > 100 else "" )
            return content
        return "Контента нет"

    def get_absolute_url(self):
        """Возвращает канонический URL для статьи."""
        return reverse("blogapp:article", kwargs={"pk": self.pk})
