# Recursos — canal de clips virales + comentarios

Formato: clip → tarjeta de comentario (con "pop") → meme de reacción → sigue el clip. Se repite 4 veces y cierra con "¿Cuál fue el mejor comentario?".
Referencia de estilo: @humorrandom-p1r. Video final: 1080x1920 a 30 fps, -14 LUFS.

## memes/ (recortados sin la interfaz de TikTok)
| archivo | dur. | uso sugerido |
|---|---|---|
| knuckles-sorprendido.mp4 | 2.1 s | sorpresa, ":0" |
| audifonos-mueca.mp4 | 0.9 s | vergüenza ajena, mueca |
| bailarin-senalando.mp4 | 0.9 s | burla o festejo, "tú" |
| grito-animado-vegeta.mp4 | 3.5 s | clímax, el mejor comentario |
| perro-mirada-fija.mp4 | 1.7 s | silencio incómodo, "¿en serio?" |
| ete-sech-baile.mp4 | 8.9 s | festejo o contraste de tamaño (recortar) |
| pepe-el-pollo-pantalla-verde.mp4 | 11.7 s | pantalla verde: quitar el fondo con chromakey=0x00FF00 |
| primitos-camara-cae.mp4 | 3.9 s | caos, "cuando dejo de vigilar…" |

## clips/
- malambo-penal-arco-roja.mp4 — Perú, crédito @futbolmacho.pe / Tacho TV
- bolivia-fuegos-artificiales.mp4 — crédito Red Uno de Bolivia

## comentarios/
Tarjetas recortadas de las capturas: m* = Malambo, f* = fuegos artificiales.

## videos-finales/
- malambo.mp4 y fuegos.mp4 — primera versión completa (22/11/2026)

## fuente/
- humorrandom-referencia.mp4 — video de referencia del formato (de ahí salen los primeros 5 memes)

## script/build.py
Arma el video a partir de una línea de tiempo (clip / card / meme). Uso: `python3 build.py malambo`.
Si cambias las rutas de origen, ajusta `src` y `REF` dentro del script.

## Regla
Todo recurso audiovisual que comparta Mui (foto, audio o video) se guarda aquí y se registra en scripts/guineo/RECURSOS.md.
