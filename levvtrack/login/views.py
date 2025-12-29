from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is None:
                context = {'error': 'Invalid username or password', 'form': form}
                return render(request, "login/login.html", context)
            login(request, user)
            return redirect("/")
        else:
            context = {'error': 'Invalid form', 'form': form}
            return render(request, "login/login.html", context)
    else:
        form = LoginForm()
    context = { 'form': form }
    return render(request, "login/login.html", context)

@login_required
def logout_view(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("/")
        logout(request)
        return redirect("/")
    return render(request, "login/logout.html", {})

