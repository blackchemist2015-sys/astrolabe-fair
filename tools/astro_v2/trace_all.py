"""Trace thrones (and the silver rete of A2.17) from the book photographs
and store them normalised (mater radius = 1, rete: Capricorn radius = 1)
in traced/*.json.  Also writes rectified photos for the overlay sheets.

usage: python3 trace_all.py /path/Volume2EN.pdf"""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import trace as T
from photos import FRONT, BACK, SILVER_RETE

HERE = os.path.dirname(os.path.abspath(__file__))


def extract_images(book, cache):
    os.makedirs(cache, exist_ok=True)
    if not any(f.endswith('.png') for f in os.listdir(cache)):
        subprocess.run(['pdfimages', '-f', '91', '-l', '156', '-png', '-p', book, os.path.join(cache, 'i')], check=True)
    return cache


def main(book):
    cache = extract_images(book, os.path.join(HERE, '.cache', 'img'))
    out = os.path.join(HERE, 'traced')
    os.makedirs(out, exist_ok=True)
    photos = os.path.join(HERE, '.cache', 'rectified')
    os.makedirs(photos, exist_ok=True)
    meta = {}
    for k, (f, cut) in FRONT.items():
        path = os.path.join(cache, f'i-{f}.png')
        polys, (img, cx, cy, r) = T.throne_v2(path, 2.0, cut, upscale=3)
        json.dump({'id': k, 'photo': f, 'cut_h': cut, 'polys': [{'hole': bool(h), 'pts': [[round(x, 5), round(y, 5)] for x, y in p]} for p, h in polys]},
                  open(os.path.join(out, f'{k}_throne.json'), 'w'))
        for side, pid in (('front', f), ('back', BACK.get(k))):
            if not pid:
                continue
            img, mask, cx, cy, r = T.rectify(os.path.join(cache, f'i-{pid}.png'), 2)
            # crop around the instrument and save
            h, w = img.shape[:2]
            x0, x1 = max(0, int(cx - 1.25 * r)), min(w, int(cx + 1.25 * r))
            y0, y1 = max(0, int(cy - 1.75 * r)), min(h, int(cy + 1.2 * r))
            crop = img[y0:y1, x0:x1]
            fn = f'{k}_{side}.jpg'
            cv2.imwrite(os.path.join(photos, fn), crop, [cv2.IMWRITE_JPEG_QUALITY, 80])
            meta[f'{k}_{side}'] = {'file': fn, 'cx': cx - x0, 'cy': cy - y0, 'r': r, 'w': x1 - x0, 'h': y1 - y0}
        print('traced', k, len(polys))
    json.dump(meta, open(os.path.join(photos, 'meta.json'), 'w'), indent=1)
    for k in SILVER_RETE:
        polys, (img, cx, cy, r, ro) = T.silver_rete(os.path.join(cache, f'i-{FRONT[k][0]}.png'), 1.0, upscale=3)
        json.dump({'id': k, 'polys': [{'hole': bool(h), 'pts': [[round(x, 5), round(y, 5)] for x, y in p]} for p, h in polys]},
                  open(os.path.join(out, f'{k}_rete.json'), 'w'))
        print('rete', k, len(polys))


if __name__ == '__main__':
    main(sys.argv[1])
