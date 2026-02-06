from random import random

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views import View
from django.utils.translation import gettext_lazy as _, ngettext

from .forms import ProfileForm
from .models import Profile


class HelloView(View):
    welcome_message = _("welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"<h2>{products_line}</h2>"
        )

class TestView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return JsonResponse({"test1": "test1", "test2": "test2"})


class AboutMeView(LoginRequiredMixin, UpdateView):
    """View для страницы about-me с формой изменения аватара"""
    model = Profile
    form_class = ProfileForm
    template_name = "myauth/about-me.html"
    success_url = reverse_lazy("myauth:about_me")

    def get_object(self, queryset=None):
        """Получаем профиль текущего пользователя"""
        user_profile = self.request.user.profile
        return user_profile


class UserDetailView(LoginRequiredMixin,DetailView):
    """Страница конкретного пользователя"""
    model = Profile
    template_name = "myauth/user_detail.html"
    context_object_name = "profile"


    def get_queryset(self):
        return Profile.objects.select_related("user")

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса (изменение аватарки)"""
        profile = self.get_object()

        # ПРОВЕРКА: только админ может менять
        if not request.user.is_staff:

            raise PermissionDenied("Only staff can edit profiles")

        # Меняем аватарку
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()

        return redirect('myauth:user_detail', pk=profile.pk)

class UsersListView(ListView):
    template_name = "myauth/users_list.html"
    context_object_name = "profiles"
    queryset = Profile.objects.select_related("user")

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about_me")

    def form_valid(self, form):
        # Сохраняем пользователя
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        # Получаем данные из формы
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        # Аутентифицируем пользователя
        user = authenticate(
            request=self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)

        return response


def set_cookie_vierw(requset: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("test1", "test1-value", max_age=3600)
    return response





@cache_page(60 * 2)
def get_cookie_view(requset: HttpRequest) -> HttpResponse:
    value = requset.COOKIES.get("test1", "default")
    return HttpResponse(f"COOKIE VALUE: {value} + {random()}")

@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["Test2"] = "test2 - value"
    return HttpResponse("Session set")


def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("Test2")
    return HttpResponse(f"Session value - {value!r}")


def my_logout_view(request):
    logout(request)
    return redirect('myauth:login')
