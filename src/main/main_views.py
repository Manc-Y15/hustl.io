from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from .models import Stock

from .holdings import get_holdings, holdings_distribution, holdings_total


def home(request):
    return render(request, 'home.html', {'holdings': get_holdings(request.user), 'total': holdings_total(request.user),
	'distribution': holdings_distribution(request.user)})

def signup_view(request):
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

def logout(request):
	if request.method == 'POST':
		logout(request)
		return redirect('/')
