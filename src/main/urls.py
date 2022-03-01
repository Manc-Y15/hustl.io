from django.contrib import admin
from django.urls import path
from . import main_views
from . import trading_views

urlpatterns = [
    path('', main_views.home),
    path('signup/', main_views.signup_view),
    path('login/', main_views.login_view),
    path('logout/', main_views.logout),
    path('trading/<str:ticket>', trading_views.asset_page),
    path('trading/', trading_views.asset_list_page)
]
