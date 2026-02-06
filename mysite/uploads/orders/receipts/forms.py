from django import forms
from django.contrib.auth.models import Group
from .models import Order, Product


# Создаем кастомный виджет для множественной загрузки файлов
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    """Форма продукта на основе ModelForm"""

    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'discount', 'preview', 'archived']

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 10,
                'cols': 30,
                'placeholder': 'Enter product description here...'
            }),
            'discount': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'step': 1
            }),
            'price': forms.NumberInput(attrs={
                'min': 1,
                'max': 100000,
                'step': 0.01
            })
        }

        labels = {
            'description': 'Product description',
            'preview': 'Product image',
            'archived': 'Archive this product'
        }

        help_texts = {
            'discount': 'Discount percentage (0-100%)',
            'price': 'Price in USD (min: 1, max: 100000)',
        }

        error_messages = {
            'name': {
                'max_length': 'Product name is too long (max 100 characters)',
            },
            'price': {
                'min_value': 'Price must be at least $1',
                'max_value': 'Price cannot exceed $100,000',
            }
        }


    images = MultipleImageField(
        widget=MultipleFileInput(attrs={
            "multiple": True,
            "class": "form-control"
        }),
        required=False,
        label="Additional images"
    )

    # Добавляем дополнительные валидаторы
    def clean_description(self):
        description = self.cleaned_data.get('description')

        # Сохраняем оригинальную валидацию на слово "great"
        if 'great' not in description.lower():
            raise forms.ValidationError("Field must contain word 'great'")

        return description

    def clean_price(self):
        price = self.cleaned_data.get('price')

        # Дополнительная валидация цены
        if price < 1:
            raise forms.ValidationError("Price must be at least $1")
        if price > 100000:
            raise forms.ValidationError("Price cannot exceed $100,000")

        return price

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')

        # Валидация скидки
        if discount and discount < 0:
            raise forms.ValidationError("Discount cannot be negative")
        if discount and discount > 100:
            raise forms.ValidationError("Discount cannot exceed 100%")

        return discount


class OrderForm(forms.ModelForm):
    """Класс описывающий форму заказазов и его поля"""

    class Meta:
        model = Order
        fields = ["delivery_adress", "promocode", "user", "products"]

        widgets = {
            "delivery_adress": forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Введите адрес доставки',
                'rows': 3
            }),
            "promocode": forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Промокод (необязательно)'
            }),
            "user": forms.Select(attrs={
                'class': 'form-select'
            }),
            "products": forms.SelectMultiple(attrs={
                'class': 'form-multiselect',
                'size': 5
            })
        }

        labels = {
            'delivery_adress': 'Адрес доставки',
            'promocode': 'Промокод',
            'user': 'Пользователь',
            'products': 'Товары'
        }

    def clean_delivery_adress(self):
        address: str = self.cleaned_data["delivery_adress"]

        if len(address.strip()) == 0:
            raise forms.ValidationError("Адрес не может быть пустым")

        return address

    def clean_products(self):
        products = self.cleaned_data['products']

        if not products:
            raise forms.ValidationError("Выберите хотя бы один товар")

        if products.count() > 10:
            raise forms.ValidationError("Нельзя выбрать больше 10 товаров")

        return products


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control'}),
        }

class CSVImportForm(forms.Form):
    """Фрма загрузки данных через сsv"""
    csv_file = forms.FileField()


# forms.py - добавь новую форму
class CSVOrdersImportForm(forms.Form):
    """Форма загрузки данных заказов через CSV"""
    csv_file = forms.FileField(label="CSV файл с заказами")