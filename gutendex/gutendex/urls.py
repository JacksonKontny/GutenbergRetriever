from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from rest_framework import routers

from books import views, urls as books_urls


# router = routers.DefaultRouter()
# router.register(r'books', views.BookViewSet)

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name='home.html'),
        name='home',
        ),
    # url(r'^', include(router.urls)),
    url(r'^books/', include(books_urls)),
    url(r'^accounts/login/$',
        auth_views.login,
        {'template_name': 'login.html'},
        name='login'),
    url(r'^accounts/logout/$',
        auth_views.logout,
        {'template_name': 'logout.html'},
        name='logout'),
    url(r'^admin/', admin.site.urls),
]
