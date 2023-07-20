from django.contrib import admin
from .models import *


class FondsArrayAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CryptoArrayAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(FondsArray, FondsArrayAdmin)
admin.site.register(CryptoArray, CryptoArrayAdmin)
