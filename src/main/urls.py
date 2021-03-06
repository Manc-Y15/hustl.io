from django.contrib import admin
from django.urls import path
from . import main_views
from . import trading_views
from . import leaderboards_views
from . import league_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

# This page maps URLs to view-response functions.
# URLs can have variables in them (e.g. "<str:name>"), these are passed into the funcs.

urlpatterns = [
    path('', main_views.landing_page),
    path('favicon.png', RedirectView.as_view(url=staticfiles_storage.url('img/favicon2.png'))),
    path('signup/', main_views.signup_view),
    path('login/', main_views.login_view),
    path('logout/', main_views.logout_view),
    path('home/', main_views.home_view),
    path('trading/transaction', trading_views.asset_page_form),
    path('trading/<str:ticket>', trading_views.asset_page),
    path('leaderboard/', leaderboards_views.leaderboard_view),
    path('leaderboard/friends', leaderboards_views.leaderboard_view_friends),
    path('trading/', trading_views.asset_list_page),
    path('portfolio/', trading_views.portfolio_view),
    path('portfolio/<str:name>', trading_views.other_user_portfolio),
    path('account_info/', main_views.info_view),
    path('friends/', main_views.friends_view),
    path('friends/search', main_views.friends_search_form),
    path('friends/request', main_views.request_friend),
    path('friends/remove', main_views.remove_friend),
    path('leagues/', league_views.view_leagues),
    path('leagues/create', league_views.create_league_view),
    path('leagues/<str:league_name>', league_views.league_leaderboard),
    path('leagues/<str:league_name>/add_member', league_views.add_member),
    path('leagues/<str:league_name>/delete', league_views.delete_league),
    path('leagues/<str:league_name>/leave', league_views.leave_league),
    path('leagues/<str:league_name>/remove_user/<str:username>', league_views.remove_league_user),
    # Asset list page can be rerouted to global one as it's non-specific to leagues
    path('leagues/<str:league_name>/trading', trading_views.asset_list_page),
    # Asset listing page needs a separate variable but still routes to same page
    path('leagues/<str:league_name>/trading/<str:ticket>', league_views.league_asset_listing_page),
    path('leagues/<str:league_name>/portfolio', league_views.league_portfolio),
    path('leagues/<str:league_name>/portfolio/<str:name>', league_views.league_other_portfolio)
]
