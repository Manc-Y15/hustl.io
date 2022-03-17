from email import message
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from .models import Stock,Profile,Portfolio,Holding,User,Transaction
from .generic_functions import getPortfolioValue, percentage_change
from .holdings import get_holdings, holdings_distribution, holdings_total
import json
import random

def home_view(request):
	request.user.portfolio_value = getPortfolioValue(request.user)
	winner = ["nice work!","good job!"]
	loser = ["Don't worry, it'll go up tomorrow. Right??",
			"Oh dear...",
			"We can't all be the best",
			"Maybe trading isn't for you."]
	if request.user.portfolio_value > 50000:
		message = random.choice(winner)
	else:
		message = random.choice(loser)
	stocks = [stock for stock in Stock.objects.all()]
	stocklist = []
	positive = {}
	for stock in stocks:
		historical_prices = json.loads(stock.historical)['history']
		lastWeekPrice = float(historical_prices[len(historical_prices)-4]['oldData'])
		yesterdayPrice =  float(historical_prices[len(historical_prices)-2]['oldData'])
		todayPrice =  float(stock.current_price)
		if yesterdayPrice > todayPrice:
			stock.price_pos = False
		else: stock.price_pos = True
		stock.day_change = percentage_change(yesterdayPrice,todayPrice)
		print(stock.day_change)
		if stock.day_change > 0:stock.day_pos = True
		else: stock.day_pos = False
		stock.week_change = percentage_change(lastWeekPrice,todayPrice)
		print(stock.week_change)
		if stock.week_change > 0:stock.week_pos = True
		else: stock.week_pos = False
		cols = stock.display_colour.split(' ')
		stock.col1 = cols[0]
		stock.col2 = cols[1]
		stocklist.append([])
		stocklist[0].append(stock)
		stocklist[0].append(stock.day_change)
		stocklist[0].append(stock.week_change)


	# get activity feeds for user
	usertransactions= []
	allTransactions = Transaction.objects.filter(portfolio_id = request.user.portfolio)
	activityFeed = []
	transactions = []
	for transac in allTransactions:
		if transac.portfolio_id.owner == request.user:
			activityFeed.append(transac)
		else:
			pass
	for transac in activityFeed:
		transactions.append([])
		newtransacaction = transactions[-1]
		newtransacaction.append(transac.portfolio_id.owner.username)
		if transac.buy == True:
			newtransacaction.append('bought')
		else:
			newtransacaction.append('sold')
		newtransacaction.append(round(transac.buy_price * transac.volume,2))
		newtransacaction.append(transac.stock_id.ticket)
		newtransacaction.append(transac.stock_id.current_price)
		newtransacaction.append(transac.time)
	transactions.reverse()
	transactions = transactions[:6]
	usertransactions = transactions
	# friend activity feed
	friendtransactions = []
	allTransactions = Transaction.objects.all()
	activityFeed = []
	transactions = []
	for transac in allTransactions:
		if transac.portfolio_id.owner in request.user.profile.friends.all():
			activityFeed.append(transac)
		else:
			pass
	for transac in activityFeed:
		transactions.append([])
		newtransacaction = transactions[-1]
		newtransacaction.append(transac.portfolio_id.owner.username)
		if transac.buy == True:
			newtransacaction.append('bought')
		else:
			newtransacaction.append('sold')
		newtransacaction.append(round(transac.buy_price * transac.volume,2))
		newtransacaction.append(transac.stock_id.ticket)
		newtransacaction.append(transac.stock_id.current_price)
		newtransacaction.append(transac.time)
	print(transactions)
	transactions.reverse()
	transactions = transactions[:6]
	print(transactions)
	friendtransactions = transactions

	errors = []
	return render(request, 'accounts/home.html', {
		'portfolio_value': request.user.portfolio_value,
		'message': message,
		'user_transactions': usertransactions,
		'friend_transactions': friendtransactions,
		'stocks': stocks[:4],
		'errors': errors,
		})

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
			return redirect('/home')

	return render(request, 'accounts/signup.html', {'errors': errors})


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
			# login
			user = form.get_user()
			login(request, user)
		return redirect('/home')
	return render(request, "accounts/login.html", {'errors': errors})

def logout_view(request):
	logout(request)
	return redirect('/')

def logout(request):
	if request.method == 'POST':
		logout(request)
		return redirect('/')

def settings_view(request):
	errors = []

	return render(request, 'accounts/account_settings.html', {})

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
		return render(request, 'accounts/friends_response.html', {"form": form, "search_result_name":search_result_name})

def request_friend(request):
	if request.method == "POST":
		form={}
		friend_name = request.POST.get("username", "")
		if User.objects.filter(username = friend_name).exists():
			newFriend =  User.objects.filter(username = friend_name)[0]
			if newFriend not in request.user.profile.requested_friends.all():
				request.user.profile.requested_friends.add(newFriend)
				request.user.profile.save()
				newFriend.profile.friends.add(request.user)
				newFriend.profile.save()
				return(True,"")
				form['success'] = True
			else:
				return(False,f"You've already requested to be friends with {friend_name}")
				form['success'] = False
			return render(request, 'accounts/friends_response.html', {"form": form, "search_result_name":search_result_name})			
		else:
			return(False,"This user does not exist")
		# add user to friend names requested list

def add_friend(request,friend_name):
	if User.objects.filter(username = friend_name).exists():
		newFriend =  User.objects.filter(username = friend_name)[0]
		if newFriend  in request.user.profile.requested_friends.all():
			request.user.profile.friends.add(newFriend)
			request.user.profile.save()
			newFriend.profile.friends.add(request.user)
			newFriend.profile.save()
			return(True,"")
		else:
			return(False,f"You're already friends with {friend_name}")
	else:
		return(False,"This user does not exist")
def remove_friend(request,friend_name):
	if User.objects.filter(username = friend_name).exists():
		oldFriend =  User.objects.filter(username = friend_name)[0]
		if oldFriend in request.user.profile.friends.all():
			request.user.profile.friends.remove(oldFriend)
			request.user.profile.save()
			oldFriend.profile.save()
			return(True,"")
		else:
			return(False,f"You're not friends with {friend_name}")
	else:
		return(False,"This user does not exist")

def friends_view(request):
	request.user.portfolio_value = getPortfolioValue(request.user)
	friends = []
	print(request.user.profile.friends.all())
	for friend in request.user.profile.friends.all():
		print(friend.username)
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

	leagues = [["Y15 League",["Someone1191","Up"],["Someone1391","Down"],["Someone1237","Same"]],["Y20 League",["Someone2054","Same"],["Someone2978","Up"],["Someone2453","Down"]]]
	add_friend(request,"alex")
	remove_friend(request,'louis')
	return render(request, 'accounts/friends.html', {
		'friends':friends,
		'leagues':leagues
		})
	



