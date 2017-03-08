from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers

from books import views as book_views


app_name="books"
urlpatterns = [
    url(r'^query/$', book_views.QueryView.as_view(), name='query'),
    url(r'^ranked-list/$', book_views.ListView.as_view(), name='ranked-list'),
    url(r'^text/(?P<pk>\d+)$', book_views.DetailView.as_view(), name='text'),
]
