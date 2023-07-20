from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout, login
from .decorators import anonymous_required

from .forms import *


def index(request):
    return render(request, 'patterns_app/index.html')


def ta(request):
    return render(request, 'patterns_app/ta.html')


def signals(request):
    return render(request, 'patterns_app/signals.html')


def desc_ind(request):
    return render(request, 'patterns_app/desc_ind.html')


def desc_ta(request):
    return render(request, 'patterns_app/desc_ta.html')


def lk(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'patterns_app/lk.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if User.objects.filter(username=request.POST['username']):
            return render(request, 'patterns_app/register.html', {'form': RegisterForm(), 'msg': f'Логин {request.POST["username"]} уже существует, выберите другой.'})
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    context = {
        'form': form,
        'msg': ''
    }
    return render(request, 'patterns_app/register.html', context)


class MyLoginView(LoginView):
    template_name = 'patterns_app/login.html'
    form_class = AuthUserForm

    def get_success_url(self):
        return reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(MyLoginView, self).dispatch(request, *args, **kwargs)


def logout_user(request):
    logout(request)
    return redirect('home')
