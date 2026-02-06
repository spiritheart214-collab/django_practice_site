from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import (ShopIndexView,
                    GroupsListView,

                    ProductsListView,
                    ProductDetailView,
                    ProductCreateView,
                    ProductUpdateView,
                    ProductDeleteView,
                    ProductsDataExportView,
                    ProductViewSet,
                    LatestProductsFeed,

                    OrdersListView,
                    OrdersDetailView,
                    OrdersCreateView,
                    OrdersUpdateView,
                    OrdersDeleteView,
                    OrdersExportView,
                    OrderViewSet,
                    UserOrdersListView,
                    UserOrderExportView)


app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)


urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),

    path("api/", include(routers.urls)),

    path("groups/", GroupsListView.as_view(), name="groups_list"),

    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create", ProductCreateView.as_view(), name="create_product"),
    path("products/latest/feed", LatestProductsFeed(), name="products-feed"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="product_details"),
    path("products/<int:pk>/update", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/confirm_delete", ProductDeleteView.as_view(), name="product_delete"),

    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/сreate", OrdersCreateView.as_view(), name="create_order"),
    path("orders/export", OrdersExportView.as_view(), name="order-export"),
    path("orders/<int:pk>", OrdersDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update", OrdersUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete", OrdersDeleteView.as_view(), name="order_delete"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_ordes_list"),
    path("users/<int:user_id>/orders_export/", UserOrderExportView.as_view(), name="user_ordes_export"),
]
