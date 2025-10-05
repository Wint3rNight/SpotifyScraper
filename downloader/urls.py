from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path('check_progress/', views.check_progress, name='check_progress'),
]
