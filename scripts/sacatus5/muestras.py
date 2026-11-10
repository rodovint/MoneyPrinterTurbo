"""Muestras de voz para el capitán de SacaTus5: la misma frase en varias voces."""
import asyncio, os, sys
import edge_tts

OUT = sys.argv[1] if len(sys.argv) > 1 else "sacatus5/out"
FRASE = "Tranquilos, caballeros. Yo tengo mi perfil y nuestro equipo en SacaTus5."
VOCES = [
    ("1_luis_ec_grave", "es-EC-LuisNeural", "-6Hz", "+0%"),
    ("2_gonzalo_co", "es-CO-GonzaloNeural", "+0Hz", "+5%"),
    ("3_alex_pe", "es-PE-AlexNeural", "+0Hz", "+5%"),
    ("4_jorge_mx", "es-MX-JorgeNeural", "+0Hz", "+5%"),
    ("5_sebastian_ve", "es-VE-SebastianNeural", "+0Hz", "+5%"),
    ("6_tomas_ar", "es-AR-TomasNeural", "+0Hz", "+5%"),
    ("7_lorenzo_cl", "es-CL-LorenzoNeural", "+0Hz", "+5%"),
    ("8_alonso_us", "es-US-AlonsoNeural", "+0Hz", "+5%"),
]

async def main():
    os.makedirs(f"{OUT}/muestras", exist_ok=True)
    for name, v, pitch, rate in VOCES:
        for intento in range(3):
            try:
                await edge_tts.Communicate(FRASE, v, rate=rate, pitch=pitch).save(f"{OUT}/muestras/{name}.mp3")
                print("voz", name); break
            except Exception as e:
                print(f"::warning::{name}: {e}"); await asyncio.sleep(3)

asyncio.run(main())
