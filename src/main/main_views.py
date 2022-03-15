from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from stock_updater import update_user_portfolio
from .models import Stock,Profile,Portfolio,Holding,User

from .holdings import get_holdings, holdings_distribution, holdings_total


def home(request):
    return render(request, 'home.html', {'holdings': get_holdings(request.user), 'total': holdings_total(request.user),
	'distribution': holdings_distribution(request.user)})

def signup_view(request):
	if request.user.is_authenticated:
		return redirect('/portfolio')
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

	return render(request, 'accounts/signup.html', {'errors': errors})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('/portfolio')
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
		return redirect('/portfolio')
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
def add_friend(request,friend_name):
	if User.objects.filter(username = friend_name).exists():
		newFriend =  User.objects.filter(username = friend_name)[0]
		if newFriend not in request.user.profile.friends.all():
			request.user.profile.friends.add(newFriend)
			request.user.profile.save()
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
	userHoldings = [holding for holding in Holding.objects.filter(owner = request.user)]
	request.user.portfolio_value = request.user.portfolio.balance
	for holding in userHoldings:
		request.user.portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
	friends = []
	print(request.user.profile.friends.all())
	for friend in request.user.profile.friends.all():
		print(friend.username)
		friends.append([])
		friendinfo = friends[-1]
		friendinfo.append(friend.username)
		friendHoldings = [holding for holding in Holding.objects.filter(owner = friend)]
		friend.portfolio_value = friend.portfolio.balance
		for holding in friendHoldings:
			friend.portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
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
	

