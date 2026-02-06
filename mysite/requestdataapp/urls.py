from django.urls import path

from .views import request_get_view, user_form, handle_file_upload


app_name = "requestdataapp"


urlpatterns = [
    path("get/", request_get_view, name="request_get_view"),
    path("bio/", user_form, name="user_form"),
    path("upload/", handle_file_upload, name="file_upload"),
]
