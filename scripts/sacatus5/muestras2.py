"""Segunda tanda de muestras de voz para el capitán de SacaTus5: la misma frase en varias voces."""
import asyncio, os, sys
import edge_tts

OUT = sys.argv[1] if len(sys.argv) > 1 else "sacatus5/out"
FRASE = "Tranquilos, caballeros. Yo tengo mi perfil y nuestro equipo en SacaTus5."
VOCES = [
    ("09_sebastian_ve_grave", "es-VE-SebastianNeural", "-6Hz", "+0%"),
    ("10_sebastian_ve_rapido", "es-VE-SebastianNeural", "+0Hz", "+12%"),
    ("11_alvaro_es", "es-ES-AlvaroNeural", "+0Hz", "+5%"),
    ("12_emilio_do", "es-DO-EmilioNeural", "+0Hz", "+5%"),
    ("13_juan_cr", "es-CR-JuanNeural", "+0Hz", "+5%"),
    ("14_roberto_pa", "es-PA-RobertoNeural", "+0Hz", "+5%"),
    ("15_mateo_uy", "es-UY-MateoNeural", "+0Hz", "+5%"),
    ("16_marcelo_bo", "es-BO-MarceloNeural", "+0Hz", "+5%"),
    ("17_mario_py", "es-PY-MarioNeural", "+0Hz", "+5%"),
    ("18_andres_gt", "es-GT-AndresNeural", "+0Hz", "+5%"),
    ("19_carlos_hn", "es-HN-CarlosNeural", "+0Hz", "+5%"),
    ("20_victor_pr", "es-PR-VictorNeural", "+0Hz", "+5%"),
    ("21_manuel_cu", "es-CU-ManuelNeural", "+0Hz", "+5%"),
    ("22_rodrigo_sv", "es-SV-RodrigoNeural", "+0Hz", "+5%"),
]

async def main():
    os.makedirs(f"{OUT}/muestras2", exist_ok=True)
    for name, v, pitch, rate in VOCES:
        for intento in range(3):
            try:
                await edge_tts.Communicate(FRASE, v, rate=rate, pitch=pitch).save(f"{OUT}/muestras2/{name}.mp3")
                print("voz", name); break
            except Exception as e:
                print(f"::warning::{name}: {e}"); await asyncio.sleep(3)

asyncio.run(main())
