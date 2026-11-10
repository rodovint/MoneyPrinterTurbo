"""Frase de cierre del anuncio de SacaTus5, con la voz del capi (Marcelo)."""
import asyncio, os, sys
import edge_tts

OUT = sys.argv[1] if len(sys.argv) > 1 else "sacatus5/out"
TOMAS = {
    "c6_a": ("Completa tu equipo... saca tus cinco.", "+0%", "+0Hz"),
    "c6_b": ("Completa tu equipo. ¡Saca tus cinco!", "+5%", "+0Hz"),
    "c6_c": ("Completa tu equipo... ¡saca tus cinco!", "-5%", "-2Hz"),
}

async def main():
    os.makedirs(f"{OUT}/capi-marcelo", exist_ok=True)
    for k, (txt, rate, pitch) in TOMAS.items():
        for intento in range(3):
            try:
                await edge_tts.Communicate(txt, "es-BO-MarceloNeural", rate=rate, pitch=pitch).save(f"{OUT}/capi-marcelo/{k}.mp3")
                print("voz", k); break
            except Exception as e:
                print(f"::warning::{k}: {e}"); await asyncio.sleep(3)

asyncio.run(main())
