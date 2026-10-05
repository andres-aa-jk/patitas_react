# Lista de verificación de la interfaz (rellenar con lo que realmente se observe)
Navegador: ____ versión ____ | Sistema: Windows ____ | Fecha: ____ | Quién probó: ____
Guardar una captura por caso en evidencias/capturas/ con el nombre del caso (ej. UI-05a.png).
Resultado: Aprobado / Falla (describir lo observado). No marcar Aprobado sin haberlo visto.

| Caso | Pasos | Resultado esperado | Resultado obtenido | Captura |
|---|---|---|---|---|
| UI-01 | Abrir http://localhost:5173 | Carga mapa y tarjetas | | |
| UI-01b | Pulsar "Localizarme" (permitir ubicación) | Mapa centrado, círculo de 1 km, animales cercanos | | |
| UI-01c | Clic en un marcador | Ventana con datos del animal | | |
| UI-02 | Sin sesión, abrir /perfil | Redirige a /login | | |
| UI-03 | Login con clave incorrecta | Mensaje de error | | |
| UI-04 | Registrarse desde el formulario | Éxito y redirección | | |
| UI-05a | Entrar a Registrar Animal | Mapa selector visible | | |
| UI-06 | Clic en el mapa selector | Se muestran las coordenadas | | |
| UI-07 | Registrar un animal completo | Éxito y aparece en el inicio | | |
| UI-08 | Abrir Perfil | Datos del usuario | | |
| UI-09 | Cerrar sesión | Se ocultan opciones privadas | | |
| UI-10/11 | Quiénes somos y Contáctanos sin sesión | Accesibles | | |
| RES-375 | DevTools, ancho 375 px | Menú hamburguesa, sin desbordamiento horizontal | | |
| RES-767 | Ancho 767 px | Menú hamburguesa | | |
| RES-769 | Ancho 769 px | Menú lateral de escritorio | | |
| RES-1366 | Ancho 1366 px | Sin desbordamiento horizontal | | |
| JS | Consola (F12) durante el recorrido | Registrar si hay errores en rojo | | |
