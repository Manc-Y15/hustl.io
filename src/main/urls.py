from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('signup/', views.signup_view),
    path('login/', views.login_view),
    path('logout/', views.logout)
]
