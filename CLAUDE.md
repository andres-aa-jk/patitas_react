# Instrucciones para Claude Code — Pruebas de Patitas Amigables

Proyecto: backend Django + MongoDB (`patitas-backend/`) y cliente React + Vite (`patitas-react/`).
Entorno: Windows, PowerShell. Responsable de pruebas: Andrés Felipe Bello Peñuela.

## Regla principal (no negociable)
Este trabajo es evidencia para un documento académico. **Registra solo lo que realmente ocurra.**
- Copia la salida real de cada comando en `evidencias/registros/`.
- Si algo falla, no lo arregles en silencio ni lo ocultes: documenta el error tal cual y, si corriges algo, anota qué cambiaste y por qué.
- No inventes, redondees ni "mejores" cifras. Si no puedes ejecutar algo, escribe "No ejecutado" y la razón.
- No modifiques el código de `pets/`, `users/`, `config/` ni `src/` para que las pruebas pasen. Las únicas excepciones permitidas son las de la sección "Rendimiento", siempre revertidas.
- Nunca imprimas ni guardes en los registros la URI de MongoDB con usuario y contraseña; sustitúyela por `<URI>`.

## Antes de empezar
1. Confirma que existen Python 3, Node.js y MongoDB (local o Atlas). Registra las versiones en `evidencias/registros/00_ambiente.txt`:
   `python --version`, `node --version`, `pip list` (Django, DRF, simplejwt, django-mongodb-backend), `mongod --version` o `mongosh --version`, versión de Windows (`systeminfo` solo las líneas de SO, procesador y RAM), navegador y su versión.
2. Sigue `LEEME.md` de la raíz para crear el entorno virtual, instalar `requirements.txt` y crear `patitas-backend/.env`.
   **Usa una base de PRUEBAS**, no la real: `MONGODB_NAME=patitas_pruebas`.
3. `python manage.py makemigrations` y `python manage.py migrate`. Guarda la salida en `01_migraciones.txt`.

## Prueba 1 — API (21 casos)
Desde `patitas-backend` con el entorno virtual activo:
```
python manage.py test pruebas -v 2 *> ..\evidencias\registros\02_pruebas_api.txt
```
El archivo `pruebas/test_api.py` usa `APITransactionTestCase` (vacía los datos entre casos; funciona con MongoDB sin réplica). Django crea y borra su propia base `test_patitas_pruebas`.
Registra cuántos casos corrieron, cuántos pasaron y cuáles fallaron, con el mensaje de error.

## Prueba 2 — Cliente
Desde `patitas-react`: `npm ci`, `npm run build` y `npx oxlint .`. Guarda las salidas en `03_build_cliente.txt` y `04_oxlint.txt`.

## Prueba 3 — Rendimiento (RNF-01: menos de 2000 ms con 50 usuarios simultáneos)
1. `python pruebas/carga_datos.py` (crea 200 animales sintéticos en la base de PRUEBAS).
2. Inicia el servidor: `python manage.py runserver 8000 --noreload` (en una terminal aparte).
3. Mide el código original: `python pruebas/medir.py > ..\evidencias\registros\05_rendimiento_original.txt`.
4. Cuenta las consultas (opcional): con `DEBUG=True`, usa `django.test.utils.CaptureQueriesContext` sobre `/api/animales/cercanos/` y guarda el número.
5. **Cambio temporal y reversible**: en `pets/views.py`, en `get_queryset`, cambia `Animal.objects.all()` por `Animal.objects.select_related("registrado_por")`. Reinicia el servidor, repite el paso 3 guardando en `06_rendimiento_select_related.txt`.
6. Revierte el cambio: `git checkout -- pets/views.py` y confirma con `git status` que no quedan cambios en el código.
Si las cifras difieren de las del informe v1.0, eso es normal: son de otro equipo. Se reportan las nuevas.

## Prueba 4 — Interfaz (navegador real)
Con ambos servidores arriba (backend :8000, frontend :5173 con `npm run dev`), recorre `evidencias/LISTA_INTERFAZ.md` caso por caso.
Si cuentas con una herramienta de navegador (por ejemplo Claude in Chrome), úsala y guarda capturas en `evidencias/capturas/`. Si no, pide al usuario que haga cada paso y te diga qué observó. Marca Aprobado solo lo que se haya visto funcionar.
Revisa especialmente: (a) si el mapa de "Registrar Animal" se ve (hallazgo H-01), (b) errores en la consola del navegador, (c) el menú a 767 px y a 769 px.

## Entregable final
Crea `evidencias/RESUMEN_EJECUCION.md` con: ambiente real, tabla de resultados por prueba (ejecutadas / aprobadas / fallidas), tiempos de rendimiento, hallazgos confirmados o descartados (H-01 a H-10 del informe v1.0), y una lista de lo que no se pudo ejecutar con la razón. Ese resumen será la base del informe v2.0.
