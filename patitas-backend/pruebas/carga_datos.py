"""Crea 200 animales sintéticos alrededor de Mosquera para la prueba de rendimiento.
Uso (desde patitas-backend, con el .env apuntando a una base de PRUEBAS):
    python pruebas/carga_datos.py
Borra los animales/usuario 'seed' previos para que sea repetible."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.contrib.auth import get_user_model
from pets.models import Animal
U = get_user_model()
U.objects.filter(username="seed").delete()
u = U.objects.create_user("seed", "seed@example.com", "Clave-Segura-2026", direccion="x", numero="3000000000")
random.seed(7)
esp = ["perro", "gato", "conejo", "ave"]; sal = ["saludable", "lesionado", "enfermo", "desnutrido"]
Animal.objects.bulk_create([Animal(nombre=f"A{i}", especie=random.choice(esp), estado_salud=random.choice(sal),
    descripcion="dato sintetico", latitud=4.7059 + random.uniform(-0.05, 0.05),
    longitud=-74.2309 + random.uniform(-0.05, 0.05), registrado_por=u) for i in range(200)])
print("Animales creados:", Animal.objects.count())
