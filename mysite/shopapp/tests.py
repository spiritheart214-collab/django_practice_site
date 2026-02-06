import random
from string import ascii_letters

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse

from shopapp.models import Order, Product


class ProductCreateViewTest(TestCase):
    """Класс для тестирования создания продукта"""

    @classmethod
    def setUpClass(cls) -> None:
        """Создание супер пользователя для всего класса"""
        super().setUpClass()
        
        cls.user = User.objects.create_superuser(username="TestUserCreateProduct",
                                            password="TestPasswordCreateproduct",)


    def setUp(self) -> None:
        """Генерация случайного имени продукта"""
        self.product_name = "".join(random.choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()


    def test_create_product(self) -> None:
        """Созданния продукта и проверка на начличие созданного продукта"""
        self.url = reverse("shopapp:create_product")
        self.prodict_data = {
            "name": self.product_name,
            "price": 123,
            "description": "Test description",
            'discount': 10
        }

        self.client.force_login(self.user)
        response = self.client.post(self.url, self.prodict_data)

        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    """Класс тестирующий страницу деталей продукта"""

    @classmethod
    def setUpClass(cls) -> None:
        """Создание продукта и пользователя"""
        super().setUpClass()

        cls.user = User.objects.create_user(username="UserProductDetail", password="TestProductDetail")

        cls.product = Product.objects.create(name="TestProduct")

    def setUp(self):
        """Логирование пользователя"""
        self.client.force_login(self.user)

    def test_get_product(self):
        """тест на получение проудкта"""
        response = self.client.get(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))

        self.assertEqual(response.status_code, 200)

    def test_get_product_check_content(self):
        """Тест на проверку содержимого"""
        response = self.client.get(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))

        self.assertContains(response, self.product.name)


class ProductListViewTestCase(TestCase):
    """Класс теста продуктового списка"""
    fixtures = [
        "product-fixtures.json"
    ]

    def test_products(self) -> None:
        """Тест: на соответствие страницы которую мы полчаем - шаблону и соответствие данных их фикстур - контектсу"""
        response = self.client.get(reverse("shopapp:products_list"))
        products_from_bd = Product.objects.filter(archived=False)
        products_from_context = response.context["products"]

        self.assertQuerySetEqual(
            qs=products_from_bd,
            values=(product.pk for product in products_from_context),
            transform=lambda product: product.pk
        )

        self.assertTemplateUsed(response, "shopapp/products_list.html")


class ProductExportViewTestCase(TestCase):
    """Класс для тестов экспорта json товаров"""
    fixtures = ["product-fixtures.json"]

    def test_get_product_view(self):
        """Тест: проверка статус кода на соответствие коду 200 и соответствие фикстуре продуктов json ответу страницы"""
        response = self.client.get(reverse("shopapp:products-export"))
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        producst_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(producst_data["products"], expected_data)


class OrdersListViewsTestCase(TestCase):
    """Класс для тестов страницы списков товаров"""
    @classmethod
    def setUpClass(cls) -> None:
        """Создание пользователя"""
        super().setUpClass()
        cls.user = User.objects.create_user(username="OrderListTestUser", password="OrderListTestPassword")


    def setUp(self) -> None:
        """Авторизация пользователя"""
        self.client.force_login(self.user)

    def test_orders_view(self) -> None:
        """Тест: получение страницы заказов и наличие на страницу слова 'Orders'"""
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self) -> None:
        """Проверка не авторизованного пользователя"""
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

class OrderDetailViewTestCase(TestCase):
    """Класс для тестирования деталей заказа"""

    @classmethod
    def setUpClass(cls) -> None:
        """Функция преднастройка. Создает пользователя, продукт, заказ и связывает их."""
        super().setUpClass()

        cls.user: User = User.objects.create_user(username="TestUser", password="testuser")
        cls.product: Product = Product.objects.create(name="Test Product", price=100.00)
        cls.order: Order = Order.objects.create(delivery_adress="Test adress",  user=cls.user, promocode="test_promo")

        cls.url = reverse("shopapp:order_details", kwargs={"pk": cls.order.pk})

    def setUp(self) -> None:
        self.order.products.add(self.product)
        self.client.force_login(self.user)

    def test_order_detail_without_permission(self) -> None:
        """Тест: пользователь без прав не может видеть заказ"""
        response = self.client.get(self.url)

        self.assertIn(response.status_code, (403,))

    def test_order_detail_with_permission(self) -> None:
        """Тест: пользователь с правами может видеть страницу заказа"""
        permissions = Permission.objects.get(codename="view_order")
        self.user.user_permissions.add(permissions)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_order_details(self) -> None:
        """
        Тест: проверка на наличие на странице:  адрес заказа, промокода.
        Реализация проверки, что в контексте ответа тот же заказ, который был создан
        """
        permissions = Permission.objects.get(codename="view_order")
        self.user.user_permissions.add(permissions)
        response = self.client.get(self.url)

        self.assertContains(response, self.order.delivery_adress)
        self.assertContains(response, self.order.promocode)
        self.assertContains(response, self.product.name)
        self.assertEqual(response.context["order"], self.order)

    def test_no_autharized_user(self) -> None:
        """Тест: перенаправление пользователя на авторизацию при неавторизированном входе"""
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)


class OrdersExportTestCase(TestCase):
    """Класс тестирования view экспорта продукта"""

    fixtures = ["orders-fixture.json",
                "users-fixture.json",
                "product-fixtures.json"]

    @classmethod
    def setUpClass(cls) -> None:
        """Создание польщователя и ссылки"""
        super().setUpClass()

        cls.user = User.objects.create_user(username="TestUser2", password="TestPassword", is_staff=True)
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)
        cls.url = reverse("shopapp:order-export")

    def setUp(self) -> None:
        """Авторизация"""
        self.client.force_login(self.user)

    def test_get_orders_list(self) -> None:
        """Тест: получения списка продуктов"""
        response = self.client.get(self.url)

        orders = Order.objects.all()
        expected_data = [
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

        orders_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(orders_data["orders"], expected_data)
