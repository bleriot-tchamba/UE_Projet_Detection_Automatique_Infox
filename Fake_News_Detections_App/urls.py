# Fake_News_Detections / Fake_News_Detections_App /urls.py

from django.urls import URLPattern
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('signin/', views.login, name='login'),
    path('signup/', views.register, name='register'),
]