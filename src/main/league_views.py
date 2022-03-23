from django.shortcuts import render, redirect
from .models import Stock, Profile, Portfolio, Holding, User, League, LeaguePortfolio
from .leagues import create_league, add_user,remove_user 
import random
def view_leagues(request):
    allLeagues = list(League.objects.filter(owner = request.user))
    for league in League.objects.exclude(owner = request.user):
        if request.user in league.participants.all():
            allLeagues.append(league)
    return render(request, 'leagues/leagues.html', {
        'userLeagues': allLeagues,
    })
        

def create_league_view(request):
    errors = []
    if request.method == "POST":
        newleagueName = request.POST.get("league_name", "")
        startBal = request.POST.get("league_start_bal", "")
        icon = random.randint(0,20)
        created = create_league(request.user, newleagueName, startBal, icon)
        
        if created:
            return render(request, f'leagues/{newleagueName}')
        else:
            errors.append(created[1])

    return render(request, 'leagues/league_creation.html', {
        'errors': errors,
    })