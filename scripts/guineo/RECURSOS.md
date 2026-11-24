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
  - **Velocidad y volumen de la voz real de Mui (correcciones de Mui, 15/11):** si en su grabación hay palabras que no se entienden por la rapidez, bájala a 0,9 con `atempo=0.9` (no cambia el tono; no bajar de 0,85; si una palabra sigue sin entenderse, pedirle que regrabe solo esa frase). Su voz va unos 3 dB por encima de Andrea, con un poco de presencia (EQ +3 dB en 3 kHz y compresor suave), para que no se oiga más baja.
- **Primer fotograma**: cara o acción + el texto del gancho, sin fundido (el generador ya pone el texto desde el fotograma 0). La primera frase dice quién hizo qué.
- **Duración**: 25–35 s (5–7 frases cortas). El generador avisa si pasa de 36 s.
- **Las noticias institucionales se cuentan a través de una persona.**
- **Fotos de personas (regla de Mui, 18/11, reemplaza la anterior):** cada reel lleva **fotos reales del protagonista** de la noticia (jugador, DT, figura), no solo dibujos de Cloudflare. Fuente: Wikimedia Commons con licencia libre (CC-BY, CC-BY-SA, CC0 o PD) vía `"foto_commons"` (pone el crédito solo), o fotos que mande Mui. Antes de proponer el guion, busca en Commons la foto de cada protagonista y anota el nombre exacto del archivo en el borrador. **Si no encuentras una foto libre de algún protagonista, avísale a Mui en el mensaje de aprobación (antes de generar) y pídesela.** Nunca fotos de medios, agencias, clubes o transmisiones descargadas por el agente. Estadios y lugares: también Commons.
- **Mezcla de recursos (regla de Mui, 18/11):** usa todos los recursos, no solo dibujos: foto real del protagonista (gancho y escena clave), escudos, gráficos, jugadas `tv`/`retro`, fotos de Commons de estadios, y 1 dibujo de Cloudflare como apoyo (ambiente, objetos).
- **Nada de fotos ni videos de medios, agencias o transmisiones** salvo lo que Mui mande y apruebe (ver regla 4 de "Lecciones de las métricas").
- Mui aprueba los guiones antes de producir y los videos antes de publicar.
- **Datos de terceros:** citar la fuente original y quién lo difundió, en el cierre, la franja y la descripción (ej. "Datos: CIES Football Observatory · Impect · Vía @DanielNavasV"). Una cifra sin fuente oficial se dice con cuidado ("según las cuentas de su carrera"), nunca como récord oficial.
- **Clips que manda Mui:** recortar a vertical quitando el botón flotante del iPhone, el contador de espectadores, el marcador del canal y su logo.
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
- **Regla permanente (Mui, 17/11): TODO equipo en `partido` o `marcador` lleva escudo, también las selecciones y los rivales extranjeros.** El generador lo busca solo: si el equipo no trae `"escudo"`, usa `img/escudos/<nombre-sin-tildes>.png` (ej. `bolivia.png`, `paises-bajos.png`) y, si ese archivo no existe, lo baja de TheSportsDB durante la Action (`bajar_escudo` en generar.py; nombres en español mapeados en `ESCUDO_EN`). Revisa en la hoja de contacto que salga el escudo correcto; si no salió, súbelo a `lotes/img/escudos/` antes de mandar el video a Mui. **Si falta el escudo de cualquiera de los equipos, la tarjeta sale SIN NINGÚN escudo** (regla de Mui del 17/11, ya está en el generador: `todos_con_escudo`); nunca uno sí y el otro no. TheSportsDB bloquea las descargas automáticas (403): si falta un escudo, pídele a Mui la imagen ANTES de generar, quítale el fondo y guárdala en `lotes/img/escudos/<nombre>.png`. Ya hay: bolivia, boca, atletico-mineiro, lanus.

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

## Guion de edición con cada guion (Mui, 21/11)
- Con CADA guion que se manda a Mui para aprobar va también su GUION DE EDICIÓN, segundo a segundo, para que ella vea el video antes de producirlo. Una línea por escena con este formato:
  `0:00–0:03 · VISUAL: foto Commons de Enner (zoom in) · TEXTO: "¡ENNER LO HIZO!" · EFECTO: destello + flash de entrada · VOZ: Mui (gancho)`
- Debe decir en qué segundo entra cada imagen (foto Commons, escudo, gráfico, dibujo, pizarra), cada efecto (destello, hinchada, suspenso, zoom, glitch), cada transición entre escenas (flash, barrido, zoom, glitch, rota), los textos/franja en pantalla y quién dice cada frase (Mui o Andrea).
- Los segundos se estiman a ~2,6 palabras por segundo hasta que llegue el audio; con el audio de Mui se ajustan con los tiempos reales (inicio/fin) y, si cambian mucho, se avisa.
- Va en el mismo mensaje de aprobación (debajo del guion) y en el .md del borrador.

## Colores de las súper imposiciones según el club (Mui, 22/11)
- Si la noticia es de UN club en particular, el reel se ambienta con SUS colores (cajas, letras de las cajas, franja y barra de progreso): en el JSON del reel pon `"club": "emelec"` (nombres en PALETAS de scripts/guineo/generar.py: emelec, barcelona, liga, idv, aucas, el nacional, deportivo cuenca, macara, delfin, orense, universidad catolica, mushuc runa, tecnico universitario, libertad, manta, vinotinto, ecuador, boca, atletico mineiro, real madrid, fc barcelona, argentina, brasil). Nunca un reel de Emelec con amarillo y negro (son los de Barcelona) ni al revés.
- Club que no está en la lista: `"paleta": {"fondo": "#RRGGBB", "texto": "#RRGGBB"}` con sus dos colores principales (y agrégalo a PALETAS).
- Noticia sin club (mundo, Tri en general, varios equipos, otros deportes): sin "club" ni "paleta"; el generador intercala los colores oficiales de Guineo: amarillo (reels impares) y verde guineo joven (reels pares).
- Si la noticia enfrenta a dos clubes, usa los del protagonista de la noticia (el que ganó o del que se habla); si es una previa neutral, colores de Guineo.

## Recursos audiovisuales compartidos por Mui (regla, 22/11)
- Toda foto, audio o video que comparta Mui se guarda en el git y se registra aquí, para que lo usen ella y los demás agentes.
- `recursos/clips-comentarios/` — canal de clips virales + comentarios: 8 memes recortados (knuckles, audífonos, bailarín, grito/Vegeta, perro, ete Sech, Pepe el pollo en pantalla verde, primitos), 2 clips (Malambo, fuegos artificiales en Bolivia), tarjetas de comentarios, videos finales y el script `build.py`. Detalle en su README.md.
## Personajes del entorno del deporte (Mui, 22/11)
- Además de jugadores y equipos, los agentes vigilan a periodistas deportivos, directivos y presidentes de clubes, dirigentes, árbitros, padres o familiares de jugadores, hinchas e influencers del fútbol. Si una frase, pelea, publicación o video de alguno genera interacciones y sube rápido como tendencia, entra como posible noticia o reel (marcado con 🗣️).
- Se verifica qué dijo o hizo en una fuente fiable (nunca frases sin confirmar). No se descarga su video o publicación: se cuenta con gráfico "cita", foto_commons si es figura pública con foto libre, o dibujo sin cara realista.
- Con personas privadas (hinchas, padres): respeto, sin burlas, sin datos personales y sin exponer a menores; si es delicado, Mui decide antes.

## Retención de Shorts (métricas de YouTube 22/11 · Mui aprobó probar)
Diagnóstico: 39–53 % "se quedaron" (hay que pasar de 60 % para salir del rango 550–980 vistas); caída fuerte entre 0:04 y 0:10; caída de golpe en el cierre "Comenta y síguenos". Desde el 23/11:
1. DURACIÓN 20–25 s, 4–5 frases (reemplaza la regla anterior de 25–35 s y 5–7 frases).
2. FOTOGRAMA 0 CON MOVIMIENTO: foto del protagonista con zoom ya en marcha y la frase más fuerte sonando desde el primer cuadro. Nunca un cartel de título solo de texto. La portada se elige aparte.
3. DEL SEGUNDO 3 AL 10: un cambio visual cada ~2 s (escenas cortas, zoom, cifra que salta, escudo) para frenar la caída.
4. SIN CIERRE "Comenta y síguenos": se elimina esa frase y la escena de cierre al final. La pregunta al hincha va a MITAD del video, pegada a una invitación de ~3 s con algo concreto (ej.: "¿Para ti fue penal? Te leo, y si quieres el fútbol ecuatoriano contado así, sigue a Guineo."). La ÚLTIMA frase debe enlazar con la primera para que el video se repita en bucle.
5. PRUEBA DE VOZ (lote del 23/11 y siguientes hasta tener datos): la mitad de los reels con TODAS las frases grabadas por Mui (sin Andrea) y la otra mitad con Andrea en los datos. Marca cada reel en el borrador con "Prueba voz: Mui" o "Prueba voz: Mui+Andrea" y repítelo en textos-*.txt para comparar después.
6. PRIORIDAD a "X vs Y" con el RESULTADO en el título, publicado lo antes posible después del partido (formato del mejor video: Ecuador vs Uganda 0-0, 1,1 K y 53 %).
7. INVITAR AL CANAL sin cortar el video: el generador pone siempre "@GUINEOCOMUNICACIONES" en la franja; en textos-*.txt agrega por video: "Comentario fijado:" (la pregunta + invitación a seguir el canal) y "Video relacionado sugerido:" (un video previo de Guineo del mismo tema o equipo, para enlazarlo en YouTube) y, cuando se pueda, series ("Parte 1 de 2", "mañana te cuento…").

## Gancho sin revelar la noticia (Mui, 22/11) — TIENE PRIORIDAD sobre "la primera frase dice quién hizo qué"
- SIEMPRE gancho, pero NUNCA se revela toda la noticia al inicio, sea partido, suceso, frase polémica o desenlace de un meme: se dice DE QUÉ trata y QUIÉN está, no CÓMO termina. Algo sutil que abra una pregunta o una tensión para que se queden hasta el final.
- La primera frase presenta al protagonista y la tensión ("Barcelona se jugaba la Libertadores… y todo se definió en un minuto."), no el resultado ("Barcelona ganó 1-0 y va a la Libertadores").
- El dato clave (marcador, gol, récord, la frase exacta, el remate del meme) se revela entre el 60 % y el 70 % del video; después solo queda el remate que enlaza con el inicio (bucle).
- Textos en pantalla, franja y gráficos tampoco lo adelantan: el marcador/cifra/cita aparece recién en la escena de la revelación.
- Títulos: nombres y "X vs Y" para la búsqueda, con el desenlace como intriga ("Barcelona SC vs Universidad Católica: lo que pasó en el minuto 89"). Solo va el marcador en el título si el resultado mismo ES lo que la gente busca (final de torneo, resultado de la Tri); aun así el video lo revela tarde. La portada tampoco lo revela.

## Fórmula del título: SEO + gancho (Mui, 22/11)
Título = [LO QUE LA GENTE BUSCA] + [GANCHO QUE NO REVELA] + #Shorts
- Primero la palabra clave, dentro de los primeros ~40 caracteres (lo que se ve en el celular): nombres completos ("Enner Valencia", "Barcelona SC vs Universidad Católica"), el torneo o el evento, y si existen, las búsquedas en alza de explore-ultimo.json tal cual.
- Después el gancho: intriga concreta sin revelar el desenlace (minuto, gesto, frase, decisión, "lo que nadie vio", "la reacción de…", "por qué…"). Debe ser verdad: nada de clickbait falso que el video no cumpla.
- Máximo 70 caracteres antes de #Shorts; sin MAYÚSCULAS completas; 1 emoji como máximo (al final del gancho).
- Ejemplos: "Barcelona SC vs Universidad Católica: lo que pasó en el minuto 89 ⏱️ #Shorts" · "Enner Valencia en la final de la Sudamericana: su reacción lo dijo todo #Shorts" · "Ecuador vs Uganda: el detalle que nadie vio en el 0-0 #Shorts".
- En el txt de publicación, proponer 2 títulos por video (A y B) para que Mui elija o pruebe.

## Los cuatro grandes en los titulares del SRF (Mui, 23/11)
- En los titulares del Súper Resumen Futbolero va SIEMPRE algo de Barcelona SC, Emelec, Liga de Quito e IDV, sin revelar el desenlace (regla del gancho). Ver scripts/guineo/SRF.md.

## Formatos de conexión: historias y tops (Mui, 23/11 · idea de un experto en redes y deportes)
- En la ronda de la mañana, además de las noticias, el agente propone 1–2 piezas de FORMATO ligadas a lo que está dando vueltas en redes:
  - 🏆 TOP 5 (momentos épicos, goles imposibles, remontadas, ecuatorianos en finales, etc.). El n.º 1 se revela al final.
  - 📖 HISTORIA de un deportista nuestro (superación, la vida de…, "el día que…"), contada como historia de una persona: gancho de la persona antes que el logro.
  - Versión en español de un TOP 5 de un creador inglés que esté pegando: se toma la IDEA y la lista, se investiga por cuenta propia, se escribe un guion propio con enfoque ecuatoriano/latino cuando se pueda, y se menciona la inspiración en la descripción ("Inspirado en el top de @canal"). Nunca se copia su guion palabra por palabra ni su video.
- Duración: Shorts de 45–60 s (versiones largas de 3–5 min solo si Mui lo pide). Mismas reglas de gancho sin revelar, colores por club, guion de edición y título SEO + gancho.
- COPYRIGHT: "pocos segundos" NO evita reclamos (Content ID detecta 2–3 s). La base del video es material propio (voz de Mui, foto_commons, escudos, pizarra, dibujos, cifras); clips reales solo si Mui los manda, máx. 2–3 s, con voz encima y crédito. Nunca descargados por el agente.

## Decimales en gráficos (bug 23/11)
- Los decimales van con COMA ("0,33"), nunca con punto: el punto se lee como separador de miles. Desde el 23/11 el generador ya no cuenta "0.31" como 31, pero igual escribe decimales con coma.

## Memes y sonidos en videos (Mui, 23/11)
- SRF y videos largos: imagen relacionada con cada noticia + un meme (video o imagen) relacionado entre noticia y noticia + efectos de sonido. Antes de producir, guion técnico a Mui con memes, imágenes, efectos y sonidos segundo a segundo (ver scripts/guineo/SRF.md).

## Recursos propios en CADA corto (Mui, 23/11) — no depender solo de lo que manda Mui
Diagnóstico: los últimos cortos se apoyaron casi solo en fotos y titulares de texto; el reel de Enner (el del suspenso de película) funcionó porque tenía un momento distinto. Desde ahora, cada corto lleva SÍ O SÍ:
1. Al menos 1 DIBUJO de Cloudflare relacionado con la escena (ambiente, objeto, metáfora visual; sin caras realistas).
2. Al menos 1 ANIMACIÓN propia: pizarra/pixel con la jugada, tv/retro, cifra animada, marcador que gira, escudos que chocan, etc.
3. Un MOMENTO DE CINE distinto en cada video, en la escena clave (la revelación). Rotar, sin repetir el mismo en dos videos seguidos del día: suspenso (silencio + golpe), cámara lenta + desaturado, zoom dramático con latido, glitch/corte de señal, flash + hinchada, congelado tipo "fotograma de película", cuenta regresiva, disco rayado y freno.
4. EFECTOS DE SONIDO acompañando cada cambio importante (whoosh, golpe, redoble, campana, disco rayado, latido, silencio antes de la revelación).
- El guion de edición debe marcar cuál es el dibujo, la animación y el momento de cine de ese video. Fotos de Commons y material de Mui SUMAN, no reemplazan estos recursos.

## Guineo Animación (Mui, 23/11)
- Cortos de anécdotas/historias de fútbol (libros de Mui) en ESTILO PLASTILINA (claymation): figuras de plastilina con textura de huellas, maquetas de estadio, luz de estudio, look stop-motion. Referencia: scripts/guineo/animacion/ref-plastilina.png (usarla como "referencias" en el JSON de dibujos).
- Dibujos de Cloudflare: sin caras reconocibles de personas reales, sin texto ni escudos en la imagen. Las anécdotas se cuentan con palabras propias (nunca se copia el texto del libro) y se cita el libro en la descripción.
- Cada ilustración se anima (paneo, zoom, capas, lluvia/partículas, parpadeos) + SFX + voz de Mui; momento de cine en la revelación. Guion técnico a Mui antes de producir.
