import logging
from csv import DictWriter

from typing import Any, Dict, List
from timeit import default_timer

from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .common import save_csv_products, save_csv_orders
from .forms import CSVImportForm, ProductForm, OrderForm, GroupForm, CSVOrdersImportForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

log = logging.getLogger(__name__)


@extend_schema(description="Product API endpoints")
class ProductViewSet(ModelViewSet):
    """
    ViewSet для полного цикла работы с продуктами через API.

    Предоставляет CRUD операции (Create, Read, Update, Delete)
    и дополнительные действия для продуктов.
    """

    # 🔹 Базовая конфигурация
    queryset = Product.objects.all()  # Все продукты из БД
    serializer_class = ProductSerializer  # Как сериализовать/десериализовать

    # 🔹 Фильтрация и поиск
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "description"]  # Поиск по этим полям
    filterset_fields = ["name", "description", "price", "discount", "archived"]  # Фильтрация
    ordering_fields = ["name", "price"]  # Сортировка по клику

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        print("\033[1;93mHELLO PRODUCTS LIST\033[0m")
        return super().list(*args, **kwargs)

    # 🔹 Кастомизация стандартного retrieve
    @extend_schema(
        summary="Получить продукт по ID",
        description="Возвращает детальную информацию о продукте или 404 если не найден",
        responses={
            404: OpenApiResponse(description="Продукт не найден"),
            200: ProductSerializer
        }
    )
    def retrieve(self, *args, **kwargs):
        """Получение детальной информации о продукте"""
        return super().retrieve(*args, **kwargs)

    # 🔹 CSV экспорт продуктов
    @action(methods=["get"], detail=False)
    def download_csv(self, request: HttpRequest) -> HttpResponse:
        """
        Скачивание списка продуктов в формате CSV.

        Используется для:
        - Экспорта данных в Excel
        - Миграции данных между системами
        - Создания резервных копий

        Returns:
            HttpResponse: CSV файл с продуктами
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="products-export.csv"'

        # Оптимизация: грузим только нужные поля
        queryset = self.filter_queryset(self.queryset)
        fields = ["name", "description", "price", "discount"]
        queryset = queryset.only(*fields)

        # Записываем CSV
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()  # Заголовки

        for product in queryset:
            writer.writerow({
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "discount": product.discount
            })

        return response

    # 🔹 CSV импорт продуктов
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser]
    )
    def upload_csv(self, request: Request) -> Response:
        """
        Загрузка продуктов из CSV файла.

        Используется для:
        - Массового создания продуктов
        - Импорта данных из других систем
        - Восстановления из резервной копии

        Args:
            request: Запрос с файлом в form-data (поле 'csv_file')

        Returns:
            Response: JSON с созданными продуктами или ошибкой
        """
        form = CSVImportForm(request.POST, request.FILES)

        if not form.is_valid():
            return Response(
                {"error": "Неверные данные", "details": form.errors},
                status=400
            )

        # Импортируем продукты
        products = save_csv_products(file=form)

        # Возвращаем результат
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


@extend_schema(description="Order API endpoints")
class OrderViewSet(ModelViewSet):
    """
    ViewSet для полного цикла работы с заказами через API.

    Предоставляет CRUD операции и управление заказами магазина.
    """

    # 🔹 Базовая конфигурация
    queryset = Order.objects.select_related("user").prefetch_related("products").all()
    serializer_class = OrderSerializer

    # 🔹 Фильтрация и поиск
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["delivery_adress", "promocode", "user__username"]
    filterset_fields = ["user", "promocode", "created_at"]
    ordering_fields = ["created_at", "delivery_adress"]

    # 🔹 CSV экспорт заказов
    @action(methods=["get"], detail=False)
    def download_csv(self, request: HttpRequest) -> HttpResponse:
        """
        Скачивание списка заказов в формате CSV.

        Используется для:
        - Аналитики продаж
        - Отчетов для бухгалтерии
        - Экспорта в CRM системы

        Returns:
            HttpResponse: CSV файл с заказами
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders-export.csv"'

        queryset = self.filter_queryset(self.queryset)
        fields = ["id", "delivery_adress", "promocode", "user", "created_at"]
        queryset = queryset.only(*fields)

        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for order in queryset:
            writer.writerow({
                "id": order.id,
                "delivery_adress": order.delivery_adress or "",
                "promocode": order.promocode or "",
                "user": order.user.id if order.user else "",
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return response

    # 🔹 CSV импорт заказов
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser]
    )
    def upload_csv(self, request: Request) -> Response:
        """
        Загрузка заказов из CSV файла.

        Используется для:
        - Массового создания заказов
        - Импорта заказов из старой системы
        - Тестирования с большим объемом данных

        Args:
            request: Запрос с файлом в form-data (поле 'csv_file')

        Returns:
            Response: JSON с созданными заказами или ошибкой
        """
        form = CSVOrdersImportForm(request.POST, request.FILES)

        if not form.is_valid():
            return Response(
                {"error": "Неверные данные", "details": form.errors},
                status=400
            )

        try:
            orders = save_csv_orders(file=form)
            serializer = self.get_serializer(orders, many=True)
            return Response({
                "message": f"Успешно импортировано {len(orders)} заказов",
                "orders": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": f"Ошибка импорта: {str(e)}"},
                status=400
            )

    # 🔹 Дополнительный метод: статистика по заказам
    @action(methods=["get"], detail=False)
    def stats(self, request: Request) -> Response:
        """
        Статистика по заказам.

        Returns:
            Response: JSON со статистикой
        """
        from django.db.models import Count, Sum

        stats = Order.objects.aggregate(
            total_orders=Count("id"),
            total_users=Count("user", distinct=True),
            # Можно добавить больше агрегаций
        )

        return Response(stats)


class LatestProductsFeed(Feed):
    """
    RSS/Atom фид последних 5 статей блога.

    Предоставляет автоматически обновляемую ленту новых статей
    для RSS-ридеров и агрегаторов.
    """

    # Основные метаданные фида
    title = "Магазин: новые продукты"
    description = "Обновления о новых продуктах в магазине"
    link = reverse_lazy("shopapp:products_list")

    def items(self) -> List[Product]:
        """Возвращает 5 последних опубликованных статей."""
        return (
            Product.objects.filter(created_at__isnull=False)[:5]
        )

    def item_title(self, item: Product) -> str:
        """Заголовок для каждого элемента фида."""
        return item.name

    def item_description(self, item: Product) -> str:
        """
        Описание/контент для каждого элемента фида.
        Возвращает первые 100 символов контента.
        """
        return item.description[:100] if item.description else ""

    def item_link(self, item: Product) -> str:
        """Ссылка на полную версию статьи."""
        return reverse("shopapp:product_details", kwargs={"pk": item.pk})


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["delivery_adress", 'promocode']
    filterset_fields = ["delivery_adress", "promocode", "created_at", "user", "products"]
    ordering_fields = ["created_at"]


class ShopIndexView(View):
    """Класс отображения главной страницы"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Функция отображения главной страницы"""

        products = [
            ("Laptop", 1999),
            ("Desktop", 2999),
            ("Smartphone", 999),
            ("Tablet", 499),
            ("Headphones", 199),
        ]

        context = {
            "time_running": default_timer(),  # Добавлена запятая
            "products": products,
            "shop_name": "TechStore Pro",
            "current_year": 2024,
        }

        print("\033[1;93mSHOP INDEX CONTEX CONTEXT", context, "\033[0m")

        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request=request, template_name="shopapp/shop_index.html", context=context)


class GroupsListView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        """Функция получения страницы"""
        form = GroupForm()
        groups: QuerySet[Group] = Group.objects.prefetch_related("permissions").all()

        context: Dict[str, Any] = {
            "form": form,
            "groups": groups,
        }

        return render(request=request, template_name="shopapp/groups_list.html", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Обработка отправки формы - создание новой группы"""
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect(request.path)
        else:
            # При ошибках - рендерим шаблон с формой, содержащей ошибки
            groups: QuerySet[Group] = Group.objects.prefetch_related("permissions").all()
            context: Dict[str, Any] = {
                "form": form,  # Форма с ошибками!
                "groups": groups,
            }
            return render(request=request, template_name="shopapp/groups_list.html", context=context)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related("user").prefetch_related("products")
    context_object_name = "orders"


class OrdersDetailView(DetailView):
    queryset = Order.objects.select_related("user").prefetch_related("products")

    def get_total_price(self):
        return sum(product.price for product in self.products.all())


class OrdersUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    context_object_name = "order"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        url = reverse("shopapp:order_details",
                      kwargs={"pk": self.object.pk})

        return url


class OrdersCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")


class OrdersDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class OrdersExportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View для выгрузки товаров в формате JsonResponse"""
    permission_required = "shopapp.view_order"

    def test_func(self):
        """Разрешение только для staff пользователей"""
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        """Get - запрос. Получает страницу с JSON ответом"""
        orders: Order = Order.objects.select_related("user").prefetch_related("products").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_adress": order.delivery_adress,
                "promocode": order.promocode,
                "created_at": str(order.created_at),
                "user": order.user.id,
                "products": [product.id for product in order.products.all()
                             ]
            } for order in orders
        ]

        return JsonResponse({"orders": orders_data})


class UserOrdersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Страница заказа пользоваеля"""
    template_name = "shopapp/user_orders_list.html"
    context_object_name = "user_orders"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.user_id = self.kwargs["user_id"]
        self.owner = get_object_or_404(User, id=self.user_id)

    def get_queryset(self):
        """Фильтруем заказы ТОЛЬКО текущего пользователя"""

        queryset = (Order.objects.
                    filter(user=self.owner).
                    select_related("user").
                    prefetch_related("products").
                    order_by("-created_at"))

        return queryset

    def get_context_data(self, **kwargs):
        """Формируем кастомный контекст для шаблона"""
        context = super().get_context_data(**kwargs)

        context["owner"] = self.owner
        context["orders_count"] = context["user_orders"].count()

        return context

    def test_func(self):
        """Доступ для стаффа/админа/пользователя, если он открывает свой заказ ил если есть разрешение на просмотр"""

        site_staff = self.request.user.is_superuser or self.request.user.is_staff
        is_user_order = self.request.user.id == self.user_id
        is_user_has_permission = self.request.user.has_perm("shopapp.view_order")

        if site_staff or is_user_order or is_user_has_permission:
            return True

        return False


class ProductDetailView(LoginRequiredMixin, DetailView):
    template_name = "shopapp/product-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products_list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(UserPassesTestMixin, CreateView):
    """Класс создания продукта"""
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        """Функционал автоматичесукого заполнения создателя формы"""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )

        return response

    def test_func(self):
        return self.request.user.is_superuser


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование продукта."""
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"
    context_object_name = "product"

    def get_success_url(self):
        url = reverse("shopapp:product_details",
                      kwargs={"pk": self.object.pk})

        return url

    def test_func(self):
        """Проверка прав на редактирование"""
        user = self.request.user
        product = self.get_object()

        if user.is_superuser:
            return True

        has_permissions = user.has_perm("shopapp.change_product")

        is_author = False

        if product.created_by:  # Если есть создатель продукта
            is_author = (product.created_by.id == user.id)  # Если пользователь создатель продукта

        is_access = is_author and has_permissions

        return is_access

    def form_valid(self, form):
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )

        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductsDataExportView(View):

    def get(self, request: HttpRequest) -> JsonResponse:
        cahce_key = "products_data_export"
        products_data = cache.get(cahce_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": str(product.price),
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cahce_key, products_data, 300)

        return JsonResponse({"products": products_data})
