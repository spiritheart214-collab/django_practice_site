from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .admin_mixins import ExportAsCSVMixin, ExportAsExcelMixin
from .common import save_csv_products, save_csv_orders
from .models import Product, ProductImage, Order
from .forms import CSVImportForm, CSVOrdersImportForm


@admin.action(description="Archive products")
def mark_archived(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Пометить продукт как архивированный"""
    queryset.update(archived=True)

@admin.action(description="Unarchive products")
def mark_unarchived(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Пометить продукт как не архивированный"""
    queryset.update(archived=False)


class ProductImagesInline(admin.StackedInline):
    model = ProductImage
    extra = 1

class OrderInline(admin.TabularInline):
    model = Product.orders.through
    extra = 1


@admin.register(Product)
class ProductAdmin(ExportAsCSVMixin, ExportAsExcelMixin, admin.ModelAdmin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
        "export_excel"
    ]
    inlines = [
        OrderInline,
        ProductImagesInline
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived", "created_by"
    list_display_links = "pk", "name"
    ordering = "pk", "name"
    search_fields = "name", "description"
    fieldsets = [
        ("MAIN", {
            "fields": ("name",  "description",  "created_by"),
            "classes": ("wide",)}),

        ("Pricew options", {
            "fields": ("price", "discount"),
            "classes": ("collapse", "wide")}),

        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse", "wide"),
            "description": "Extra options is for soft delete"}),

        ("Images", {
             "fields": ("preview",)})
    ]

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":

            form = CSVImportForm()
            context = {
                "form": form
            }

            return render(request=request, template_name="admin/csv_form.html", context=context)
        form = CSVImportForm(request.POST, request.FILES)

        if not form.is_valid():
            context = {
                "form" : form
            }
            return render(request, "admin/csv_form.html", status=400)

        save_csv_products(file=form)

        self.message_user(request, f"Imported products from CSV")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/", self.import_csv, name="import_products_csv"
            )
        ]
        return new_urls + urls

    def description_short(self, model_object: Product) -> str:
        """Возвращает укороченное описание товара."""
        if len(model_object.description) < 48:
            return model_object.description
        short_description = model_object.description[:48] + "..."
        return short_description


class ProductInline(admin.TabularInline):
    model = Order.products.through
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline
    ]
    list_display = "id", "delivery_adress", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order):
        return obj.user.first_name or obj.user.username

    change_list_template = "shopapp/orders_changelist.html"

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        """
        Обработка импорта CSV для заказов.
        """
        if request.method == "GET":
            form = CSVOrdersImportForm()
            return render(request, "admin/csv_orders_form.html", {"form": form})

        form = CSVOrdersImportForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, "admin/csv_orders_form.html", {"form": form}, status=400)

        try:
            orders = save_csv_orders(file=form)
            self.message_user(request, f"Successfully imported {len(orders)} orders")
        except Exception as e:
            self.message_user(request, f"Import failed: {str(e)}", level="error")

        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv"
            ),
        ]
        return new_urls + urls


