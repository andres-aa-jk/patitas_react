from django.conf import settings
from django.db import models


class Animal(models.Model):
    ESPECIE_CHOICES = [
        ("perro", "Perro"),
        ("gato", "Gato"),
        ("conejo", "Conejo"),
        ("ave", "Ave"),
    ]

    ESTADO_SALUD_CHOICES = [
        ("saludable", "Saludable"),
        ("lesionado", "Lesionado"),
        ("enfermo", "Enfermo"),
        ("desnutrido", "Desnutrido"),
    ]

    nombre = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Nombre"
    )
    especie = models.CharField(
        max_length=20, choices=ESPECIE_CHOICES, verbose_name="Especie"
    )
    raza = models.CharField(max_length=50, blank=True, null=True, verbose_name="Raza")
    edad = models.IntegerField(blank=True, null=True, verbose_name="Edad")
    estado_salud = models.CharField(
        max_length=20, choices=ESTADO_SALUD_CHOICES, verbose_name="Estado de salud"
    )
    descripcion = models.TextField(verbose_name="Descripción")
    foto = models.FileField(
        upload_to="animales/", verbose_name="Foto", blank=True, null=True
    )

    # En MongoDB se usan floats en lugar de Decimal: es más simple y permite
    # índices geoespaciales más adelante.
    latitud = models.FloatField(verbose_name="Latitud")
    longitud = models.FloatField(verbose_name="Longitud")

    fecha_registro = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de registro"
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="animales",
        verbose_name="Registrado por",
    )

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animales"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.especie} - {self.nombre or 'Sin nombre'}"
