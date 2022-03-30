from email import message
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from stock_updater import update_user_portfolio
from .models import Stock,Profile,Portfolio,Holding,User, Transaction

from .generic_functions import getPortfolioValue, percentage_change, get_user_leagues
from .constants import *
from .holdings import get_holdings, holdings_distribution, holdings_total
import json
import random


# home_view (view func)
# User homepage, not viewable if not logged in.
# Displays both global and user-related information
@login_required
def home_view(request):
	request.user.portfolio_value = getPortfolioValue(request.user)

	# Formulate witty response for if they're makign profit/loss
	if request.user.portfolio_value > 50000:
		message = random.choice(WINING_RESPONSE)
	else:
		message = random.choice(LOSING_RESPONSE)

	# Determine hot and cold stocks
	stocks = [stock for stock in Stock.objects.all()]
	daySortStocks = sorted(stocks, key = lambda stock: stock.day_change)
	weekSortStocks = sorted(stocks, key = lambda stock: stock.week_change)
	HotandCold = [daySortStocks[::-1][0],daySortStocks[::-1][-1],weekSortStocks[::-1][0],weekSortStocks[::-1][-1]]
	for stock in HotandCold:
		cols = stock.display_colour.split(' ')
		stock.col1 = cols[0]
		stock.col2 = cols[1]
	marketDirection = 0
	for i in range(0,len(stocks)):
		marketDirection += stocks[i].week_change
	marketDirection = round(marketDirection / len(stocks),2)
	TopTrader = None # default
	TopTrader = Portfolio.objects.filter(leaderboard_ranking=1)[0].owner
	# get activity feeds for user
	usertransactions= []
	friendtransactions = []
	allTransactions = list(Transaction.objects.filter(portfolio_id = request.user.portfolio))
	
	for transac in Transaction.objects.exclude(portfolio_id = request.user.portfolio):
		if transac.portfolio_id.owner in request.user.profile.friends.all():
			allTransactions.append(transac)
	transac_count = 0
	for transac in Transaction.objects.all():
		transac_count +=1
	for transac in allTransactions:
		if transac.portfolio_id.owner == request.user:
			usertransactions.append([])
			cols = transac.stock_id.display_colour.split(' ')
			transac.stock_id.col1 = cols[0]
			transac.stock_id.col2 = cols[1]
			usertransactions[-1] += [
				transac.portfolio_id.owner.username,
				'bought' if transac.buy else 'sold',
				round(transac.buy_price * transac.volume,2),
				transac.stock_id.ticket,
				transac.stock_id.current_price,
				transac.time,
				transac.stock_id.col1,
				transac.stock_id.col2,
			]		
		elif transac.portfolio_id.owner in request.user.profile.friends.all() and transac.portfolio_id.owner != request.user:
			friendtransactions.append([])
			cols = transac.stock_id.display_colour.split(' ')
			transac.stock_id.col1 = cols[0]
			transac.stock_id.col2 = cols[1]		
			friendtransactions[-1] += [
				transac.portfolio_id.owner.username,
				'bought' if transac.buy else 'sold',
				round(transac.buy_price * transac.volume,2),
				transac.stock_id.ticket,
				transac.stock_id.current_price,
				transac.time,
				transac.stock_id.col1,
				transac.stock_id.col2,
			]

	usertransactions = usertransactions[::-1][:6]
	friendtransactions = friendtransactions[::-1][:6]
	errors = []


	return render(request, 'accounts/home.html', {
		'portfolio_value': request.user.portfolio_value,
		'message': message,
		'TradeNum': transac_count,
		'user_transactions': usertransactions,
		'toptrader': TopTrader,
		'friend_transactions': friendtransactions,
		'market_direction': marketDirection,
		'stocks': HotandCold,
		'errors': errors,
		'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST},
		'global_ranking': request.user.portfolio.leaderboard_ranking
		})

# signup_view (view func)
def signup_view(request):
	if request.user.is_authenticated:
		return redirect('/home')
	errors = []

	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if len(form.errors) > 0:
			for error_field in form.errors.as_data():
				for error in form.errors.as_data()[error_field]:
					errors.append((str(error)[:len(str(error))-2])[2:])
		if form.is_valid():
			user = form.save() # Create account
			login(request, user)
			update_user_portfolio(user.portfolio)
			return redirect('/portfolio')

	return render(request, 'accounts/signup.html', {'errors': errors, 'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}})

# login_view (view func)
def login_view(request):
	if request.user.is_authenticated:
		return redirect('/home')
	errors = []

	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if len(form.errors) > 0:
			for error_field in form.errors.as_data():
				for error in form.errors.as_data()[error_field]:
					errors.append((str(error)[:len(str(error))-2])[2:])
		if form.is_valid():
			# login the user
			user = form.get_user()
			login(request, user)
			return redirect('/home')
	return render(request, "accounts/login.html", {'errors': errors, 'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}})

# logout_view: Not an actual page, just a redirect passthrough to log them out
def logout_view(request):
	logout(request)
	return redirect('/')


def info_view(request):
	errors = []

	return render(request, 'accounts/account_info.html', {
		'league_info': {
			'current_league': "global", 
			'all_leagues': get_user_leagues(request.user), 
			'icon_list': ICON_LIST}
		})

def friends_search_form(request):
	if request.method == "POST":
		form = {}
		username_search = request.POST.get("friend_search", "")
		if User.objects.filter(username = username_search).exists():
			search_result_name =  User.objects.filter(username = username_search)[0]
			form['success'] = True
		else:
			form['success'] = False
			search_result_name = ""
		return render(request, 'accounts/friends_response.html', {"form": form, "search_result_name":search_result_name, 'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}})

def request_friend(request):
	if request.method == "POST":
		form={}
		friend_name = request.POST.get("username")
		if User.objects.filter(username = friend_name).exists():
			newFriend =  User.objects.filter(username = friend_name)[0]
			if request.user in newFriend.profile.requested_me.all():
				form['friends'] = False
			elif newFriend in request.user.profile.friends.all():
				form['friends'] = True
			elif newFriend in request.user.profile.requested_me.all():
				request.user.profile.friends.add(newFriend)
				request.user.profile.requested_me.remove(newFriend)
				newFriend.profile.friends.add(request.user)
				# newFriend.profile.requested_friends.remove(request.user)
				newFriend.profile.save()
				request.user.profile.save()
				form['success'] = True
				form['friends'] = True
				return redirect("/friends")
			else:
				# request.user.profile.requested_friends.add(newFriend)
				newFriend.profile.requested_me.add(request.user)
				request.user.profile.save()
				newFriend.profile.save()
				form['success'] = True
			return render(request, 'accounts/friend_request_response.html', {"form": form, "friend_name":friend_name, 'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}})			
		else:
			return(False,"This user does not exist")
		# add user to friend names requested list



def remove_friend(request):
	if request.method == "POST":
		friend_name = request.POST.get("username")
		if User.objects.filter(username = friend_name).exists():
			oldFriend =  User.objects.filter(username = friend_name)[0]
			if oldFriend in request.user.profile.friends.all():
				request.user.profile.friends.remove(oldFriend)
				request.user.profile.save()
				oldFriend.profile.friends.remove(request.user)
				oldFriend.profile.save()
				# return(True,"")
			if oldFriend in request.user.profile.requested_me.all():
				request.user.profile.requested_me.remove(oldFriend)
			return redirect("/friends")
			# else:
			# 	return(False,f"You're not friends with {friend_name}")
		else:
			return(False,"This user does not exist")

def friends_view(request):
	request.user.portfolio_value = getPortfolioValue(request.user)
	friends = []
	suggested_users = []
	for friend in request.user.profile.friends.all():
		friends.append([])
		friendinfo = friends[-1]
		friendinfo.append(friend.username)
		friend.portfolio_value = getPortfolioValue(friend)
		friendinfo.append(friend.portfolio_value)
		friendinfo.append("21-02-2022")
		winvslose = request.user.portfolio_value - friend.portfolio_value
		if winvslose > 0:
			friendinfo.append("Winning")
			friendinfo.append(winvslose)
		else:
			friendinfo.append("Losing")
			friendinfo.append( winvslose * -1)	
		for suggested in friend.profile.friends.all():
			if not any(suggested.username in sublist for sublist in suggested_users) and suggested != request.user and suggested not in request.user.profile.friends.all() and request.user not in suggested.profile.requested_me.all() and suggested not in request.user.profile.requested_me.all():
				n=-1
				for existing_friend in request.user.profile.friends.all():
					if suggested in existing_friend.profile.friends.all():
						n+=1
				suggested_users.append([suggested.username,friend.username,n])

	
	suggested_users.sort(key=lambda l:l[2], reverse=True)
	print(suggested_users)
	userlist = []

	for player in User.objects.all():
		userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
		totalPortValue = 0
		for holding in userHoldings:
			totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
		totalPortValue +=  player.portfolio.balance
		player.portfolio_value = totalPortValue
		userlist.append(player)
	userlist.sort(key = lambda x: x.portfolio_value)
	userlist = userlist[::-1]

	n=0
	while len(suggested_users)<3 and n<len(userlist):
		if not any(userlist[n].username in sublist for sublist in suggested_users) and userlist[n] != request.user and userlist[n] not in request.user.profile.friends.all() and request.user not in userlist[n].profile.requested_me.all() and userlist[n] not in request.user.profile.requested_me.all():
			suggested_users.append([userlist[n].username,False,0])
		n+=1

	requests=[]

	for friend_request in request.user.profile.requested_me.all():
		mutuals = []
		for friend in request.user.profile.friends.all():
			if friend_request in friend.profile.friends.all():
				mutuals.append(friend.username)
		if len(mutuals) > 1:
			n = len(mutuals)-1
		elif len(mutuals) == 1:
			n=0
		else:
			n=0
			mutuals.append(False)
		requests.append([friend_request.username,mutuals[0],n])

	leagues = [["Y15 League",["Someone1191","Up"],["Someone1391","Down"],["Someone1237","Same"]],["Y20 League",["Someone2054","Same"],["Someone2978","Up"],["Someone2453","Down"]]]
	# add_friend(request,"alex")
	# remove_friend(request,'louis')
	return render(request, 'accounts/friends.html', {
		'friends':friends,
		'leagues':leagues,
		'requests':requests,
		'suggestions':suggested_users,
		'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}
		})
	

def error_view(request, error="Page doesn't exist"):
	return render(request, 'base/error.html', {'error': error, 'league_info': {'current_league': "global", 'all_leagues': get_user_leagues(request.user), 'icon_list': ICON_LIST}})