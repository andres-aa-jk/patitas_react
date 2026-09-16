from django.contrib import admin

from .models import Animal


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especie", "estado_salud", "fecha_registro", "registrado_por")
    list_filter = ("especie", "estado_salud")
    search_fields = ("nombre", "raza", "descripcion")
