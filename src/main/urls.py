from django.contrib import admin
from django.urls import path
from . import main_views
from . import trading_views

urlpatterns = [
    path('', main_views.login_view),
    path('signup/', main_views.signup_view),
    path('login/', main_views.login_view),
    path('logout/', main_views.logout_view),
    path('trading/transaction', trading_views.asset_page_form),
    path('trading/<str:ticket>', trading_views.asset_page),
    path('trading/', trading_views.asset_list_page),
    path('portfolio/', trading_views.portfolio_view)
]
