# Cómo usar este paquete (Windows)

1. Descarga/clona el repositorio: `git clone https://github.com/andres-aa-jk/patitas_react.git`
2. Copia el contenido de esta carpeta **encima** de la raíz del repositorio (debe quedar `CLAUDE.md` junto a `LEEME.md`,
   `patitas-backend\pruebas\` dentro del backend y la carpeta `evidencias\`).
3. Ten MongoDB listo (servicio local o URI de Atlas). Crea tú mismo `patitas-backend\.env`; **no pegues la URI en el chat**.
4. Abre Claude (aplicación de escritorio) → pestaña **Code** → elige la carpeta del repositorio. (Alternativa: abre PowerShell en la carpeta y escribe `claude`.)
5. Pega este mensaje:

---
Lee `CLAUDE.md` y ejecuta las cuatro pruebas en este computador, en el orden indicado. Trabaja con la base de pruebas (`patitas_pruebas`), guarda cada salida real en `evidencias\registros\` y no modifiques el código del proyecto salvo el cambio temporal de rendimiento, que debes revertir. No inventes ni ajustes ningún resultado: si algo falla, documenta el error tal cual. Para la interfaz, guíame caso por caso con `evidencias\LISTA_INTERFAZ.md` y dime qué debo mirar. Al final genera `evidencias\RESUMEN_EJECUCION.md`.
---

6. Cuando termine, sube a Claude (en este chat) `RESUMEN_EJECUCION.md` y la carpeta `evidencias\registros\` comprimida,
   y actualizo el informe a la versión 2.0 con sus cifras reales.
