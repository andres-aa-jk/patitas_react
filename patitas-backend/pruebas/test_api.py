from django.contrib.auth import get_user_model
from rest_framework.test import APITransactionTestCase as APITestCase

from pets.models import Animal

User = get_user_model()
REG = {"username": "ana", "email": "ana@x.co", "direccion": "Calle 1", "numero": "3001112233",
       "password1": "Clave-Segura-2026", "password2": "Clave-Segura-2026"}
ANIMAL = {"nombre": "Luna", "especie": "perro", "estado_salud": "saludable",
          "descripcion": "Encontrada en el parque", "latitud": 4.7059, "longitud": -74.2309}


def crear_usuario(nombre="bob", email="bob@x.co"):
    return User.objects.create_user(username=nombre, email=email, password="Clave-Segura-2026",
                                    direccion="Cra 2", numero="3000000000")


class Autenticado(APITestCase):
    def login(self, user):
        r = self.client.post("/api/auth/login/", {"username": user.username, "password": "Clave-Segura-2026"})
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])


class AuthTests(Autenticado):
    def test_cp01_registro_valido(self):
        r = self.client.post("/api/auth/register/", REG)
        self.assertEqual(r.status_code, 201)
        self.assertIn("access", r.data); self.assertIn("refresh", r.data)
        self.assertEqual(r.data["user"]["username"], "ana")

    def test_cp02_username_duplicado(self):
        crear_usuario("ana", "otro@x.co")
        r = self.client.post("/api/auth/register/", REG)
        self.assertEqual(r.status_code, 400); self.assertIn("username", r.data)

    def test_cp03_email_duplicado(self):
        crear_usuario("otro", "ana@x.co")
        r = self.client.post("/api/auth/register/", REG)
        self.assertEqual(r.status_code, 400); self.assertIn("email", r.data)

    def test_cp04_passwords_distintas(self):
        r = self.client.post("/api/auth/register/", {**REG, "password2": "otra"})
        self.assertEqual(r.status_code, 400)

    def test_cp05_password_debil(self):
        r = self.client.post("/api/auth/register/", {**REG, "password1": "123", "password2": "123"})
        self.assertEqual(r.status_code, 400)

    def test_cp06_faltan_campos(self):
        r = self.client.post("/api/auth/register/", {"username": "z", "password1": "Clave-Segura-2026", "password2": "Clave-Segura-2026"})
        self.assertEqual(r.status_code, 400)
        for c in ("email", "direccion", "numero"):
            self.assertIn(c, r.data)

    def test_cp07_login_ok(self):
        crear_usuario()
        r = self.client.post("/api/auth/login/", {"username": "bob", "password": "Clave-Segura-2026"})
        self.assertEqual(r.status_code, 200)
        for k in ("access", "refresh", "user"):
            self.assertIn(k, r.data)

    def test_cp08_login_incorrecto(self):
        crear_usuario()
        r = self.client.post("/api/auth/login/", {"username": "bob", "password": "mala"})
        self.assertEqual(r.status_code, 401)

    def test_cp09_perfil_sin_sesion(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    def test_cp10_perfil_y_edicion(self):
        u = crear_usuario(); self.login(u)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        r = self.client.patch("/api/auth/me/", {"direccion": "Nueva 123"})
        self.assertEqual(r.status_code, 200); self.assertEqual(r.data["direccion"], "Nueva 123")

    def test_cp11_cambio_password(self):
        u = crear_usuario(); self.login(u)
        mala = self.client.post("/api/auth/change-password/", {"old_password": "x", "new_password1": "Nueva-Clave-9981", "new_password2": "Nueva-Clave-9981"})
        self.assertEqual(mala.status_code, 400)
        ok = self.client.post("/api/auth/change-password/", {"old_password": "Clave-Segura-2026", "new_password1": "Nueva-Clave-9981", "new_password2": "Nueva-Clave-9981"})
        self.assertEqual(ok.status_code, 200)

    def test_cp12_refresh(self):
        crear_usuario()
        r = self.client.post("/api/auth/login/", {"username": "bob", "password": "Clave-Segura-2026"})
        r2 = self.client.post("/api/auth/refresh/", {"refresh": r.data["refresh"]})
        self.assertEqual(r2.status_code, 200); self.assertIn("access", r2.data)


class AnimalTests(Autenticado):
    def test_cp13_crear_animal(self):
        u = crear_usuario(); self.login(u)
        r = self.client.post("/api/animales/", ANIMAL)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["registrado_por_username"], "bob")

    def test_cp14_crear_sin_sesion(self):
        self.assertEqual(self.client.post("/api/animales/", ANIMAL).status_code, 401)

    def test_cp15_listado_publico(self):
        u = crear_usuario(); Animal.objects.create(registrado_por=u, **ANIMAL)
        r = self.client.get("/api/animales/")
        self.assertEqual(r.status_code, 200); self.assertEqual(len(r.data), 1)

    def test_cp16_filtros(self):
        u = crear_usuario()
        Animal.objects.create(registrado_por=u, **ANIMAL)
        Animal.objects.create(registrado_por=u, **{**ANIMAL, "especie": "gato", "estado_salud": "enfermo"})
        self.assertEqual({a["especie"] for a in self.client.get("/api/animales/?especie=gato").data}, {"gato"})
        self.assertEqual({a["estado_salud"] for a in self.client.get("/api/animales/?estado_salud=saludable").data}, {"saludable"})

    def test_cp17_validaciones(self):
        u = crear_usuario(); self.login(u)
        self.assertEqual(self.client.post("/api/animales/", {**ANIMAL, "edad": -1}).status_code, 400)
        self.assertEqual(self.client.post("/api/animales/", {**ANIMAL, "especie": "dragon"}).status_code, 400)
        sin = {k: v for k, v in ANIMAL.items() if k not in ("latitud", "longitud")}
        self.assertEqual(self.client.post("/api/animales/", sin).status_code, 400)

    def test_cp18_cercanos(self):
        u = crear_usuario()
        Animal.objects.create(registrado_por=u, **ANIMAL)
        Animal.objects.create(registrado_por=u, **{**ANIMAL, "latitud": 4.80, "longitud": -74.2309})
        r1 = self.client.get("/api/animales/cercanos/?lat=4.7059&lng=-74.2309&radio=1000")
        self.assertEqual(len(r1.data), 1)
        r2 = self.client.get("/api/animales/cercanos/?lat=4.7059&lng=-74.2309&radio=30000")
        self.assertEqual(len(r2.data), 2)

    def test_cp19_cercanos_sin_coordenadas(self):
        self.assertEqual(self.client.get("/api/animales/cercanos/").status_code, 400)

    def test_cp20_permisos_propietario(self):
        due = crear_usuario("due", "d@x.co"); otro = crear_usuario("otro", "o@x.co")
        a = Animal.objects.create(registrado_por=due, **ANIMAL)
        self.login(otro)
        self.assertEqual(self.client.patch(f"/api/animales/{a.pk}/", {"nombre": "X"}).status_code, 403)
        self.assertEqual(self.client.delete(f"/api/animales/{a.pk}/").status_code, 403)
        self.login(due)
        self.assertEqual(self.client.patch(f"/api/animales/{a.pk}/", {"nombre": "Y"}).status_code, 200)
        self.assertEqual(self.client.delete(f"/api/animales/{a.pk}/").status_code, 204)

    def test_cp21_mis_animales(self):
        a = crear_usuario("a", "a@x.co"); b = crear_usuario("b", "b@x.co")
        Animal.objects.create(registrado_por=a, **ANIMAL); Animal.objects.create(registrado_por=b, **ANIMAL)
        self.assertEqual(self.client.get("/api/animales/mis-animales/").status_code, 401)
        self.login(a)
        self.assertEqual(len(self.client.get("/api/animales/mis-animales/").data), 1)
