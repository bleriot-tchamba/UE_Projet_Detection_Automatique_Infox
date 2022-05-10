# Fake_News_Detections / Fake_News_Detections_App /urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'index'),
    path('signin/', views.signin, name='login'),
    path('signup/', views.register, name='register'),
    path('logout/', views.deconnecter, name='logout'),
    path('license/', views.abonnement, name='license'),
    path('extract_subject/', views.extract_subject, name='extract_subject')
]