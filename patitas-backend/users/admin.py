from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "numero", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Datos de contacto", {"fields": ("direccion", "numero")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Datos de contacto", {"fields": ("email", "direccion", "numero")}),
    )
