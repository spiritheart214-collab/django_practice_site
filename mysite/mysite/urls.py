"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    products_list.css. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    products_list.css. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    products_list.css. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .sitemaps import sitemaps


urlpatterns = [
    path('admin/doc/', include("django.contrib.admindocs.urls")),
    path('admin/', admin.site.urls),
    path("req/", include("requestdataapp.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView(url_name='schema').as_view(), name="swager"),
    path("api/schema/redoc/", SpectacularRedocView(url_name='schema').as_view(), name="redoc"),
    path("api/", include("myapiapp.urls")),
    path("myauth/", include("myauth.urls")),
    path("shop/", include("shopapp.urls")),
    path("blog/", include("blogapp.urls")),
    path("sitemap.xml/", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]


if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

    urlpatterns.append(
        path('__debug__/', include("debug_toolbar.urls")),
    )
