from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers

from books import views, urls as books_urls


# router = routers.DefaultRouter()
# router.register(r'books', views.BookViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html')),
    # url(r'^', include(router.urls)),
    url(r'^books/', include(books_urls)),
    url(r'^admin/', admin.site.urls),
]
