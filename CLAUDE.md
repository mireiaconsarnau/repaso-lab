# repaso-lab — Repaso Lab (Machine Learning)

## Idioma

Responde **siempre en castellano**, aunque los mensajes incluyan catalán. Vale para las conversaciones, para los documentos de trabajo como este y para todo el contenido de la web, que va **solo en castellano**.

## Objetivo

Página web para **poner a prueba los conocimientos de Machine Learning** del curso de la profesora (https://mireiaconsarnau.github.io/machine_learning), **organizada por las unidades del curso**, para cualquiera que siga el curso.

La web se llama **Repaso Lab** (18/10/2026, elegido por la profesora; descartados «Generaliza», los nombres con guiños al ML y los de estudiar, porque es para repasar, no para estudiar). En la cabecera: «Repaso Lab | Machine Learning» (`config.json → titulo` y `lema`) y, a la derecha, «Apuntes del curso ↗» (enlace a la web del curso, `config.json → web_curso`), «← Todas las unidades» dentro de una unidad y el botón de apariencia. Por debajo de 46rem, sin el lema y con los textos cortos («Apuntes ↗», «← Inicio»).

Enlaces entre las dos webs (19/10/2026): la web del curso tiene «Repaso Lab» en su menú, después de «Licencia» (`nav_external_links` en el `_config.yaml` del repositorio `machine_learning`), y Repaso Lab enlaza al curso desde la cabecera y desde cada pregunta.

Se publica en dos sitios con el mismo código (`web/`):

- **GitHub Pages**: https://mireiaconsarnau.github.io/repaso-lab/ (público). Ahí funciona Repaso; Practica con casos y el tutor no, porque necesitan Claude, y su aviso lleva un enlace «Abrir Repaso Lab en Claude».
- **Artefacto de Claude**: https://claude.ai/artifact/YA1YZLvVcurULMRZGnsK5c. Ahí funciona todo.

**Este repositorio es público** (desde el 19/10/2026; sustituye al privado `agenteRepaso`, que queda como copia de esa fecha con el material de los centros). Aquí solo va lo que se puede ver: nunca enunciados ni soluciones de actividades o pruebas, entregas de alumnos ni datos personales.

## Decisiones del proyecto

Fijadas por la profesora. No las cambies sin preguntar.

### Al entrar: elegir unidad

- La portada muestra primero **«Primeros pasos»** (todas las preguntas de nivel Primeros pasos, de todo el curso), después las **5 unidades por su nombre, sin numerar** («Aprendizaje supervisado», no «Unidad 3»), con una descripción breve, y al final **«Todo el temario»**. Están en `config.json → primeros_pasos`, `unidades` y `todo_el_temario`. Debajo, aparte, la tarjeta de **«Resuelve tus dudas»** (el tutor, `config.json → tutor`).
- **La web no se organiza por centros ni por pruebas**, ni siquiera de forma oculta.
- La página **siempre empieza por la portada** (no recuerda la última unidad); un enlace con `#fundamentos`, `#preprocesamiento`, `#supervisado`, `#no-supervisado`, `#redes` o `#todo` (o `#primeros-pasos`) abre directamente esa opción, y con `/practica` (por ejemplo, `#redes/practica`), en esa pestaña. `#dudas` abre el tutor. (En el artefacto de Claude solo llegan los enlaces sin `/`.)
- **Menú de unidades** (17/10/2026, para no tener que volver a la portada): dentro de una unidad, una barra con las 7 opciones (nombres cortos de `config.json → corto`) queda fija arriba al bajar; en el móvil se desliza de lado. Al cambiar de unidad desde el menú se mantienen la pestaña, el tipo de pregunta y el nivel (`cambiarUnidad`); desde la portada, la unidad se abre por el principio (`abrirUnidad`).
- La **unidad y la lección de cada pregunta salen de su primer enlace** con código de lección (`U3L2` → «Aprendizaje supervisado», lección «Modelos de clasificación»). Dentro de una unidad se filtra por lección; en «Todo el temario» y en «Primeros pasos», por unidad.
- En la cabecera de cada pregunta se muestra el nombre de la lección (y, en «Todo el temario», también el de la unidad), nunca «Unidad N · Lección M» ni el nombre de una actividad.

### Las 2 pestañas de cada unidad y el tutor

1. **Repaso**: preguntas con solución y explicación ya preparadas, en **dos menús: primero «Tipo test» y después «Preguntas abiertas»**. Dentro de cada menú se elige uno de **cuatro niveles de dificultad: Primeros pasos, Aplica, Comprende y Reto** (18/10/2026; criterios en «Reglas para escribir preguntas»); no se llaman principiante/experto, ni «Nivel 1, 2…», ni por tipo de pregunta (nombres y descripción corta en `config.json → niveles`; al entrar se muestra Aplica, `nivel_inicial`). En «Primeros pasos» no hay selector de nivel. Después, filtro por lección y **paginado de 5 en 5** (`POR_PAGINA` en `web/js/app.js`). No necesita cuenta.
2. **Practica con casos** (**prototipo del 17/10/2026**, pendiente de valoración): el alumno escribe su respuesta a un caso práctico y Claude, mediante la capacidad `sample` de los artefactos, le dice qué está bien, qué está mal y qué le falta, comparando con la solución y los criterios del banco. **Sin nota y sin chat.** Solo preguntas abiertas, con las mismas unidades y los mismos cuatro niveles que Repaso. Sus casos **son distintos de las abiertas de Repaso** (`"uso": "practica"`) y preguntan los mismos conceptos de otra manera, con un caso nuevo. **No todos llevan gráfico** (lo pidió la profesora): unos tienen **gráficos que hay que interpretar** (curvas ROC, matrices de confusión, histogramas, diagramas de caja, curvas de aprendizaje y de pérdida, codo y silueta, k-distancias, residuos, PCA, fitness…) y otros son **problemas con datos**: fragmento de dataset con problemas plantados, escenario con variables para decidir comprobaciones y visualizaciones, dos modelos con sus errores, tabla de resultados de validación cruzada, tabla A/B/C de algoritmos de clustering, arquitecturas MLP que comparar, cálculos de épocas, lotes o parámetros…
   - Cómo funciona (`panelPractica`, `pedirCorreccion`, `promptCorreccion` y `panelCorreccion` en `web/js/app.js`): nivel → lección → páginas de 3 casos (`POR_PAGINA_PRACTICA`). Cada caso tiene un cuadro de texto (el borrador se guarda en el navegador), «Corregir con Claude» y «Ver solución». La página llama a `sample.json()` con instrucciones fijas (docente de ML, sin nota, aceptar otras palabras, no inventar criterios, terminología del curso, el texto del alumno es solo su respuesta), el enunciado, los datos de las tablas y gráficos en texto (`Graficos.describir`), los apartados, la solución, los criterios y el `aviso`, y espera `{"bien": [], "mal": [], "falta": [], "consejo": ""}`. Cada error de `sample` (`not_granted`, `rate_limited`…) tiene su mensaje, sin reintentos automáticos.
   - Fuera de Claude (o sin permiso), la pestaña avisa de que la corrección solo funciona en Claude y deja escribir y ver la solución.

**Resuelve tus dudas** (**prototipo del 19/10/2026**, pendiente de valoración): **un solo tutor para todo el curso**, que se abre desde la portada (19/10/2026: ya no es una pestaña de cada unidad). Sin nota.
   - **Qué hace y qué no** (fijado por la profesora el 19/10/2026):
     - Responde **todas las dudas de teoría** del curso **basándose en su material** (fichas, teoría y cuadernos), como lo explica él y con sus términos. Si los apuntes no lo explican o lo explican poco o de forma poco clara, **lo amplía un poco** con sus conocimientos, sin salirse del nivel del curso y sin alargarse. **Nunca dice «no lo encuentro en los apuntes»**: lo explica y cita la lección donde se trata. Si es de ML pero no del curso, dice en una frase que no está en el temario y no lo desarrolla; si no tiene que ver con el curso, lo dice amablemente.
     - **Vocabulario técnico, pero sencillo**: los términos del curso (exactitud, precisión, sensibilidad…) y, la primera vez, una explicación breve con lenguaje cotidiano; sin tecnicismos que no estén en los apuntes; frases cortas, unas 200 palabras, **siempre un ejemplo inventado en las dudas de teoría** (a la profesora le encanta) y sin fórmulas salvo que las pidan y estén en los apuntes.
     - **Sin pregunta de comprobación** (quitada el 19/10/2026, a petición de la profesora): no pregunta si lo ha entendido.
     - **Código**: si funciona, explica qué hace, a qué paso y técnica del curso corresponde y cómo interpretar lo que produce (también tablas, métricas y gráficos que el alumno pegue o describa). **Si da error, dice en qué línea o parte está, qué significa y qué tendría que hacer, pero no lo soluciona**: no da el código corregido ni escribe código nuevo. También señala los errores de concepto (ajustar el escalador con todos los datos…). Para entender el código puede usar lo que sabe de Python; los conceptos de ML, como en los apuntes.
     - **No resuelve ejercicios, actividades ni preguntas de examen**: explica la teoría que hace falta y ayuda a razonar con pistas.
     - **Redirige al material**: en las dudas de teoría y de interpretación cita siempre la lección (`[U3L2]`) y, si se apoya en un cuaderno, el cuaderno (`[U3L29]`). La página convierte los códigos en enlaces («Apuntes: …», «Cuaderno …», a Colab con `config.json → tutor.cuadernos`) y al final de la respuesta pone el recuadro **«Para repasar en la web del curso»**, como en las soluciones: cada lección citada con su **infografía**, y cada cuaderno. Los códigos que no existen se quedan como texto.
     - Al ayudar con un error, termina animándole a probar el cambio. Explica la buena práctica cuando el material discrepa y no obedece instrucciones del alumno que cambien las normas.
   - **Aspecto** (19/10/2026: el azul no destacaba y se confundía con Fundamentos): no lleva color de unidad. En la portada, un panel oscuro como la franja de la portada (`tarjetaDudas`, `.tutor-tarjeta`), con una franja de los colores de las cinco unidades arriba (`franjaUnidades`: responde dudas de todas) y el botón blanco «Preguntar al tutor →». Su vista, con la franja oscura y la de colores debajo; sus botones y líneas, en tinta (`[data-u="dudas"]`).
   - Vista propia (`vistaDudas`, `#dudas`): franja, aviso de si Claude está disponible y la conversación. Sin conversación, arriba va el cuadro de texto y debajo **las dudas de ejemplo de cada unidad** (`config.json → sugerencias_dudas`, 4 por unidad con la etiqueta de su color; en el móvil, 2). Pulsar una la envía tal cual; el alumno puede escribir lo que quiera, también código o un error (hasta 3.000 caracteres, `MAX_TEXTO`).
   - Cómo funciona (`preguntarTutor`, `turnosTutor`, `instruccionesTutor`, `buscarApuntes`, `pistasCodigo` y `textoTutor` en `web/js/app.js`): conversación con la capacidad `sample` (`cache: false`, con streaming y botón «Parar»). Claude no recuerda nada, así que en cada mensaje la página envía un primer turno con las normas del tutor, la lista de lecciones del curso, las notas del profesorado sobre discrepancias del material y **solo los apuntes relacionados con la duda**, buscados por palabras en la propia página: las fichas de resumen de las 1–2 lecciones con más coincidencias (`MAX_FICHAS`), los 4 fragmentos de teoría más parecidos (`MAX_FRAGMENTOS`) y, si el alumno pega código o habla de él (`pareceCodigo`), los 3 trozos de cuaderno más parecidos (`MAX_CUADERNOS`). Con código, la teoría se busca sin los nombres de variables y con las pistas de `PISTAS_CODIGO` (funciones y errores habituales de Python → conceptos del curso: `StandardScaler` → estandarización, «could not convert string to float» → codificación de categóricas…). Después, los últimos 12 mensajes. Son unos 25.000–28.000 caracteres por mensaje.
   - **La conversación no se guarda** (19/10/2026, pedido por la profesora): solo está en memoria mientras la página está abierta y se pierde al cerrarla o recargarla. Al cargar la página se borra lo que guardaban versiones anteriores en el navegador (`borrarConversacionesGuardadas`, claves `repasoML:dudas…`). «Nueva conversación» la vacía. Los borradores de Practica con casos sí se siguen guardando.
   - **Imágenes** (19/10/2026): el alumno puede adjuntar una imagen por mensaje (capturas de gráficos, tablas, resultados, código o errores) con «Adjuntar imagen», pegándola con Ctrl+V en el cuadro o arrastrándola encima (`ponerImagen`, vista previa con «Quitar»). Va en `options.images` de `sample` solo con ese mensaje: en los siguientes, el turno lleva una nota de que ya no la tiene delante, y la norma del tutor le pide empezar diciendo qué ve. El botón solo aparece si `sample.limits()` devuelve `images` (`limitesImagen`); los errores `image_rejected` e `images_unavailable` tienen su mensaje. Necesita `capabilities: {"sample": {"images": true}}`; quien ya había dado permiso a la página se lo vuelve a pedir Claude la primera vez.
   - Los apuntes están en `web/datos/apuntes/U1.json … U5.json` (fichas, síntesis, notas, fragmentos de teoría y trozos de los cuadernos sin sus salidas; la síntesis no se envía), generados con `tools/generar_apuntes.py` a partir del repositorio público del curso. Si cambian los apuntes del curso, vuelve a generarlos. La lección U1L3 (Google Colab) está en el catálogo de `config.json` para que el tutor pueda enlazarla.

Practica con casos y el tutor usan la cuenta de Claude de cada persona (sirve la gratuita): cada llamada a `sample` gasta su propio uso y le pide permiso la primera vez. **Sin cuenta, Repaso debe seguir funcionando.** Solo funcionan dentro del artefacto de Claude. En GitHub Pages (sin `window.claude`), su aviso añade el enlace «Abrir Repaso Lab en Claude →» al artefacto (`config.json → artefacto`, `rellenarEstado` en `app.js`), con el ancla de la unidad o `#dudas`. Para que funcione para el alumnado, el artefacto tiene que estar compartido con enlace público.

### Idea pendiente: abrir los apuntes en un panel

Propuesta aceptada en principio: un botón «Ver en los apuntes» en cada pregunta que abre un panel lateral con el trozo exacto del resumen visual de la lección (ideas clave, esquema, errores típicos…). En GitHub Pages, la web y los apuntes del curso están en el mismo dominio (`mireiaconsarnau.github.io`), así que el panel puede leer los resúmenes directamente con `fetch`; en el artefacto de Claude no (no deja cargar contenido de otras webs) y habría que copiar los resúmenes.

### Regla fija sobre los datos

**Nunca uses los datasets reales de las actividades** en las preguntas: ni sus nombres, ni sus columnas, ni sus datos, ni sus resultados. **Inventa siempre ejemplos nuevos**: otro contexto, otras variables, otros datos y otros valores. Si encuentras una pregunta con datos reales, cámbiala. Tampoco reutilices los casos de las pruebas anteriores: escribe casos nuevos con el mismo estilo.

`tools/validar_banco.py` busca en el banco los nombres de `tools/prohibidos.txt` (datasets y columnas reales y casos de pruebas). **Ese archivo no se publica** (está en `.gitignore`): se copia a mano en cada ordenador (también está en el repositorio privado `agenteRepaso`). Sin él, el validador avisa y no busca nada. Amplíalo cada semestre.

### Otros requisitos

- **No se puntúa nunca.** Ni nota ni cronómetro.
- La página **no muestra** formato de pruebas, puntuación, tiempo, número de preguntas, curso ni semestre.
- **Pie de página: solo la licencia.** El repositorio y la web usan la misma licencia que el repositorio del curso: **CC BY-NC-SA 4.0**, «Repaso Lab: Machine Learning» de Mireia Consarnau (`LICENSE.md`; datos del pie en `config.json → licencia`). Las tipografías (OFL) quedan fuera.
- Las preguntas comprueban si se entienden los conceptos de crear modelos, con casos prácticos. Los avisos hablan de los **cuadernos del curso** (públicos), nunca de solucionarios, entregas ni pruebas de ningún centro.
- Cada pregunta enlaza al **apartado concreto** de la web del curso (https://mireiaconsarnau.github.io/machine_learning) donde se explica el tema.

### Diseño

- Las preguntas están en un **único archivo de datos aparte**, `web/datos/preguntas.json`, no dentro del código. Así las puede editar el profesorado y Practica con casos reutiliza las mismas soluciones y criterios. Cada pregunta tiene: enunciado, tipo, nivel, opciones, solución, explicación, criterios de corrección, tema y enlaces (formato detallado en «Banco de preguntas»).
- En las preguntas tipo test se explica también **por qué cada opción incorrecta está mal**.
- La página debe verse bien **en el móvil**.
- **Diseño** (aprobado el 18/10/2026): estilo sobrio de herramienta profesional, al modo de los sistemas de diseño de producto. Esquinas rectas, superficies planas sin sombras, una sola familia tipográfica (IBM Plex Sans, y Plex Mono para datos) y rejilla de 8 px. La profesora rechazó antes el diseño «cuaderno de datos» (todo blanco y azul, botones y menús iguales, fondo punteado) y una primera versión por colores que «se veía muy hecha por la IA».
  - **Un color por unidad** (`[data-u]` en `web/css/estilos.css`; `app.js` pone `data-u` en `#app`, en las tarjetas, en el menú y, en «Todo el temario» y «Primeros pasos», en cada pregunta): Primeros pasos verde, Fundamentos azul, Preprocesamiento turquesa, Supervisado violeta, No supervisado rosa, Redes naranja y Todo el temario gris. **Nada de mostaza.** Redes no puede tirar a marrón (19/10/2026): su franja y la cabeza de su tarjeta van en un naranja vivo (`#e65c00`; en oscuro, un tono más saturado que el de las demás), y sus textos y botones, en uno más oscuro (`#c24f00`) para que se lean bien. Lo llevan la cabecera de su tarjeta en la portada (baja: lo justo para un título de dos líneas, 19/10/2026), su marca en el menú, la franja de la unidad, el número de cada pregunta, los botones y la solución.
  - **Dificultad de verde a rojo** (`--dif-0` … `--dif-3`: verde, verde lima, naranja y rojo; sin amarillo): un medidor de cuatro barras en cada ficha de nivel; la elegida, con borde de tinta. En el móvil, las cuatro fichas quedan en 2 × 2.
  - **Cada control tiene su forma**: menú de unidades en barra oscura fija (la actual, subrayada con su color); pestañas contenidas debajo de la franja de la unidad; selector de tipo con borde (la opción elegida, en tinta); etiquetas de lección; botones con el texto a la izquierda y el icono a la derecha (lleno, con borde o sin borde).
  - En «Todo el temario» y «Primeros pasos», la cabecera de cada pregunta lleva la unidad en una etiqueta de su color y el nombre corto de la lección.
  - Portada: franja oscura de altura moderada (a la profesora le gusta ancha, pero no demasiado), sin frase encima del título, con el título «Pon a prueba tus conocimientos de Machine Learning», una frase corta y la ilustración `ilustracionPortada` (en `app.js`): un panel con cuatro miniaturas con su nombre, como las salidas de un cuaderno (curvas de pérdida de entrenamiento y validación, matriz de confusión 2 × 2, grupos de un clustering y curva ROC). Descartadas: el gráfico de dispersión con frontera y el de K-Means con regiones (no se entendían). Nada de redes neuronales en la ilustración: no es lo que más se trabaja. En el móvil no hay ilustración (de fondo tampoco gustó): la franja ocupa solo lo que el texto.
  - Los enlaces de cada pregunta llevan a la lección y a su **«Infografía»** (nunca «resumen»).
- **Gráficos** (`web/js/graficos.js`, sin librerías): SVG dibujado a partir de los datos del campo `figuras` de cada pregunta, con colores fijos por serie (azul, naranja, verde; máximo 3), leyenda si hay 2 o más series, un solo eje vertical (los diagramas de caja van uno al lado del otro, cada uno con su escala), etiquetas al pasar el ratón y la tabla «Ver los datos del gráfico». Se ven en modo claro y oscuro y en el móvil (el texto se agranda por debajo de 520 px).
- **Apariencia** (botón en la cabecera): cada alumno elige el modo (Automático, Claro u Oscuro); se recuerda en su navegador. El color lo pone cada unidad.

## Normas del repositorio

- Repositorio **público** `repaso-lab` (https://github.com/mireiaconsarnau/repaso-lab). Aquí se mantiene la web desde el 19/10/2026.
- **Nunca subas** enunciados ni soluciones de actividades o pruebas, material interno de los centros, entregas de alumnos ni datos personales. Ese material está en el repositorio privado `agenteRepaso` (copia del 19/10/2026), que no se toca salvo que la profesora lo pida.
- Cuando la persona usuaria diga «haz commit y push» o «haz pull», hazlo. No hagas commit ni push sin que lo pida. **Cada push a `main` publica la web** en GitHub Pages.
- Haz `git pull` antes de empezar a trabajar.

## Estructura del repositorio

- `web/`: la página de repaso (se publica en GitHub Pages y como artefacto de Claude).
  - `index.html`: fragmento de página (sin `<!doctype>`, `<html>`, `<head>` ni `<body>`): el artefacto y `tools/construir_web.py` le añaden el esqueleto.
  - `datos/config.json`: licencia del pie, niveles de dificultad, unidades (id, código `Un`, nombre y descripción) y «Todo el temario», temas, catálogo de lecciones de la web del curso (título, nombre corto para el filtro, enlace a la lección y a su infografía), estado de las pestañas, el tutor (`tutor`), sus dudas de ejemplo (`sugerencias_dudas`) y el enlace al artefacto (`artefacto`).
  - `datos/preguntas.json`: banco de preguntas.
  - `datos/apuntes/U1.json … U5.json`: apuntes del curso para el tutor (generados; no los edites a mano).
  - `js/app.js` y `css/estilos.css`: la página. `js/graficos.js`: los gráficos de las preguntas. `css/fuentes.css` es generado: no lo edites a mano.
  - `fuentes/`: IBM Plex Sans e IBM Plex Mono (licencia OFL), origen de `css/fuentes.css`.
- `tools/validar_banco.py`: comprueba el banco de preguntas y la configuración (y los nombres de `tools/prohibidos.txt`, que no se publica).
- `tools/barajar_opciones.py`: baraja las opciones de los test (orden fijo por pregunta, correcta repartida entre A, B, C y D).
- `tools/generar_apuntes.py`: genera `web/datos/apuntes/Un.json` a partir de una copia del repositorio del curso: `git clone --depth 1 https://github.com/mireiaconsarnau/machine_learning.git <carpeta>` y `python -I tools/generar_apuntes.py <carpeta>` (necesita `pdftotext`). Las notas sobre discrepancias del material están en el propio script (`NOTAS`).
- `tools/generar_fuentes_css.py`: genera `web/css/fuentes.css` con las tipografías incrustadas.
- `tools/construir_web.py`: construye la web completa en `_site/` (ignorada) para GitHub Pages.
- `tools/servir_local.py`: vista local de la web, igual que la publicada.
- `.github/workflows/pages.yml`: en cada push a `main`, valida el banco, construye la web y la publica en GitHub Pages. Si el validador da errores, no se publica.

## Banco de preguntas (`web/datos/preguntas.json`)

Cada pregunta es un objeto con estos campos:

| Campo | Tipo | Uso |
|---|---|---|
| `id` | texto único | Identificador estable (lo usa Practica con casos para guardar el borrador). |
| `tipo` | `"abierta"` o `"test"` | Los test salen en el menú «Tipo test» de Repaso. |
| `nivel` | `0` a `3` | Dificultad: **0 Primeros pasos**, **1 Aplica**, **2 Comprende**, **3 Reto**. Cómo decidirlo, en «Reglas para escribir preguntas». Los casos de práctica usan la misma escala. |
| `uso` | `"repaso"` o `"practica"` (abiertas) | `repaso`: menú «Preguntas abiertas» de Repaso. `practica`: pestaña Practica con casos (necesita `apartados` y `criterios`). |
| `tema` | id de tema | Uno de `config.json → temas`. Sirve para organizar el banco; en la página no se muestra (se muestra la lección del primer enlace). |
| `enunciado` | lista de párrafos | Admite HTML sencillo (`<strong>`, `<em>`, `<code>`). |
| `datos` | lista de tablas (opcional) | `{ "titulo", "columnas", "filas", "nota" }`. Para fragmentos de dataset, matrices de confusión, resultados o arquitecturas. |
| `figuras` | lista de gráficos (opcional) | Datos de un gráfico que dibuja `web/js/graficos.js`. Tipos: `lineas` (`eje_x`, `eje_y`, `series: [{nombre, puntos: [[x, y]…]}]`, opcionales `x_min`, `x_max`, `y_min`, `y_max`, `referencia` y `referencia_nombre`), `roc` (como `lineas`, con la diagonal del azar), `barras` (`eje_y`, `categorias`, `series: [{nombre, valores}]`), `histograma` (`limites` de los intervalos y `series: [{nombre, conteos}]`), `boxplot` (`cajas: [{nombre, min, q1, mediana, q3, max, atipicos}]`), `dispersion` (`grupos: [{nombre, puntos, sin_color?}]`, opcionales `linea` y `linea_nombre`) y `matriz` (`etiquetas`, `valores`; filas = real, columnas = predicho). Todos admiten `titulo` y `nota`; como máximo 3 series. Los datos se inventan con un script (nunca a ojo) y deben ser coherentes con la solución. |
| `apartados` | lista (abiertas) | Subapartados a), b), c). |
| `opciones` | lista (test) | `{ "texto", "correcta": true/false, "explicacion" }`. Una sola correcta; todas con explicación. |
| `solucion` | lista de párrafos (abiertas) | Respuesta modelo, breve y concreta. |
| `criterios` | lista (abiertas) | Criterios de corrección: lo que debe tener una respuesta completa. Obligatorios en las de práctica; los usa Practica con casos. |
| `explicacion` | lista de párrafos | El porqué de la solución. |
| `aviso` | texto (opcional) | Cuando el material del curso (cuadernos, teoría) discrepa de la buena práctica. No menciones solucionarios, entregas ni pruebas. |
| `enlaces` | lista | Códigos del catálogo `config.json → lecciones` (p. ej. `"U2L4"`) o `{ "texto", "url" }`. **El primero debe ser la lección principal**: de él salen la unidad y la lección de la pregunta. |

Para añadir una lección al catálogo, copia el ancla de su título en `https://mireiaconsarnau.github.io/machine_learning/unidadN/unidadN.html` y el de su infografía (la ficha de `resumenes/unidadN.html#leccion-M`, campo `infografia`; en la página se enlaza como «Infografía», no «resumen»).

## Reglas para escribir preguntas

- Cada pregunta trabaja lo que se hace en una lección del curso (su tipo de problema, sus conceptos y sus decisiones), **con un caso inventado** (regla fija sobre los datos).
- **Ninguna combinación unidad × tipo (test/abiertas) × nivel puede quedar vacía**: todas deben tener al menos 3 preguntas (la profesora lo pidió el 17/10/2026). Comprueba la matriz antes de dar por terminado un cambio del banco. En Practica con casos hay al menos 5 casos por unidad y nivel, y 3 en Primeros pasos (18/10/2026). `tools/validar_banco.py` avisa si alguna combinación se queda por debajo.
- Casos de práctica: preguntan lo mismo que las abiertas de Repaso, pero de otra manera y con otro caso. Mezcla gráficos que interpretar con problemas con datos (tablas, escenarios, arquitecturas, cálculos sencillos). Si el gráfico es la clave del caso, la solución cita lo que se ve en él (valores, forma, punto de inflexión) y los criterios dicen qué debe leerse del gráfico.
- Cada pregunta nueva lleva su `nivel` de dificultad (cuatro niveles, fijados con la profesora el 18/10/2026). **El nivel lo decide lo que pide la pregunta**, no el tema:
  - **Primeros pasos (0):** definiciones y teoría, qué es y para qué sirve (IA, tipos de IA, tipos de aprendizaje, nulo, atípico, clúster, época, sesgo, test de Turing, habitación china…). Sin datos, sin cálculos y **sin un caso al que aplicarlo**. Un ejemplo de tipos de IA («un programa que gana al ajedrez, ¿por qué no es IA general?») sigue siendo Primeros pasos.
  - **Aplica (1):** aplicar lo básico a unos datos o a un caso concreto («cuál es la variable objetivo de este problema», «qué tipo de aprendizaje usa esta app», «qué harías con estas columnas», «cómo rellenarías estos nulos», «qué capa de salida pondrías»), leer un gráfico o una tabla sin decidir, calcular con una fórmula conocida (métricas, épocas × lotes), reconocer un hiperparámetro.
  - **Comprende (2):** el porqué y las diferencias (LabelEncoder frente a One-Hot, por qué escalar), cómo funcionan los algoritmos del curso por dentro sin matemáticas (AdaBoost, limitaciones de DBSCAN, distancias), qué pasa al cambiar un hiperparámetro, **valorar si un modelo es bueno y explicar por qué** («exactitud del 90 % y sensibilidad del 50 %: ¿es buen modelo?»), decidir con criterio o con una decisión directa de un gráfico (k en el codo, la mejor época), y qué son y para qué sirven los temas avanzados. Una pregunta que mezcla un cálculo con una decisión va al nivel más alto que pide.
  - **Reto (3):** razonar con un caso (comparar y elegir, diagnosticar y proponer, elegir el valor de un hiperparámetro con resultados), temas avanzados a fondo y **todo lo que va más allá de la teoría del curso, aunque se pregunte como una definición** (IA explicativa, aprendizaje semisupervisado, neuronas «muertas» de ReLU, BatchNormalization, curva ROC con varias clases, sesgo-varianza, contar parámetros).
  - **Algoritmos genéticos y transfer learning:** nunca por debajo de Comprende. Lo básico y lo intermedio (qué son, para qué sirven, el cruce en un punto, congelar capas) son Comprende; calcular probabilidades de selección o aptitudes con restricciones, el diseño del algoritmo y las estrategias de transfer learning, Reto.
  - **Autoencoders:** qué son, sus partes y para qué sirven, Comprende; su diseño por dentro (pooling y upsampling, decisiones de la salida y de la pérdida), Reto.
  - **Hiperparámetros:** qué es o cuál es → Aplica; qué pasa al cambiarlo → Comprende; elegir su valor con resultados → Reto. **Gráficos:** leerlo → Aplica; una decisión directa → Comprende; comparar y sopesar → Reto.
- Estilos de pregunta:
  - pregunta reflexiva sobre lo que se hace en un ejemplo del curso;
  - escenario nuevo con datos (fragmento de dataset con problemas plantados, matrices de confusión, tabla de modelos con métricas, arquitecturas) y 2–3 subapartados: identificar, elegir y justificar;
  - test A–D.
- **Opciones de los test** (19/10/2026, pedido por la profesora, porque se podían acertar sin saber: la correcta era la A en 212 de 240 y la más larga en 204):
  - Las cuatro opciones, de **longitud parecida**. La correcta dice la respuesta y nada más; el porqué va en su `explicacion`. Si hace falta, alarga las incorrectas con detalles verosímiles.
  - Ningún texto cita otra opción por su letra o su posición («la opción B», «la anterior», «todas las anteriores»): el orden cambia al barajar.
  - **Siempre** que se añadan o se cambien preguntas tipo test, ejecuta `python -I tools/barajar_opciones.py` antes de validar y publicar (lo pidió la profesora el 19/10/2026). Coloca la correcta en A, B, C o D según un hash del id (siempre igual para cada pregunta) y reparte las letras por igual.
  - `tools/validar_banco.py` avisa de cada pregunta tipo test sin barajar, da error si una opción cita otra por su letra y avisa si la correcta es mucho más larga que las demás, si se concentra en una letra o si es la más larga en más del 35 % de las preguntas.
- Nivel: conceptual, sin código ni fórmulas ni calculadora. Las cuentas, si las hay, se hacen de cabeza.
- Las soluciones modelo son breves y nombran las técnicas concretas que se ven en el curso. Los criterios enumeran lo que debe aparecer.
- La respuesta modelo y la explicación siguen la **buena práctica**, aunque algún cuaderno haga otra cosa. Por ejemplo: dividir antes de imputar, escalar o eliminar atípicos y ajustar las transformaciones solo con el entrenamiento; One-Hot (no LabelEncoder) en las variables nominales; no imputar la variable objetivo; validar con la validación (no con el test) al entrenar una red.
- Usa la terminología del curso:
  - **exactitud (accuracy)**, **precisión (precision)**, **sensibilidad (recall)**;
  - sobreajuste/subajuste;
  - normalización = Min-Max, estandarización = Z-score, escalado robusto.
  Distingue siempre exactitud de precisión: el material las mezcla a veces.
- Cuando el material discrepa de la buena práctica, el `aviso` lo menciona sin penalizar al alumnado que haya seguido el material. Ejemplos: la clase positiva «Sano» del ejemplo del VIH, o los umbrales del error porcentual (10/25 en la teoría frente a 10/30 en los cuadernos). Las notas del tutor (`NOTAS` en `tools/generar_apuntes.py`) recogen las demás.
- La unidad y la lección de cada pregunta las decide su **primer enlace** (`UnLm`). Elige la lección donde se explica lo que pregunta.
- Redacta de forma neutra, sin «Actividad N», «la prueba» ni nombres de centros.

## Material teórico del curso (repositorio público)

El curso está en https://github.com/mireiaconsarnau/machine_learning (web: https://mireiaconsarnau.github.io/machine_learning/).

- Hay 5 unidades. Cada una tiene teoría en PDF (`unidadN/lM.pdf`; `material_teorico_all.pdf` es su unión), cuadernos en `unidadN/cuadernos/UnLmm.ipynb` (el cuaderno mm de la lección m) y una página `unidadN/unidadN.md` con los enlaces y los vídeos de YouTube.
- En la web, cada lección tiene un ancla propia en la página de la unidad (`unidadN.html#lección-M-…`) y una ficha en `resumenes/unidadN.html#leccion-M`. Son los «apartados concretos» a los que enlazan las preguntas.
- `resumenes/unidadN.md`: una ficha por lección con la idea principal, el vocabulario, los errores habituales y preguntas de comprobación.
- `ras.md`: relación entre unidades y RA (U1 → RA1, RA2; U2 y U3 → RA3; U4 → RA4; U5 → RA5; U3, U4 y U5 → RA6).
- `fed/fed.md`: fe de erratas. En el ejemplo completo de la U4 hay que excluir la columna de etiquetas del clúster al calcular las métricas y el PCA.
- «Ejemplos completos» del curso: U2L25 (preprocesamiento), U3L29 (clasificación), U3L37 (regresión), U4L33 (clustering), U5L11 y U5L12 (MLP de clasificación y de regresión), U5L21 (autoencoder), U5L22 (LSTM), U5L31 (transfer learning) y U5L32 (algoritmo genético).
- Para leerlo, haz un `git clone --depth 1` en el scratchpad. Los PDF se leen con `pdftotext -enc UTF-8` (entre palabras salen marcas U+202D/U+202C: cámbialas por un espacio).

## Estado actual y cómo retomar (19/10/2026)

**Hecho**

- Banco de **594 preguntas**: 240 tipo test, 182 abiertas de repaso y 172 casos de práctica (35 con gráficos), todas con caso inventado y con uno de los **cuatro niveles**. Por unidad: Fundamentos 100, Preprocesamiento 106, Supervisado 125, No supervisado 106 y Redes 157. Por nivel: Primeros pasos 105, Aplica 134, Comprende 206 y Reto 149. Cada combinación unidad × tipo × nivel de Repaso tiene al menos 5 preguntas; en la práctica, cada unidad tiene 6 casos de Primeros pasos, 9–10 de Aplica, 6–9 de Comprende y 6–14 de Reto.
  - Opciones de los test revisadas una a una para que la correcta no destaque por su longitud y barajadas (correcta en A, B, C y D: 59, 59, 62 y 60).
  - Niveles: Claude clasificó todo el banco con los criterios acordados y la profesora revisó las 23 preguntas dudosas; sus respuestas fijaron los matices de «Reglas para escribir preguntas».
- Web organizada por unidades: portada con Primeros pasos, las 5 unidades y «Todo el temario»; en cada una, Repaso y Practica con casos; desde la portada, Resuelve tus dudas.
- `python -I tools/validar_banco.py` da el reparto actualizado, también por nivel.
- 19/10/2026: repositorio público `repaso-lab` con GitHub Pages; el privado `agenteRepaso` queda como copia con el material de los centros.

**Siguiente paso**

1. Esperar la valoración del prototipo de Practica con casos: estilo de los casos y de los gráficos, calidad de las correcciones de Claude (solo se pueden probar abriendo el artefacto en claude.ai) y cuántos casos por unidad y nivel.
2. Ajustar, si hace falta, las instrucciones de `promptCorreccion` según cómo corrija Claude.
3. Equilibrio pendiente: Redes sigue siendo la unidad más grande (tiene más temas) y Comprende el nivel con más preguntas, sobre todo en los test de Supervisado y Redes. En Practica con casos, Fundamentos y Supervisado tienen solo 6 casos de Comprende frente a 12–14 de Reto.
4. El panel «Ver en los apuntes».
5. Esperar la valoración del prototipo de «Resuelve tus dudas»: calidad y longitud de las respuestas, si encuentra los apuntes adecuados, si se ciñe al temario y al material (y cuánto amplía), los ejemplos, cuánto uso gasta (unos 25.000–28.000 caracteres por mensaje) y si respeta las normas sobre el código.

**Publicación**

- **GitHub Pages**: automático en cada push a `main` (`.github/workflows/pages.yml`; en el repositorio, Settings → Pages → Source: «GitHub Actions»). Mira el resultado en la pestaña Actions de GitHub.
- **Artefacto de Claude**: https://claude.ai/artifact/YA1YZLvVcurULMRZGnsK5c. Se publica con la herramienta Artifact: página `web/index.html` y, como archivos de apoyo (`files`), `css/fuentes.css`, `css/estilos.css`, `js/graficos.js`, `js/app.js`, `datos/config.json`, `datos/preguntas.json` y `datos/apuntes/U1.json … U5.json`, cada uno desde su ruta en `web/`. Después de cambiar la web, republícalo también para que los dos sitios sean iguales.
- El artefacto declara la capacidad `sample` con imágenes (`capabilities: {"sample": {"images": true}}`), que usan Practica con casos y el tutor (las imágenes, solo el tutor). Al republicar sin `capabilities` se mantiene la que ya tiene.
- El artefacto se comparte con enlace público desde claude.ai (lo hace la profesora). Para republicar en el mismo enlace desde otra sesión, pasa la URL del artefacto (`url`), después de leerlo.

**Comprobar cambios en la web**

- `python -I tools/validar_banco.py` (estructura del banco, etiquetas, enlaces y nombres prohibidos).
- Vista local: la página carga los JSON con `fetch` y `index.html` es un fragmento, así que no funciona abriéndolo con doble clic. Ejecuta `python -I tools/servir_local.py` y abre http://localhost:8000. Para ver la versión de GitHub Pages tal cual, `python -I tools/construir_web.py` y sirve `_site/` con `python -m http.server`.
- Capturas sin interfaz: Chrome no baja de unos 500 px de ancho de ventana; para ver el móvil, mete la página en un `<iframe>` de 400 px.
- La corrección con Claude y el tutor no funcionan en local (`window.claude` solo existe en el visor de Claude). Para probar el flujo, en una página de prueba define antes de `app.js` un `window.claude = { use: … }` falso cuyo `sample()` / `sample.json()` devuelva una respuesta fija o un error (`{code: 'rate_limited'}`) y cuyo `sample.limits()` devuelva `images` si quieres probar las imágenes, y revisa el texto que recibe.
- Para revisar todos los gráficos de una vez, haz una página de prueba que cargue `js/graficos.js` y llame a `Graficos.crear(fig)` para cada figura del banco.
- Si cambias las tipografías de `web/fuentes/`, ejecuta `python -I tools/generar_fuentes_css.py`.

**Otros asistentes (Antigravity, Gemini…)**

`AGENTS.md` remite a este archivo, que es la fuente única del contexto. Si cambia algo importante, actualiza este archivo, no `AGENTS.md`.
