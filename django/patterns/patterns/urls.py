"""
URL configuration for patterns project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from patterns_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('ta/', ta, name='ta'),
    path('login', MyLoginView.as_view(), name='login'),
    path('register', register, name='register'),
    path('logout', logout_user, name='logout'),
    path('lk', lk, name='lk'),
    path('signals', signals, name='signals'),
    path('about_ta', desc_ta, name='about_ta'),
    path('decs_indicators', desc_ind, name='decs_indicators')
]
