from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages

from .forms import CustomerLoginForm, CustomerSignUpForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomerSignUpForm()

    return render(request, 'OutdoorShop/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "You are now signed in.")
            return redirect('home')
    else:
        form = CustomerLoginForm()

    return render(request, 'OutdoorShop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')