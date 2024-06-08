from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignupForm, LoginForm
from django.http import HttpResponse, JsonResponse
from firebase_admin import db

def index(request):
    return render(request, 'index.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('main_menu')  # Redirige a 'main_menu' después de iniciar sesión
            else:
                # Usuario no es un administrador, muestra un mensaje de error o redirige a otra página
                return HttpResponse("Solo los administradores pueden iniciar sesión.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            # Actualizar Firebase
            ref = db.reference('users')
            ref.child(str(user.id)).set({
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
                # Añadir más campos según sea necesario
            })

            return redirect('main_menu')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def main_menu(request):
    return render(request, 'main_menu.html')

