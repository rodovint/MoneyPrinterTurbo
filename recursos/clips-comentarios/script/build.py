"""Arma un video de 'clip viral + comentarios' (1080x1920) desde una grabación de pantalla de TikTok.
Uso: python3 build.py malambo
"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ANTON = '/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf'
FG_Y = 330  # donde va el clip dentro del 9:16

CFG = {
  'malambo': dict(
    src='/mnt/user-data/uploads/ScreenRecording_11-22-2026_04-29-25_1.mp4',
    pre='delogo=x=6:y=384:w=120:h=120,crop=645:900:0:118',
    title=['LE ROMPIÓ EL ARCO', 'DE UN PENAL... Y LE SACARON ROJA'],
    credit='Video: @futbolmacho.pe',
    end='¿CUÁL FUE EL MEJOR COMENTARIO?',
    # (tipo, args)
    timeline=[
      ('clip', 4.6, 12.0, 1.0, 1.0, None),
      ('card', 'm1_alexander', 8.6, 3.4),
      ('meme', 'perro'),
      ('clip', 12.0, 22.3, 1.0, 1.0, None),
      ('card', 'm2_omar', 9.4, 3.2),
      ('meme', 'audifonos'),
      ('clip', 8.6, 11.0, 1.0, 1.5, None),
      ('card', 'm3_gaaaa', 21.5, 3.2),
      ('meme', 'grito'),
      ('clip', 22.3, 27.0, 1.0, 1.0, None),
      ('card', 'm4_franco', 26.5, 4.2),
      ('meme', 'knuckles'),
      ('clip', 27.0, 37.9, 1.0, 1.0, 'END'),
    ]),
  'fuegos': dict(
    src='/mnt/user-data/uploads/30dee8aa-ScreenRecording_11-22-2026_04-34-11_1.mp4',
    pre='delogo=x=6:y=386:w=118:h=116,crop=640:430:0:334',
    fg_y=520, fg_h=726,
    title=['LA MANDÓ A LAS NUBES', 'Y SE ARMÓ EL CORTOCIRCUITO'],
    credit='Video: Red Uno de Bolivia',
    end='¿CUÁL FUE EL MEJOR COMENTARIO?',
    timeline=[
      ('clip', 0.0, 8.0, 1.0, 1.0, None),
      ('card', 'f1_john', 7.0, 3.6),
      ('meme', 'knuckles'),
      ('clip', 8.0, 14.8, 1.0, 1.0, None),
      ('card', 'f2_cristian', 12.5, 3.6),
      ('meme', 'perro'),
      ('clip', 11.2, 14.0, 0.6, 1.3, 'REPETICIÓN'),
      ('card', 'f3_nacho', 16.0, 4.2),
      ('meme', 'bailarin'),
      ('clip', 14.8, 19.9, 1.0, 1.0, None),
      ('card', 'f4_benellit', 13.0, 4.5),
      ('meme', 'grito'),
      ('clip', 11.0, 15.0, 1.0, 1.2, 'END'),
    ]),
}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)

def font(sz): return ImageFont.truetype(ANTON, sz)

def text_block(lines, size, maxw=1000, color='white', box=None):
    """PNG transparente con texto con contorno negro grueso."""
    f = font(size)
    im = Image.new('RGBA', (W, 40 + len(lines) * int(size * 1.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 20
    for i, ln in enumerate(lines):
        fs = size
        while d.textlength(ln, font=font(fs)) > maxw: fs -= 2
        ff = font(fs); tw = d.textlength(ln, font=ff)
        x = (W - tw) / 2
        if box and i == len(lines) - 1:
            d.rounded_rectangle((x - 18, y + 2, x + tw + 18, y + fs * 1.18), 12, fill=box)
        d.text((x, y), ln, font=ff, fill=color if not (box and i == len(lines)-1) else 'white',
               stroke_width=0 if (box and i == len(lines)-1) else 7, stroke_fill='black')
        y += int(fs * 1.25)
    return im

def make_assets(c, out):
    text_block([c['title'][0], c['title'][1]], 92, box=(226, 30, 60, 255)).save(f'{out}/title.png')
    text_block(['REPETICIÓN'], 70, box=(226, 30, 60, 255)).save(f'{out}/replay.png')
    text_block([c['end'], 'COMENTA'], 78, box=(226, 30, 60, 255)).save(f'{out}/end.png')
    cr = Image.new('RGBA', (W, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(cr)
    ff = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 30)
    d.text((W - 30 - d.textlength(c['credit'], font=ff), 10), c['credit'], font=ff, fill=(255, 255, 255, 200),
           stroke_width=3, stroke_fill='black')
    cr.save(f'{out}/credit.png')

def card_png(name, out):
    im = Image.open(f'cards/{name}.png').convert('RGBA')
    s = 980 / im.width; im = im.resize((980, int(im.height * s)), Image.LANCZOS)
    pad = 40
    can = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', can.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 10, pad + im.width, pad + im.height + 10), 36, fill=(0, 0, 0, 170))
    can = Image.alpha_composite(can, sh.filter(ImageFilter.GaussianBlur(16)))
    mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, *im.size), 36, fill=255)
    can.paste(im, (pad, pad), mask)
    p = f'{out}/card_{name}.png'; can.save(p); return p, can.size

ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS),
       '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k']

def seg_clip(c, out, i, a, b, speed, zoom, tag):
    dur = (b - a) / speed
    fg = f"[0:v]{c['pre']},setpts=(PTS-STARTPTS)/{speed}"
    if zoom != 1.0: fg += f",crop=iw/{zoom}:ih/{zoom}"
    fg += f",scale=1080:-2,split[f][b0];"
    bg = f"[b0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=25:2,eq=brightness=-0.2[bg];"
    fc = fg + bg + f"[bg][f]overlay=0:{c.get('fg_y',FG_Y)}:shortest=1[v0];[v0][1:v]overlay=0:40[v1];[v1][2:v]overlay=0:{c.get('fg_y',FG_Y)}+{c.get('fg_h',1507)}+10[v2]"
    last = 'v2'
    inputs = ['-ss', str(a), '-t', str(b - a), '-i', c['src'], '-loop', '1', '-i', f'{out}/title.png',
              '-loop', '1', '-i', f'{out}/credit.png']
    if tag == 'REPETICIÓN':
        inputs += ['-loop', '1', '-i', f'{out}/replay.png']
        fc += f";[{last}][3:v]overlay=0:{c.get('fg_y',FG_Y)}+40:enable='lt(mod(t,0.8),0.55)'[v3]"; last = 'v3'
    if tag == 'END':
        inputs += ['-loop', '1', '-i', f'{out}/end.png']
        fc += f";[{last}][3:v]overlay=0:'if(lt(t,{dur-3.5}),{H},max(1250,{H}-(t-{dur-3.5})*2400))'[v3]"; last = 'v3'
    af = f"[0:a]asetpts=PTS-STARTPTS" + (f",atempo={speed}" if speed != 1 else '') + "[a]"
    run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', fc + ';' + af, '-map', f'[{last}]', '-map', '[a]',
         '-t', f'{dur:.3f}', *ENC, f'{out}/seg{i:02d}.mp4'])

REF='/mnt/user-data/uploads/ScreenRecording_11-22-2026_04-13-32_1.mp4'
MEMES={'knuckles':(17.85,19.95),'audifonos':(23.05,23.95),'bailarin':(25.85,26.75),
       'grito':(29.45,32.95),'perro':(35.7,37.4)}

def seg_meme(c, out, i, name):
    a,b=MEMES[name]; dur=b-a
    fc=(f"[0:v]crop=610:830:45:110,scale=1080:-2,split[f][b0];"
        f"[b0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=25:2,eq=brightness=-0.2[bg];"
        f"[bg][f]overlay=0:(H-h)/2[v];[0:a]asetpts=PTS-STARTPTS[a]")
    run(['ffmpeg','-y','-v','error','-ss',str(a),'-t',str(dur),'-i',REF,'-filter_complex',fc,
         '-map','[v]','-map','[a]','-t',f'{dur:.3f}',*ENC,f'{out}/seg{i:02d}.mp4'])

def seg_card(c, out, i, name, t_bg, dur):
    bgp = f'{out}/bg{i:02d}.png'
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t_bg), '-i', c['src'], '-frames:v', '1', '-vf',
         f"{c['pre']},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.25", bgp])
    cp, (cw, ch) = card_png(name, out)
    x = (W - cw) // 2; y = (H - ch) // 2 - 60
    # entra con salto desde abajo (0.28 s) + leve rebote
    yexpr = f"if(lt(t,0.28),{H}-({H}-{y})*sin(t/0.28*PI/2)*1.04,{y})"
    fc = (f"[0:v]scale={W}:{H},format=yuv420p[bg];[bg][1:v]overlay={x}:'{yexpr}'[v];"
          f"aevalsrc='0.5*sin(2*PI*(500+1800*t)*t)*exp(-22*t)|0.5*sin(2*PI*(500+1800*t)*t)*exp(-22*t)':s=44100:d=0.25,"
          f"apad=whole_dur={dur}[a]")
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-framerate', str(FPS), '-i', bgp, '-loop', '1', '-i', cp,
         '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', str(dur), *ENC, f'{out}/seg{i:02d}.mp4'])

def main(key):
    c = CFG[key]; out = f'build_{key}'; os.makedirs(out, exist_ok=True)
    make_assets(c, out)
    for i, s in enumerate(c['timeline']):
        if s[0] == 'clip': seg_clip(c, out, i, *s[1:])
        elif s[0] == 'meme': seg_meme(c, out, i, s[1])
        else: seg_card(c, out, i, *s[1:])
        print('seg', i, 'ok', flush=True)
    with open(f'{out}/list.txt', 'w') as f:
        for i in range(len(c['timeline'])): f.write(f"file 'seg{i:02d}.mp4'\n")
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{out}/list.txt', *ENC,
         '-af', 'loudnorm=I=-14:TP=-1.5', f'{key}.mp4'])
    print('done', key)

if __name__ == '__main__':
    main(sys.argv[1])
