from django.urls import path

from .views import HelloWorldView, GroupListView


app_name = "myapiapp"


urlpatterns = [
    path("hello/", HelloWorldView.as_view(), name="hello"),
    path("groups/", GroupListView.as_view(), name="groups"),
]