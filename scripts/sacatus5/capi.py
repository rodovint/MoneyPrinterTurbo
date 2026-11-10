"""Voces del capitán para el anuncio de SacaTus5 (chat del grupo). Se arma luego con cinecode."""
import asyncio, os, sys
import edge_tts

OUT = sys.argv[1] if len(sys.argv) > 1 else "sacatus5/out"
VOZ = sys.argv[2] if len(sys.argv) > 2 else "es-EC-LuisNeural"
TAG = sys.argv[3] if len(sys.argv) > 3 else "luis"
LINEAS = {
    "c1": "Tranquilos, caballeros. Yo tengo mi perfil y nuestro equipo en SacaTus5.",
    "c2": "Publico que nos faltan dos... y la app me avisa quién está libre, aquí cerquita.",
    "c3": "Cada uno tiene su perfil: posición, nivel, y el puntaje que le dieron sus compañeros.",
    "c4": "Le doy a invitar, le llega por WhatsApp... y listo. Ya estamos completos.",
    "c5": "Cancha, equipo, y gente con ganas de jugar. Sácate tus cinco.",
}

async def main():
    os.makedirs(f"{OUT}/capi-{TAG}", exist_ok=True)
    for rate in ("+0%", "+8%"):
        for k, txt in LINEAS.items():
            name = f"{OUT}/capi-{TAG}/{k}_{'r0' if rate == '+0%' else 'r8'}.mp3"
            for intento in range(3):
                try:
                    await edge_tts.Communicate(txt, VOZ, rate=rate).save(name)
                    print("voz", name); break
                except Exception as e:
                    print(f"::warning::{name}: {e}"); await asyncio.sleep(3)

asyncio.run(main())
