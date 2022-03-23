from django.contrib import admin
from django.urls import path
from . import main_views
from . import trading_views
from . import leaderboards_views
from . import league_views

urlpatterns = [
    path('', main_views.login_view),
    path('signup/', main_views.signup_view),
    path('login/', main_views.login_view),
    path('logout/', main_views.logout_view),
    path('home/', main_views.home_view),
    path('trading/transaction', trading_views.asset_page_form),
    path('trading/<str:ticket>', trading_views.asset_page),
    path('leaderboard/', leaderboards_views.leaderboard_view),
    path('trading/', trading_views.asset_list_page),
    path('portfolio/', trading_views.portfolio_view),
    path('portfolio/<str:name>', trading_views.other_user_portfolio),
    path('settings/', main_views.settings_view),
    path('friends/', main_views.friends_view),
    path('friends/search', main_views.friends_search_form),
    path('friends/request', main_views.request_friend),
    path('friends/remove', main_views.remove_friend),
    path('leagues/', league_views.view_leagues),
    path('leagues/create', league_views.create_league_view),
    #path('leagues/<str:league_name>', league_views.league_leaderboard),
    #path('leagues/<str:league_name>/portfolio', league_views.league_portfolio),
    #path('leagues/<str:league_name>/portfolio/<str:name>', league_views.league_other_portfolio)
]
