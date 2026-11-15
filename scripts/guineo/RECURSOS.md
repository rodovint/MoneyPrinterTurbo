# Guineo Deportes · recursos visuales del generador de reels

Guía para cualquier chat o agente que arme lotes en `lotes/actual.json`.
El generador es `scripts/guineo/generar.py` (lo corre la Action "Generar reels Guineo Deportes").

## Reglas fijas
- **Voz siempre humana**: Andrea o Mui. Cada reel lleva `"audio": "audio/NN"` y el archivo va en `lotes/audio/`. Nunca la voz automática.
- **Nada de fotos ni videos de medios, agencias o transmisiones de TV** (derechos de autor y Content ID). Solo lo de esta lista.
- Mui aprueba los guiones antes de grabar y los videos antes de publicar.

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
