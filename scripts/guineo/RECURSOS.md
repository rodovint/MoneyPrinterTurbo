# Guineo Comunicaciones · recursos visuales del generador de reels

Guía para cualquier chat o agente que arme lotes en `lotes/actual.json`.
El generador es `scripts/guineo/generar.py` (lo corre la Action "Generar reels Guineo Comunicaciones").

## Reglas fijas (vienen del doc "Guineo Comunicaciones — Recursos y habilidades para videos")
- **Marca**: siempre "Guineo Comunicaciones" (cabecera, cierre, voz y textos). Nunca "Guineo Deportes".
- **Voz** (decidido por Mui el 15/11): la **voz clonada de Mui** para el gancho, la emoción, la pregunta y el cierre, y **Andrea** (Edge TTS es-EC-AndreaNeural) para los datos duros.
  - `"voz": "mui"`: la genera la Action con Chatterbox Multilingual (MIT, gratis) a partir de `scripts/guineo/voz/mui-ref.wav` (14 s limpios de Mui). Tarda ~40 s por frase; usar 2–3 frases por reel.
  - `"voz": "andrea"` (o `"luis"`): Edge TTS. Si una palabra suena mal, pon en `"dicho"` cómo se pronuncia ("Cies") y deja `"texto"` para el subtítulo.
  - Escenas sin `"voz"`: salen de una grabación real de Mui (`"audio": "audio/NN"`), cortada por pausas y limpiada sola. Solo si Mui manda audios.
  - Si la voz clonada falla, esa frase sale con Andrea (aviso en el log).
  - **Pronunciación obligatoria (corrección de Mui, 17/11)**: toda frase que nombre a **Xavi** (Xavi Hernández) lleva `"dicho"` con **"Chavi"** (Andrea y el clon lo leen "Javi", y está mal). Revisa siempre los nombres extranjeros con X, J, Ll, W, etc. y ponles `"dicho"` antes de generar.
  - **Entonación (regla de Mui, 17/11):** toda frase que cierra (afirmación o exclamación) debe terminar con el **tono hacia abajo**; solo las preguntas suben. `voz_clon.py` hace hasta 6 tomas y descarta las que no bajan al final. Escribe las frases para que cierren con punto (no con "!" ni puntos suspensivos).
  - **Final completo:** la última palabra no se puede cortar (ej. "la vuelta al mundo"). Si en la hoja de contacto o al escuchar se nota cortada, regenera esa frase.
  - Revisa siempre que el final de cada frase clonada se escuche entero y bajando antes de mandar el video a Mui.
- **Primer fotograma**: cara o acción + el texto del gancho, sin fundido (el generador ya pone el texto desde el fotograma 0). La primera frase dice quién hizo qué.
- **Duración**: 25–35 s (5–7 frases cortas). El generador avisa si pasa de 36 s.
- **Las noticias institucionales se cuentan a través de una persona.**
- **Fotos de personas (regla de Mui, 18/11, reemplaza la anterior):** cada reel lleva **fotos reales del protagonista** de la noticia (jugador, DT, figura), no solo dibujos de Cloudflare. Fuente: Wikimedia Commons con licencia libre (CC-BY, CC-BY-SA, CC0 o PD) vía `"foto_commons"` (pone el crédito solo), o fotos que mande Mui. Antes de proponer el guion, busca en Commons la foto de cada protagonista y anota el nombre exacto del archivo en el borrador. **Si no encuentras una foto libre de algún protagonista, avísale a Mui en el mensaje de aprobación (antes de generar) y pídesela.** Nunca fotos de medios, agencias, clubes o transmisiones descargadas por el agente. Estadios y lugares: también Commons.
- **Mezcla de recursos (regla de Mui, 18/11):** usa todos los recursos, no solo dibujos: foto real del protagonista (gancho y escena clave), escudos, gráficos, jugadas `tv`/`retro`, fotos de Commons de estadios, y 1 dibujo de Cloudflare como apoyo (ambiente, objetos).
- **Nada de fotos ni videos de medios, agencias o transmisiones** salvo lo que Mui mande y apruebe (ver regla 4 de "Lecciones de las métricas").
- Mui aprueba los guiones antes de producir y los videos antes de publicar.
- **Las correcciones de Mui son permanentes**: cuando corrija algo (pronunciación, escudos, estilo), anótalo aquí como regla en el mismo commit del arreglo, para que ningún agente lo repita. Antes de generar, repasa esta lista de reglas contra el JSON.

## Efectos automáticos del generador (guineo_fx)
- Transición de entrada en cada escena (barrido amarillo, zoom, glitch, destello), whoosh en cada corte.
- **Franja de noticiero** con el logo y texto corrido: `"franja": ["DATO 1", "DATO 2"]` a nivel de reel (si falta, usa título y etiqueta). No sale en el cierre.
- **Números animados** en las escenas `cifra` (cuentan hacia arriba o rebotan). `"animar": false` en la escena para dejarlo fijo.
- Por escena: `"destello": true` (flash + golpe de bajo en el momento clave), `"suspenso": true` (latido), `"hinchada": true` (hinchada de fondo), `"tono": "recuerdo" | "urgente" | "celebracion"`, `"transicion": "barrido" | "zoom" | "glitch" | "flash" | "rota"`.
- **Música** coral de fondo al 15% (`"musica": false` en el reel para quitarla, `"volumen_musica": 0.1`). Master a −14 LUFS.
- **Cierre** con el logo redondo de Guineo Comunicaciones.
- La Action sube al Release, además del mp4: `contacto-NN.jpg` (hoja de 12 fotogramas para revisar textos, cortes y superposiciones ANTES de mandar el video a Mui) y `portada-NN.jpg` (portada para Metricool, `videoThumbnailUrl`).

## Dibujos automáticos (Cloudflare, ya configurado)
- Escribe `lotes/dibujos/<reel>.json` (formato de `lotes/dibujos/espana-inglaterra.json`: referencia de estilo `scripts/guineo/ref/estilo1.jpg`, 3–4 escenas, prompts en inglés) y haz push: la Action "Dibujos" solo dibuja los JSON nuevos y los publica en un Release `dibujos-...` como `<reel>-<id>.png`.
- Bájalos a `lotes/img/` y úsalos como `"foto": "img/<archivo>.png"` con `"movimiento"`. Revísalos antes (Read): si algo sale mal (p. ej. balón de fútbol americano), corrige el prompt y repite solo ese.
- **Regla de Mui**: ilustraciones de la escena (estadio, hinchas de espaldas, balón, camisetas lisas, objetos), **nunca caras realistas de jugadores reales**, sin escudos, logos ni texto. Cupo gratis: 10.000 neuronas al día, que alcanzan para unos 8 dibujos con "9b" (se renueva a las 19:00 de Ecuador). Repártelo: 2–3 dibujos por reel y solo en los reels más importantes. Si la Action dice que se acabó el cupo, ese reel va con fondos de Pixabay o foto_commons.
- En la descripción: "Ilustraciones generadas con IA".

## Escudos de los equipos
- Están en `lotes/img/escudos/<club>.png` (barcelona, catolica, idv, liga, tecnico, macara, orense, mushuc, aucas, cuenca, manta, delfin, fef). Se usan con `"escudo": "img/escudos/<club>.png"` en cada equipo de `partido`/`marcador`, o con el gráfico `{"tipo": "escudo", "escudo": ..., "sobre": ..., "texto": ...}`.
- Si falta un club: TheSportsDB (`searchteams.php?t=<club>`, campo strBadge) o Wikimedia Commons, bajados desde una Action (este entorno no llega a esas webs).
- Una agenda de fecha va con una tarjeta `partido` por cada partido (todos los partidos, todos con escudo), no en texto chico.
- **Regla permanente (Mui, 17/11): TODO equipo en `partido` o `marcador` lleva escudo, también las selecciones y los rivales extranjeros.** El generador lo busca solo: si el equipo no trae `"escudo"`, usa `img/escudos/<nombre-sin-tildes>.png` (ej. `bolivia.png`, `paises-bajos.png`) y, si ese archivo no existe, lo baja de TheSportsDB durante la Action (`bajar_escudo` en generar.py; nombres en español mapeados en `ESCUDO_EN`). Revisa en la hoja de contacto que salga el escudo correcto; si no salió, súbelo a `lotes/img/escudos/` antes de mandar el video a Mui. **Si falta el escudo de cualquiera de los equipos, la tarjeta sale SIN NINGÚN escudo** (regla de Mui del 17/11, ya está en el generador: `todos_con_escudo`); nunca uno sí y el otro no. TheSportsDB bloquea las descargas automáticas (403): si falta un escudo, pídele a Mui la imagen ANTES de generar, quítale el fondo y guárdala en `lotes/img/escudos/<nombre>.png`. Ya hay: bolivia.

## Créditos (van en la descripción de YouTube)
- Música: "Epic Celestial Choir 2" – Megis (CC BY), Internet Archive.
- Hinchada: "Football-crowd-Cheer+Jeers" – paulw2k vía Freesound (CC BY 4.0).
- Ver `scripts/guineo/audio/LICENSES.csv`.

## Lecciones de las métricas (revisión de Mui, 17/11) — aplicar en TODA producción
Datos: YouTube 13,6 k vistas y +22 suscriptores en 28 días, pero el **61 % desliza** sin quedarse; 13 % de las vistas viene del buscador (casi todo "ravenna vs forli"). Instagram: reels nuevos 100–175 vistas (el mejor histórico 5.770). TikTok: normal 500–900, pero algunos subidos por API quedaron en 6–9.
1. **El primer segundo decide si el usuario se queda (regla de Mui, 18/11).** En el fotograma 0 tienen que estar a la vez: la **foto real del protagonista** (cara reconocible), el **gancho de 3–5 palabras en grande** y la **primera frase fuerte** (quién hizo qué, sin introducción). Si no hay foto del protagonista, pídesela a Mui antes de generar; el dibujo de Cloudflare no va en el gancho si hay foto real. Nada de portadas solo de texto, cifras sueltas o fondo plano ("¡TITULAR!", "0", "3.321 días", pantalla roja de "Última hora" rindieron menos). Los mejores: Ronaldinho, Klopp vs. Xavi, Morales cara a cara.
2. **Temas que ganan:** figuras famosas (Ronaldinho, Messi) y ecuatorianos con un logro concreto (Jordy Caicedo, Enner Valencia, IDV, Alonso Reyes, Pacho), contados como historia. Lo institucional (horarios, aniversarios sin título) rinde poco: contarlo a través de una persona o dejarlo fuera.
3. **Partidos "X vs Y" del día** con el nombre exacto que la gente busca en el título de YouTube (ej. "Ravenna vs Forlì"), publicados mientras se busca.
4. **Imágenes oficiales o de transmisiones (decisión de Mui, 17/11): solo como excepción y solo si Mui las manda ella misma** y dice que las usa. El agente NUNCA las busca ni las descarga. Reglas: máximo 2–3 s por video, solo para ilustrar el momento clave (el resto con pizarra, pixel, retro o tv), sin el audio original, crédito en pantalla y en la descripción ("Imágenes: <fuente>"), y preferir las publicadas por el propio club o federación en sus redes. Avisar a Mui en el mensaje de entrega que ese video lleva material de terceros (puede recibir reclamo de derechos o quedar sin monetizar). Alternativa sin riesgo en TikTok, Instagram y YouTube: usar las funciones de la propia app (Dúo/Stitch, Remix) sobre el video oficial.
5. **Cierres con tono hacia abajo** y última palabra completa (ver Voz).

## Publicación manual (mientras Metricool esté en su límite; después, Metricool solo para emergencias)
El agente entrega cada mp4 + un archivo textos-*.txt con los textos por red y la hora sugerida. Al final del txt agrega SIEMPRE esta lista para Mui:
- **TikTok:** subir desde la app; agregar un sonido en tendencia a volumen muy bajo (5–10 %) bajo la voz; si un video queda con menos de 50 vistas en 2 h, revisar si está "en revisión" o con alcance limitado.
- **Instagram:** subir desde la app como Reel; compartirlo en Historias; invitar como colaborador a una página de hinchas o local de El Oro cuando aplique; poner el "Primer comentario".
- **YouTube:** título con el término exacto que se busca; responder los comentarios en la primera hora (ej. "¿Pero y Emelec?").
- **Las 3 redes:** responder comentarios la primera hora; no publicar dos videos con menos de 60 min de diferencia.

## Publicación (SEO por red: textos para Metricool o para publicar a mano)
- Un post por red (no uno compartido), cada uno con su texto:
  - **YouTube Short**: título con nombres completos ("Independiente del Valle", no "IDV") + el hecho + lo que la gente busca + #Shorts (máx. 90). Descripción: la historia en 3–4 frases con nombres y cifras, la pregunta, "Suscríbete a Guineo Comunicaciones", fuentes, créditos de música/sonido y 10–12 hashtags. Sin primer comentario automático.
  - **Instagram Reel**: gancho en MAYÚSCULAS con emoji, 2–3 líneas, pregunta, créditos y hashtags + #Reels. `firstCommentText` con una pregunta de sí/no o de elegir.
  - **TikTok**: 1–2 líneas, pregunta y hashtags + #fyp.
  - Portada: `videoThumbnailUrl` = portada-NN.jpg del Release.
- Horarios: previa de un partido → YouTube unas 3 h antes (para que se indexe) e Instagram/TikTok en el pico del feed antes del evento; el resto con getBestTimeToPostByNetwork, separados 40 min.

## Fondos e imágenes (por escena)
| Recurso | Campo | Notas |
|---|---|---|
| Foto libre de Wikimedia Commons | `"foto_commons": "Nombre del archivo.jpg"` | Solo licencias CC-BY / CC0 / PD; pone el crédito solo. |
| Foto o dibujo propio | `"foto": "img/archivo.png"` | Ruta relativa a `lotes/`. Fotos que pase Mui o dibujos de Cloudflare. |
| Movimiento de la foto | `"movimiento": "zoom_in"` | `zoom_in` (defecto), `zoom_out`, `paneo_izq`, `paneo_der`, `subir`, `bajar`, `quieto`. |
| Video propio (grabado por Mui o su equipo) | `"video": "videos/clip.mp4"`, `"video_inicio": 3.5` | Se recorta a vertical y se silencia (manda la voz). |
| Fondo de Pixabay | (automático) | Si la escena no tiene foto ni video, usa clips de fútbol teñidos con el color del equipo. |

Si la escena **no lleva `grafico`** (o `"tipo": "ninguno"`), la foto/dibujo/video se ve con brillo completo; ideal para dibujos.

## Gráficos estáticos
`titular`, `cifra`, `marcador`, `cita`, `duo`, `partido`, `protagonista`, `cierre` (ver ejemplos en `lotes/actual.json`).

## Gráficos animados (jugadas) — `scripts/guineo/pizarra.py`
- `"tipo": "pizarra"`: pizarra táctica con tiza, jugadores con dorsal, flechas de pase/conducción/tiro.
- `"tipo": "pixel"`: la misma jugada recreada estilo videojuego retro (sello de Guineo).

```json
{"tipo": "pizarra", "titulo": "ASÍ FUE EL 1-0",
 "local": {"nombre": "ORENSE", "color": "#1E8A4C"}, "rival": {"nombre": "EMELEC", "color": "#0B4EA2"},
 "jugadores": [{"id": "7", "equipo": "local", "x": 15, "y": 55},
               {"id": "9", "equipo": "local", "x": 50, "y": 50},
               {"id": "4", "equipo": "rival", "x": 45, "y": 30},
               {"id": "1", "equipo": "rival", "x": 50, "y": 4, "arquero": true}],
 "balon": "7",
 "pasos": [{"mover": {"7": [22, 35]}, "balon": [22, 35], "flecha": "conduccion", "texto": "CONDUCE"},
           {"mover": {"9": [55, 18]}, "balon": [55, 18], "flecha": "pase", "texto": "CENTRO"},
           {"balon": [46, -2], "flecha": "tiro", "gol": true, "texto": "REMATE CRUZADO"}]}
```
- **Regla de Mui (15/11/2026): las jugadas se grafican SIEMPRE con `retro` o `tv` (el "3D"), con el estadio lleno.** Al proponer el guion, ofrece los dos y Mui elige; si no dice nada, usa `tv`. `pizarra` y `pixel` quedan solo para lotes viejos.
- **Estilos de jugada** (`scripts/guineo/jugadas.py`), mismo formato, con `"tipo": "retro"` o `"tipo": "tv"`:
  - `retro`: videojuego de 16 bits en perspectiva de transmisión, tribuna animada, sprites que corren, balón que se eleva, marcador de consola y ¡GOL! pixelado con confeti.
  - `tv`: gráfico táctico de transmisión, líneas con brillo, fichas con anillo, pases en curva que se dibujan solos, estela del balón.
  - Extras opcionales: `"nombre"` y `"destacado": true` en un jugador (etiqueta y pulso), `"curva"` en un paso, y `"marcador": {"local": "RAV", "rival": "FOR", "antes": [0, 0], "despues": [1, 0], "minuto": "35'"}`. La cámara se acerca sola a la zona de la jugada.
  - **Estadio lleno** (siempre): tribunas detrás del arco y a los lados con hinchas en los colores del local (`"color2"` en `local` para el segundo color), vallas lisas, reflectores, banderas que flamean, flashes y la hinchada que salta (y festeja con el gol). `"ambiente": "lleno"` (por defecto) agrega bengalas con humo; `"ambiente": "normal"` las quita. `"pancarta": "RG10"` pone un cartel en la tribuna lateral (solo textos verificados).
Coordenadas 0–100: `x` izquierda→derecha, `y` desde la línea de gol (0, arriba) hasta la mitad de cancha (100). `y < 0` es dentro del arco. Los pasos se reparten a lo largo de la frase narrada. Describir la jugada solo con lo que cuentan las crónicas verificadas; si no se sabe cómo fue, no inventarla.

## Dibujos con Cloudflare Workers AI
- Action "Dibujos (Cloudflare Workers AI)" + `scripts/guineo/dibujar.py` (FLUX.2 klein). Necesita los secretos `CF_ACCOUNT_ID` y `CF_API_TOKEN`.
- Se pide con un JSON en `lotes/dibujos/<nombre>.json` (referencias de cara y estilo en `scripts/guineo/ref/`). El resultado queda en la rama `dibujos-out`, carpeta `<nombre>/<id>.png`.
- Para usarlos: copiar los PNG a `lotes/img/` y ponerlos como `"foto"` con un `"movimiento"`.

## Pendiente / ideas
- **Escena animada corta (idea de Mui, 18/11; se prueba el sábado 21 con el Súper Resumen, NO usar antes):** recurso extra para los reels de Guineo basado en la habilidad claude-animated-shorts (github.com/mromidev/claude-animated-shorts, MIT; three.js + Remotion, personajes 2D en mundo 3D). Regla: **máximo 5 s por reel**, recreando el momento que se está contando, combinada con los recursos de siempre (gráficos, escudos, dibujos, pizarra). Solo 1 por reel y solo en los reels 🔥 más importantes, para no gastar uso. Reutilizar escenarios y personajes genéricos ya hechos (estadio, hinchas, arquero, delantero) en vez de crear todo de cero. Sin caras realistas de jugadores reales ni escudos dentro de la animación.
- Recreación 3D de jugadas con la animación de El Profe (otro repo): aún no conectada.
