"""Helper for the manual tracing of retes: draws a measuring grid on the
rectified photograph of the front (normalised units: Capricorn circle /
outer rim of the rete = 1, centre = pin, y up)."""
import os, sys, json, math
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import INSTRUMENTS
from astrolabe import Dims

HERE = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(HERE, '.cache', 'rectified')


def spec_of(i):
    return next(s for s in INSTRUMENTS if s['id'] == i)


def rete_frame(i, k=None):
    m = json.load(open(os.path.join(PH, 'meta.json')))[f'{i}_front']
    img = cv2.imread(os.path.join(PH, m['file']))
    sp = spec_of(i)
    dm = Dims(sp)
    rc = dm.R_cap if not sp.get('rete_d') else min(sp['rete_d'] / 2, dm.R_cap)
    ratio = (k if k else rc / dm.R)
    return img, m['cx'], m['cy'], m['r'] * ratio


def grid(i, out, size=1000, k=None, ext=1.08, overlay=None):
    img, cx, cy, rr = rete_frame(i, k)
    h, w = img.shape[:2]
    half = rr * ext
    x0, y0 = cx - half, cy - half
    M = np.float32([[size / (2 * half), 0, -x0 * size / (2 * half)], [0, size / (2 * half), -y0 * size / (2 * half)]])
    im = cv2.warpAffine(img, M, (size, size), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0))
    im = (im * 0.85).astype(np.uint8)
    s = size / (2 * ext)
    def P(x, y):
        return (int(round(size / 2 + x * s)), int(round(size / 2 - y * s)))
    for v in np.arange(-1.0, 1.0001, 0.1):
        col = (255, 255, 0) if abs(v) < 1e-9 or abs(abs(v) - 0.5) < 1e-9 else (200, 200, 0)
        th = 2 if abs(v) < 1e-9 or abs(abs(v) - 0.5) < 1e-9 else 1
        cv2.line(im, P(v, -1.05), P(v, 1.05), col, th, cv2.LINE_AA)
        cv2.line(im, P(-1.05, v), P(1.05, v), col, th, cv2.LINE_AA)
        lab = f'{v:+.1f}'.replace('+0.', '.').replace('-0.', '-.').replace('+1.0', '1').replace('-1.0', '-1')
        cv2.putText(im, lab, (P(v, 1.05)[0] - 12, P(v, 1.05)[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(im, lab, (P(-1.07, v)[0] - 10, P(-1.07, v)[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.circle(im, P(0, 0), int(s), (0, 0, 255), 1, cv2.LINE_AA)
    if overlay is not None:
        for poly in overlay:
            cv2.polylines(im, [np.array([P(x, y) for x, y in poly], np.int32)], True, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imwrite(out, im)


if __name__ == '__main__':
    grid(sys.argv[1], sys.argv[2])


def astro_overlay(i, rot=90.0):
    """computed ecliptic circle and star positions in normalised units,
    rotated so that the Capricorn solstice is at angle `rot` (deg)."""
    from astrolabe import select_stars, rete_xy, ecliptic_circle
    from stars import STARS
    from geom import precess_star
    sp = spec_of(i)
    dm = Dims(sp)
    if sp.get('rete_d'):
        from geom import PolarProj
        dm.R_cap = min(sp['rete_d'] / 2, dm.R_cap); dm.proj = PolarProj(dm.R_cap, dm.eps)
    R = dm.R_cap
    ec, er = ecliptic_circle(dm)
    a = math.radians(rot - 90)
    def T(p):
        x, y = p[0] / R, p[1] / R
        return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
    stars = []
    for ra, de, ar, la in STARS:
        A, Dd = precess_star(ra, de, sp.get('year', 1000), dm.eps)
        if Dd < -dm.eps - 3 or Dd > 80:
            continue
        stars.append((la, T(rete_xy(dm, A, Dd))))
    return T(ec), er / R, T((0, dm.proj.R_eq)), dm.proj.R_eq / R, stars


def grid2(i, out, rot=90.0, size=1100, ext=1.06, clahe=True, extra=None):
    img, cx, cy, rr = rete_frame(i)
    half = rr * ext
    x0, y0 = cx - half, cy - half
    M = np.float32([[size / (2 * half), 0, -x0 * size / (2 * half)], [0, size / (2 * half), -y0 * size / (2 * half)]])
    im = cv2.warpAffine(img, M, (size, size), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0))
    if clahe:
        lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
        lab[..., 0] = cv2.createCLAHE(2.0, (8, 8)).apply(lab[..., 0])
        im = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    s = size / (2 * ext)
    def P(x, y):
        return (int(round(size / 2 + x * s)), int(round(size / 2 - y * s)))
    for v in np.arange(-1.0, 1.0001, 0.1):
        major = abs(v) < 1e-9 or abs(abs(v) - 0.5) < 1e-9 or abs(abs(v) - 1) < 1e-9
        col = (255, 200, 0) if major else (150, 120, 0)
        cv2.line(im, P(v, -1.04), P(v, 1.04), col, 1, cv2.LINE_AA)
        cv2.line(im, P(-1.04, v), P(1.04, v), col, 1, cv2.LINE_AA)
        lab_ = ('%.1f' % v).replace('0.', '.')
        cv2.putText(im, lab_, (P(v, 1.04)[0] - 10, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(im, lab_, (2, P(0, v)[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)
    ec, er, _, req, stars = astro_overlay(i, rot)
    cv2.circle(im, P(*ec), int(er * s), (0, 0, 255), 1, cv2.LINE_AA)
    cv2.circle(im, P(0, 0), int(s), (0, 0, 255), 1, cv2.LINE_AA)
    for la, p in stars:
        if abs(p[0]) > 1.02 or abs(p[1]) > 1.02:
            continue
        cv2.circle(im, P(*p), 5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(im, la[:7], (P(*p)[0] + 6, P(*p)[1] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (60, 255, 60), 1, cv2.LINE_AA)
    if extra:
        for poly, closed in extra:
            cv2.polylines(im, [np.array([P(x, y) for x, y in poly], np.int32)], closed, (255, 0, 255), 2, cv2.LINE_AA)
    cv2.imwrite(out, im)


def grid_m(i, out_prefix, size=1500, ext=1.0, step=0.05, extra=None, halves=True):
    """grid in units of the mater radius (rim of the mater = 1)."""
    img, cx, cy, rr = rete_frame(i, k=1.0)
    half = rr * ext
    x0, y0 = cx - half, cy - half
    M = np.float32([[size / (2 * half), 0, -x0 * size / (2 * half)], [0, size / (2 * half), -y0 * size / (2 * half)]])
    im = cv2.warpAffine(img, M, (size, size), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0))
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    lab[..., 0] = cv2.createCLAHE(2.0, (8, 8)).apply(lab[..., 0])
    im = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    s = size / (2 * ext)
    def P(x, y):
        return (int(round(size / 2 + x * s)), int(round(size / 2 - y * s)))
    n = int(round(1 / step))
    for k in range(-n, n + 1):
        v = k * step
        major = k % 2 == 0
        col = (255, 220, 0) if k % 10 == 0 else ((200, 160, 0) if major else (120, 90, 0))
        cv2.line(im, P(v, -1), P(v, 1), col, 1, cv2.LINE_AA)
        cv2.line(im, P(-1, v), P(1, v), col, 1, cv2.LINE_AA)
        if major:
            lab_ = ('%.1f' % v).replace('0.', '.')
            for yy in (-0.98, 0.0, 0.96):
                cv2.putText(im, lab_, (P(v, yy)[0] + 2, P(v, yy)[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
            for xx in (-0.99, 0.0, 0.9):
                cv2.putText(im, lab_, (P(xx, v)[0] + 2, P(xx, v)[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
    if extra:
        for poly, closed in extra:
            cv2.polylines(im, [np.array([P(x, y) for x, y in poly], np.int32)], closed, (255, 0, 255), 2, cv2.LINE_AA)
    if halves:
        cv2.imwrite(out_prefix + '_top.jpg', im[: size // 2 + 20], [cv2.IMWRITE_JPEG_QUALITY, 88])
        cv2.imwrite(out_prefix + '_bot.jpg', im[size // 2 - 20:], [cv2.IMWRITE_JPEG_QUALITY, 88])
    else:
        cv2.imwrite(out_prefix + '.jpg', cv2.resize(im, (1100, 1100)), [cv2.IMWRITE_JPEG_QUALITY, 88])


def fit_rete_pose(i, ks=None, rots=None, verbose=False):
    """Search scale k (rete radius / mater radius) and rotation of the
    photographed rete by maximising the image gradient along the predicted
    ecliptic circle (both edges of the band) and the rim."""
    from astrolabe import ecliptic_circle
    img, cx, cy, r = rete_frame(i, k=1.0)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (3, 3), 0)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = np.hypot(gx, gy)
    sp = spec_of(i)
    dm = Dims(sp)
    ec, er = ecliptic_circle(dm)
    ecn = ec[1] / dm.R_cap; ern = er / dm.R_cap
    wn = min(0.13, max(3.0 / dm.R_cap, 0.10))
    t = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    h, w = mag.shape
    def samp(xs, ys):
        X = cx + xs * r; Y = cy - ys * r
        ok = (X >= 0) & (X < w - 1) & (Y >= 0) & (Y < h - 1)
        return mag[Y[ok].astype(int), X[ok].astype(int)].mean() if ok.any() else 0
    ks = ks if ks is not None else np.arange(0.70, 0.95, 0.005)
    rots = rots if rots is not None else np.arange(0, 360, 1.0)
    best = (-1, None, None)
    for k in ks:
        for rot in rots:
            a = math.radians(rot)
            c = (ecn * k * math.cos(a), ecn * k * math.sin(a))
            s1 = samp(c[0] + ern * k * np.cos(t), c[1] + ern * k * np.sin(t))
            s2 = samp(c[0] + (ern - wn) * k * np.cos(t), c[1] + (ern - wn) * k * np.sin(t))
            sc = s1 + s2
            if sc > best[0]:
                best = (sc, k, rot)
    return best


def pose_overlay(i, k, rot):
    """polylines (mater units) of predicted rim, ecliptic band and star dots."""
    from astrolabe import ecliptic_circle
    ec_, er_, _, req, stars = astro_overlay(i, rot)
    sp = spec_of(i)
    dm = Dims(sp)
    wn = min(0.13, max(3.0 / dm.R_cap, 0.10))
    t = np.linspace(0, 2 * np.pi, 200)
    polys = []
    for rad, c in ((1.0, (0, 0)), (er_, ec_), (er_ - wn, ec_)):
        polys.append(([((c[0] + rad * math.cos(a)) * k, (c[1] + rad * math.sin(a)) * k) for a in t], True))
    for la, p in stars:
        if math.hypot(*p) < 1.0:
            polys.append(([((p[0] + 0.012 * math.cos(a)) * k, (p[1] + 0.012 * math.sin(a)) * k) for a in t[::10]], True))
    return polys


def check_overlay(i, out):
    """our rete outline drawn back onto the photograph of the book."""
    import rete_manual
    from astrolabe import make_rete
    from geom import PolarProj
    sp = spec_of(i)
    dm = Dims(sp)
    if sp.get('rete_d'):
        dm.R_cap = min(sp['rete_d'] / 2, dm.R_cap); dm.proj = PolarProj(dm.R_cap, dm.eps)
    m = rete_manual.R[i]
    d = make_rete(dm, sp)
    g = d.geom
    a = math.radians(m['rot'] - 90)
    polys = []
    for p in (g.geoms if hasattr(g, 'geoms') else [g]):
        for ring in [p.exterior] + list(p.interiors):
            pts = []
            for x, y in ring.coords:
                x, y = x / dm.R_cap, y / dm.R_cap
                x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
                pts.append((x * m['k'], y * m['k']))
            polys.append((pts, True))
    grid_m(i, out, extra=polys, halves=False, step=0.1)
