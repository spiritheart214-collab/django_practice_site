from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, ArticleListView, ArticleDetailView, LatestArticlesFeed


app_name = "blogapp"

router = DefaultRouter()
router.register("article", ArticleViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles-feed"),
]