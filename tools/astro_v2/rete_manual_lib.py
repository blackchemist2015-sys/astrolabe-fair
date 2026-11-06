"""Geometry of retes traced by hand from the photographs of the book.

Every rete is described in rete_manual.py in normalised units of the
photograph (outer rim of the rete = 1, pin = origin, y up, as in the
rectified photo).  Elements:
  ('rim', w)                         outer (Capricorn) ring of width w
  ('ecl', (cx, cy), r, w)            ecliptic ring: outer radius r, width w
  ('ring', (cx, cy), r, w)           any ring (outer radius r, width w)
  ('arc', (cx, cy), r, w, a0, a1)    part of a ring (degrees, CCW)
  ('bar', [pts], w)                  straight band through the points
  ('curve', [pts], w)                smooth band (Catmull-Rom) through points
  ('taper', [pts], w0, w1)           smooth band tapering from w0 to w1
  ('disc', (cx, cy), r)              solid disc / boss
  ('boss', (cx, cy), r)              disc with a small rivet hole (engraved)
  ('leaf', base, tip, w)             almond pointer, tip = star
  ('flame', base, tip, w)            flame (wavy) pointer
  ('dagger', base, tip, w)           straight triangular pointer
  ('hook', base, tip, w)             curved hook pointer
  ('poly', [pts])                    solid polygon
  ('cut', [pts])                     polygon removed (opening)
  ('hub', r)                         central hub
"""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union


def catmull(pts, n=16):
    P = [np.array(p, float) for p in pts]
    if len(P) < 3:
        return [tuple(p) for p in P]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    out.append(tuple(P[-2]))
    return out


def pointer(kind, base, tip, w):
    bx, by = base; tx, ty = tip
    L = math.hypot(tx - bx, ty - by) or 1e-6
    ux, uy = (tx - bx) / L, (ty - by) / L
    nx, ny = -uy, ux
    pts_l, pts_r = [], []
    for t in np.linspace(0, 1, 30):
        if kind == 'dagger':
            wv = w / 2 * (1 - t)
            off = 0
        elif kind == 'leaf':
            wv = w / 2 * math.sin(math.pi * min(1, t * 1.0 + 0.0)) ** 0.7 * (1 - 0.5 * t) + w * 0.12 * (1 - t)
            off = 0
        elif kind == 'flame':
            wv = w / 2 * (1 - t) ** 0.8
            off = w * 0.35 * math.sin(t * math.pi * 1.5) * (1 - t)
        else:  # hook
            wv = w / 2 * (1 - t)
            off = w * 0.9 * math.sin(t * math.pi / 2) * (1 - t) * 2
        cx, cy = bx + ux * L * t + nx * off, by + uy * L * t + ny * off
        pts_l.append((cx + nx * wv, cy + ny * wv))
        pts_r.append((cx - nx * wv, cy - ny * wv))
    return Polygon(pts_l + pts_r[::-1]).buffer(0)


def build(spec):
    """returns (shapely geometry in normalised units, list of pointer tips,
    ecliptic description or None, bosses)"""
    g, cuts, tips, bosses = [], [], [], []
    ecl = None
    for e in spec['elems']:
        k = e[0]
        if k == 'rim':
            w = e[1]
            g.append(Point(0, 0).buffer(1.0, resolution=128).difference(Point(0, 0).buffer(1.0 - w, resolution=128)))
        elif k in ('ecl', 'ring'):
            c, r, w = e[1], e[2], e[3]
            g.append(Point(c).buffer(r, resolution=128).difference(Point(c).buffer(r - w, resolution=128)))
            if k == 'ecl':
                ecl = (c, r, w)
        elif k == 'arc':
            c, r, w, a0, a1 = e[1:]
            a = np.radians(np.linspace(a0, a1, 90))
            mid = r - w / 2
            g.append(LineString([(c[0] + mid * math.cos(t), c[1] + mid * math.sin(t)) for t in a]).buffer(w / 2, cap_style=2))
        elif k == 'bar':
            g.append(LineString(e[1]).buffer(e[2] / 2, cap_style=2, join_style=2))
        elif k == 'curve':
            g.append(LineString(catmull(e[1])).buffer(e[2] / 2))
        elif k == 'taper':
            pts = catmull(e[1]); w0, w1 = e[2], e[3]
            n = len(pts)
            for i in range(n - 1):
                ww = w0 + (w1 - w0) * i / (n - 1)
                g.append(LineString([pts[i], pts[i + 1]]).buffer(ww / 2))
        elif k == 'disc':
            g.append(Point(e[1]).buffer(e[2]))
        elif k == 'boss':
            g.append(Point(e[1]).buffer(e[2])); bosses.append((e[1], e[2]))
        elif k in ('leaf', 'flame', 'dagger', 'hook'):
            g.append(pointer(k, e[1], e[2], e[3])); tips.append((k, e[1], e[2], e[3]))
        elif k == 'poly':
            g.append(Polygon(e[1]).buffer(0))
        elif k == 'cut':
            cuts.append(Polygon(e[1]).buffer(0))
        elif k == 'sun':
            c, r0, r1, n = e[1], e[2], e[3], e[4]
            pts = []
            for j in range(2 * n):
                rr = r1 if j % 2 == 0 else r0
                a = math.pi * j / n
                pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
            g.append(Polygon(pts).buffer(0))
        elif k == 'lobed':
            c, r, n = e[1], e[2], e[3]
            g.append(unary_union([Point(c).buffer(r * 0.7)] + [Point(c[0] + r * 0.55 * math.cos(2 * math.pi * j / n + math.pi / 2),
                                                                     c[1] + r * 0.55 * math.sin(2 * math.pi * j / n + math.pi / 2)).buffer(r * 0.42) for j in range(n)]))
        elif k == 'leafo':
            g.append(pointer('leaf', e[1], e[2], e[3]))
        elif k == 'hub':
            g.append(Point(0, 0).buffer(e[1], resolution=64))
    geo = unary_union(g)
    if cuts:
        geo = geo.difference(unary_union(cuts))
    geo = geo.buffer(0.004).buffer(-0.004).intersection(Point(0, 0).buffer(1.0, resolution=256))
    return geo, tips, ecl, bosses


def outline_polys(spec):
    geo, tips, ecl, bosses = build(spec)
    out = []
    for p in (geo.geoms if hasattr(geo, 'geoms') else [geo]):
        out.append((list(p.exterior.coords), True))
        for i in p.interiors:
            out.append((list(i.coords), True))
    return out


def transform(elems, k, rot):
    """photo (mater units, arbitrary rotation) -> rete units (rim = 1,
    Capricorn solstice at the top)."""
    a = math.radians(90 - rot)
    ca, sa = math.cos(a), math.sin(a)
    def P(p):
        x, y = p[0] / k, p[1] / k
        return (x * ca - y * sa, x * sa + y * ca)
    def L(v):
        return v / k
    out = []
    for e in elems:
        t = e[0]
        if t in ('bar', 'curve'):
            out.append((t, [P(p) for p in e[1]], L(e[2])))
        elif t == 'taper':
            out.append((t, [P(p) for p in e[1]], L(e[2]), L(e[3])))
        elif t in ('ring', 'ecl'):
            out.append((t, P(e[1]), L(e[2]), L(e[3])))
        elif t == 'arc':
            out.append((t, P(e[1]), L(e[2]), L(e[3]), e[4] + 90 - rot, e[5] + 90 - rot))
        elif t in ('disc', 'boss'):
            out.append((t, P(e[1]), L(e[2])))
        elif t in ('leaf', 'flame', 'dagger', 'hook', 'leafo'):
            out.append((t, P(e[1]), P(e[2]), L(e[3])))
        elif t in ('poly', 'cut'):
            out.append((t, [P(p) for p in e[1]]))
        elif t == 'sun':
            out.append((t, P(e[1]), L(e[2]), L(e[3]), e[4]))
        elif t == 'lobed':
            out.append((t, P(e[1]), L(e[2]), e[3]))
        elif t == 'hub':
            out.append((t, L(e[1])))
    return out


def skeleton(elems):
    """centre lines of the structural elements (to anchor the pointers)."""
    sk = []
    for e in elems:
        t = e[0]
        if t == 'bar':
            sk.append(LineString(e[1]))
        elif t == 'curve':
            sk.append(LineString(catmull(e[1])))
        elif t == 'ring':
            sk.append(Point(e[1]).buffer(e[2] - e[3] / 2).exterior)
        elif t == 'arc':
            c, r, w, a0, a1 = e[1:]
            sk.append(LineString([(c[0] + (r - w / 2) * math.cos(math.radians(a)), c[1] + (r - w / 2) * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 40)]))
        elif t in ('disc', 'boss'):
            sk.append(Point(e[1]).buffer(e[2] * 0.5).exterior)
    return sk
