from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
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
		if oldFriend not in request.user.profile.friends.all():
			request.user.profile.friends.remove(oldFriend)
			request.user.profile.save()
			return(True,"")
		else:
			return(False,f"You're not friends with {friend_name}")
	else:
		return(False,"This user does not exist")	
def friends_view(request):
	#getUserProfile = Profile.objects.filter(user = request.user)[0]
	friendNames = []
	friendsWorth = []
	print(request.user.profile.friends.all())
	for friend in request.user.profile.friends.all():
		print(friend.username)
		friendNames.append(friend.username)
		friendsWorth.append(1000)

	friends = [[friendNames[0],100.78,"21-02-2022","Losing",73.58],[friendNames[0],230.78,"10-03-2022","Winning",62.58],["Someone7321",10058.32,"03-03-2022","Winning",3256.58]]

	leagues = [["Y15 League",["Someone1191","Up"],["Someone1391","Down"],["Someone1237","Same"]],["Y20 League",["Someone2054","Same"],["Someone2978","Up"],["Someone2453","Down"]]]
	remove_friend(request,'torin')
	return render(request, 'accounts/friends.html', {
		'friends':friends,
		'leagues':leagues
		})
	

