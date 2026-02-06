from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (set_cookie_vierw,
                    get_cookie_view,
                    set_session_view,
                    get_session_view,
                    AboutMeView,
                    RegisterView,
                    my_logout_view,
                    TestView,
                    UsersListView, UserDetailView,
                    HelloView)


app_name = "myauth"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/",
         LoginView.as_view(
             template_name="myauth/login.html",
             redirect_authenticated_user=True,
         ),
         name="login"),
    path("logout/", my_logout_view, name="logout"),
    path("about_me/", AboutMeView.as_view(), name="about_me"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("user_list/", UsersListView.as_view(), name="user_list"),
    path("test_view/", TestView.as_view(), name="test_view"),

    path("hello/", HelloView.as_view(), name="hello"),

    path("cookie/get/", get_cookie_view, name="cookie_get"),
    path("cookie/set/", set_cookie_vierw, name="cookie_set"),

    path("session/get/", get_session_view, name="session_get"),
    path("session/set/", set_session_view, name="session_set"),

]
