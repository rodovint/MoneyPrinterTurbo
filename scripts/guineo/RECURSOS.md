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
- **Primer fotograma**: cara o acción + el texto del gancho, sin fundido (el generador ya pone el texto desde el fotograma 0). La primera frase dice quién hizo qué.
- **Duración**: 25–35 s (5–7 frases cortas). El generador avisa si pasa de 36 s.
- **Las noticias institucionales se cuentan a través de una persona.**
- **Fotos de personas**: solo las que manda Mui. Estadios y lugares: Wikimedia Commons libres (crédito automático).
- **Nada de fotos ni videos de medios, agencias o transmisiones** salvo lo que Mui mande.
- Mui aprueba los guiones antes de producir y los videos antes de publicar.

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
- **Regla de Mui**: ilustraciones de la escena (estadio, hinchas de espaldas, balón, camisetas lisas, objetos), **nunca caras realistas de jugadores reales**, sin escudos, logos ni texto. Cupo gratis ≈ 6 dibujos/día con "9b"; para más usa `"modelo": "4b"`.
- En la descripción: "Ilustraciones generadas con IA".

## Créditos (van en la descripción de YouTube)
- Música: "Epic Celestial Choir 2" – Megis (CC BY), Internet Archive.
- Hinchada: "Football-crowd-Cheer+Jeers" – paulw2k vía Freesound (CC BY 4.0).
- Ver `scripts/guineo/audio/LICENSES.csv`.

## Publicación (SEO por red, en Metricool)
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
Coordenadas 0–100: `x` izquierda→derecha, `y` desde la línea de gol (0, arriba) hasta la mitad de cancha (100). `y < 0` es dentro del arco. Los pasos se reparten a lo largo de la frase narrada. Describir la jugada solo con lo que cuentan las crónicas verificadas; si no se sabe cómo fue, no inventarla.

## Dibujos con Cloudflare Workers AI
- Action "Dibujos (Cloudflare Workers AI)" + `scripts/guineo/dibujar.py` (FLUX.2 klein). Necesita los secretos `CF_ACCOUNT_ID` y `CF_API_TOKEN`.
- Se pide con un JSON en `lotes/dibujos/<nombre>.json` (referencias de cara y estilo en `scripts/guineo/ref/`). El resultado queda en la rama `dibujos-out`, carpeta `<nombre>/<id>.png`.
- Para usarlos: copiar los PNG a `lotes/img/` y ponerlos como `"foto"` con un `"movimiento"`.

## Pendiente / ideas
- Recreación 3D de jugadas con la animación de El Profe (otro repo): aún no conectada.
