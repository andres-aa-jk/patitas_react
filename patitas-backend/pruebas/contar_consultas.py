import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
with CaptureQueriesContext(connection) as q:
    r = APIClient(HTTP_HOST="localhost").get("/api/animales/cercanos/?lat=4.7059&lng=-74.2309&radio=5000")
print("CONSULTAS:", len(q), "- ANIMALES DEVUELTOS:", len(r.data))