"""
Core drawing engine for the astrolabe workshop drawings.

All geometry is in millimetres, mathematical orientation (x to the right,
y upwards), origin at the centre of the part.  A `Drawing` collects exact
primitives (true circles / arcs / lines / polylines) on named layers so that
they can be written 1:1 to CNC files (SVG in mm and DXF with real ARC/CIRCLE
entities) and also rendered in a "hand drawn" ink style for the craftsman.
"""
import math, os, random, functools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, '..', 'fonts')

# ----------------------------------------------------------------- layers
# name: (svg colour, dxf aci colour, meaning)
LAYERS = {
    'CUT_OUTER': ('#ff0000', 1, 'قص خارجي - المحيط الخارجي للقطعة'),
    'CUT_INNER': ('#ff00ff', 6, 'قص داخلي - فتحات وثقوب وتفريغ'),
    'ENGRAVE':   ('#000000', 7, 'حفر خطوط - تدريج ومنحنيات'),
    'ENGRAVE_FINE': ('#555555', 8, 'حفر خفيف - خطوط ثانوية'),
    'TEXT':      ('#0000ff', 5, 'حفر كتابة - حروف وأرقام (محيطات مغلقة)'),
    'GUIDE':     ('#00aa00', 3, 'خطوط مساعدة - لا تُحفر'),
    'BEND':      ('#ff9900', 30, 'خط ثني'),
}

DEG = math.pi / 180.0


def rot(p, ang_deg, c=(0, 0)):
    a = ang_deg * DEG
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def polar(r, ang_deg, c=(0, 0)):
    return (c[0] + r * math.cos(ang_deg * DEG), c[1] + r * math.sin(ang_deg * DEG))


# ----------------------------------------------------------------- text
class Font:
    def __init__(self, path):
        from fontTools.ttLib import TTFont
        import uharfbuzz as hb
        self.path = path
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.upem = self.tt['head'].unitsPerEm
        with open(path, 'rb') as f:
            data = f.read()
        self.hbface = hb.Face(data)
        self.hbfont = hb.Font(self.hbface)
        self.order = self.tt.getGlyphOrder()
        self.cache = {}

    def glyph_polys(self, gid):
        if gid in self.cache:
            return self.cache[gid]
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        name = self.order[gid]
        pen = DecomposingRecordingPen(self.gs)
        self.gs[name].draw(pen)
        polys, cur = [], []
        last = (0, 0)
        for op, args in pen.value:
            if op == 'moveTo':
                if cur:
                    polys.append(cur)
                cur = [args[0]]
                last = args[0]
            elif op == 'lineTo':
                cur.append(args[0]); last = args[0]
            elif op == 'qCurveTo':
                pts = list(args)
                # implied on-curve points between consecutive off-curve points
                offs, on = pts[:-1], pts[-1]
                if on is None:  # closed contour of only off-curve points
                    on = ((offs[0][0] + offs[-1][0]) / 2, (offs[0][1] + offs[-1][1]) / 2)
                    cur.append(on); last = on
                seq = []
                for i, o in enumerate(offs):
                    if i < len(offs) - 1:
                        n = offs[i + 1]
                        seq.append((o, ((o[0] + n[0]) / 2, (o[1] + n[1]) / 2)))
                    else:
                        seq.append((o, on))
                for ctrl, end in seq:
                    for t in (0.25, 0.5, 0.75, 1.0):
                        x = (1 - t) ** 2 * last[0] + 2 * (1 - t) * t * ctrl[0] + t * t * end[0]
                        y = (1 - t) ** 2 * last[1] + 2 * (1 - t) * t * ctrl[1] + t * t * end[1]
                        cur.append((x, y))
                    last = end
            elif op == 'curveTo':
                c1, c2, end = args
                for t in (0.2, 0.4, 0.6, 0.8, 1.0):
                    mt = 1 - t
                    x = mt ** 3 * last[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * end[0]
                    y = mt ** 3 * last[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * end[1]
                    cur.append((x, y))
                last = end
            elif op in ('closePath', 'endPath'):
                if cur:
                    polys.append(cur)
                cur = []
        if cur:
            polys.append(cur)
        self.cache[gid] = polys
        return polys

    def _shape_run(self, text, rtl):
        import uharfbuzz as hb
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        buf.direction = 'rtl' if rtl else 'ltr'
        hb.shape(self.hbfont, buf, {})
        return list(zip(buf.glyph_infos, buf.glyph_positions))

    def shape(self, text):
        """Shape with a simplified Unicode bidi algorithm (enough for labels:
        Arabic, Latin, European / Arabic-Indic digits and punctuation)."""
        def cls(ch):
            o = ord(ch)
            if 0x30 <= o <= 0x39 or 0x660 <= o <= 0x669 or 0x6F0 <= o <= 0x6F9:
                return 'N'
            if (0x600 <= o <= 0x6FF) or (0x750 <= o <= 0x77F) or (0xFB50 <= o <= 0xFEFF):
                return 'R' if o not in (0x66B, 0x66C) else 'X'
            if ch.isalpha():
                return 'L'
            return 'X'
        cl = [cls(c) for c in text]
        base_rtl = 'R' in cl
        # numbers absorb separators placed between digits
        for i in range(1, len(text) - 1):
            if cl[i] == 'X' and text[i] in '.,:٫٬°\'' and cl[i - 1] == 'N' and cl[i + 1] == 'N':
                cl[i] = 'N'
        for i in range(len(text)):
            if cl[i] == 'X' and text[i] in '°\'' and i > 0 and cl[i - 1] == 'N':
                cl[i] = 'N'
        strong = ['R' if c in ('R',) or (c == 'N' and base_rtl) else c for c in cl]
        dirs = []
        for i, c in enumerate(cl):
            if c == 'R':
                dirs.append('R')
            elif c in ('L', 'N'):
                dirs.append('L')
            else:
                # neutral: look at neighbours (numbers count as R in an RTL paragraph)
                j = i - 1
                while j >= 0 and cl[j] == 'X':
                    j -= 1
                k = i + 1
                while k < len(cl) and cl[k] == 'X':
                    k += 1
                left = strong[j] if j >= 0 else ('R' if base_rtl else 'L')
                right = strong[k] if k < len(cl) else ('R' if base_rtl else 'L')
                if left == right:
                    dirs.append('R' if left == 'R' else 'L')
                else:
                    dirs.append('R' if base_rtl else 'L')
        runs = []
        for ch, d in zip(text, dirs):
            if runs and runs[-1][1] == d:
                runs[-1][0] += ch
            else:
                runs.append([ch, d])
        if base_rtl:
            runs = runs[::-1]
        out, x = [], 0
        for t, d in runs:
            for info, pos in self._shape_run(t, d == 'R'):
                out.append((info.codepoint, x + pos.x_offset, pos.y_offset, pos.x_advance))
                x += pos.x_advance
        return out, x


@functools.lru_cache(None)
def get_font(bold=False):
    return Font(os.path.join(FONT_DIR, 'Amiri-Bold.ttf' if bold else 'Amiri-Regular.ttf'))


# ----------------------------------------------------------------- abjad / numerals
ABJAD = [(1000, 'غ'), (900, 'ظ'), (800, 'ض'), (700, 'ذ'), (600, 'خ'), (500, 'ث'), (400, 'ت'),
         (300, 'ش'), (200, 'ر'), (100, 'ق'), (90, 'ص'), (80, 'ف'), (70, 'ع'), (60, 'س'),
         (50, 'ن'), (40, 'م'), (30, 'ل'), (20, 'ك'), (10, 'ي'), (9, 'ط'), (8, 'ح'), (7, 'ز'),
         (6, 'و'), (5, 'ه'), (4, 'د'), (3, 'ج'), (2, 'ب'), (1, 'ا')]


def abjad(n):
    """Arabic alphabetical numerals (hisab al-jummal) as engraved on astrolabes."""
    n = int(round(n))
    if n == 0:
        return '٠'
    s = ''
    for v, ch in ABJAD:
        while n >= v:
            s += ch
            n -= v
    return s


def roman(n):
    vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'),
            (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    s = ''
    for v, r in vals:
        while n >= v:
            s += r; n -= v
    return s


def num(n, style):
    if style == 'abjad':
        return abjad(n)
    if style == 'roman':
        return roman(int(n))
    if style == 'indic':
        return str(int(n)).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
    return str(int(n))


def dms(v, style='latin'):
    d = int(math.floor(v + 1e-9)); m = int(round((v - d) * 60))
    if m == 60:
        d += 1; m = 0
    if style == 'abjad':
        return abjad(d) + ('' if m == 0 else ' ' + abjad(m))
    return f"{d}°" + (f"{m:02d}'" if m else '')


# ----------------------------------------------------------------- Drawing
class Drawing:
    def __init__(self, name='part', title=''):
        self.name = name
        self.title = title
        self.items = []
        self.notes = []          # human readable specs for the sheet
        self.material = ''
        self.thickness = None

    # basic primitives ---------------------------------------------------
    def circle(self, c, r, layer='ENGRAVE', w=None):
        if r > 1e-6:
            self.items.append(dict(t='circle', c=tuple(c), r=float(r), layer=layer, w=w))

    def arc(self, c, r, a0, a1, layer='ENGRAVE', w=None):
        """CCW arc from a0 to a1 (degrees)."""
        while a1 <= a0:
            a1 += 360
        if a1 - a0 >= 359.999:
            return self.circle(c, r, layer, w)
        if r > 1e-6 and a1 - a0 > 1e-4:
            self.items.append(dict(t='arc', c=tuple(c), r=float(r), a0=float(a0), a1=float(a1), layer=layer, w=w))

    def line(self, p0, p1, layer='ENGRAVE', w=None):
        self.items.append(dict(t='poly', p=[tuple(p0), tuple(p1)], closed=False, layer=layer, w=w))

    def poly(self, pts, closed=False, layer='ENGRAVE', w=None, fill=False):
        pts = [tuple(map(float, p)) for p in pts]
        if len(pts) >= 2:
            self.items.append(dict(t='poly', p=pts, closed=closed, layer=layer, w=w, fill=fill))

    def hole(self, c, d):
        self.circle(c, d / 2.0, 'CUT_INNER')

    def shape(self, geom, layer_outer='CUT_OUTER', layer_inner='CUT_INNER'):
        """Add a shapely (Multi)Polygon as cut contours.  Runs of vertices
        that lie on a common circle are written back as TRUE arcs/circles,
        so circular edges are exact in the CNC files."""
        from shapely.geometry import Polygon, MultiPolygon
        geoms = [geom] if isinstance(geom, Polygon) else list(getattr(geom, 'geoms', []))
        for g in geoms:
            if g.is_empty or not isinstance(g, Polygon):
                continue
            self._ring(list(g.exterior.coords)[:-1], layer_outer)
            for ring in g.interiors:
                self._ring(list(ring.coords)[:-1], layer_inner)

    def _ring(self, pts, layer):
        n = len(pts)
        if n < 3:
            return
        P = [tuple(map(float, p)) for p in pts]
        # whole ring on one circle?
        fc = _fit3(P[0], P[n // 3], P[2 * n // 3])
        if fc and n >= 8 and all(abs(math.hypot(x - fc[0][0], y - fc[0][1]) - fc[1]) <= _tol(fc[1]) for x, y in P):
            self.circle(fc[0], fc[1], layer)
            return
        # rotate start to a sharp corner so that arcs are not split
        def turn(i):
            a, b, c = P[i - 1], P[i], P[(i + 1) % n]
            v1 = (b[0] - a[0], b[1] - a[1]); v2 = (c[0] - b[0], c[1] - b[1])
            l1, l2 = math.hypot(*v1), math.hypot(*v2)
            if l1 == 0 or l2 == 0:
                return 0
            return abs(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1]))
        k = max(range(n), key=turn)
        P = P[k:] + P[:k]
        P.append(P[0])
        i, line = 0, [P[0]]
        m = len(P)
        while i < m - 1:
            best = None
            j = i + 3
            while j < m:
                fc = _fit3(P[i], P[(i + j) // 2], P[j])
                if not fc or fc[1] > 5e4:
                    break
                c, r = fc
                ok = True
                sgn = 0
                for t in range(i, j + 1):
                    if abs(math.hypot(P[t][0] - c[0], P[t][1] - c[1]) - r) > _tol(r):
                        ok = False; break
                    if t > i:
                        a0 = math.atan2(P[t - 1][1] - c[1], P[t - 1][0] - c[0])
                        a1 = math.atan2(P[t][1] - c[1], P[t][0] - c[0])
                        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
                        if abs(da) > math.radians(25) or abs(da) < 1e-12:
                            ok = False; break
                        s_ = 1 if da > 0 else -1
                        if sgn and s_ != sgn:
                            ok = False; break
                        sgn = s_
                if not ok:
                    break
                best = (j, c, r, sgn)
                j += 1
            if best:
                if len(line) > 1:
                    self.poly(line, False, layer)
                j, c, r, sgn = best
                a0 = math.degrees(math.atan2(P[i][1] - c[1], P[i][0] - c[0]))
                a1 = math.degrees(math.atan2(P[j][1] - c[1], P[j][0] - c[0]))
                if sgn > 0:
                    self.arc(c, r, a0, a1, layer)
                else:
                    self.arc(c, r, a1, a0, layer)
                i = j
                line = [P[i]]
            else:
                line.append(P[i + 1])
                i += 1
        if len(line) > 1:
            self.poly(line, False, layer)

    # text ---------------------------------------------------------------
    def _glyph_runs(self, text, size, bold=False):
        f = get_font(bold)
        glyphs, adv = f.shape(text)
        s = size / f.upem / 0.62   # size ~ height of a tall letter (alef) in mm
        return f, glyphs, adv * s, s

    def text(self, text, pos, size, ang=0, anchor='middle', layer='TEXT', bold=False, valign='middle'):
        if not text:
            return
        f, glyphs, width, s = self._glyph_runs(text, size, bold)
        ox = {'middle': -width / 2, 'start': 0, 'end': -width}[anchor]
        oy = {'middle': -0.30 * size / 0.62 * 0.62, 'baseline': 0, 'top': -size}[valign]
        for gid, gx, gy, _ in glyphs:
            for pl in f.glyph_polys(gid):
                pts = [rot((ox + (gx + x) * s, oy + (gy + y) * s), ang) for x, y in pl]
                pts = [(pos[0] + x, pos[1] + y) for x, y in pts]
                if len(pts) > 2:
                    self.poly(pts, True, layer, fill=True)

    def text_arc(self, text, c, r, ang_center, size, layer='TEXT', flip=None, bold=False):
        """Text written along a circle of radius r (baseline centre line),
        centred at angle ang_center (deg).  Upright for reader standing outside
        the top half; automatically flipped on the lower half."""
        if not text:
            return
        f, glyphs, width, s = self._glyph_runs(text, size, bold)
        if flip is None:
            a = (ang_center % 360)
            flip = 180 < a < 360
        sign = 1 if flip else -1
        yoff = -0.30 * size
        for gid, gx, gy, adv in glyphs:
            for pl in f.glyph_polys(gid):
                pts = []
                for x, y in pl:
                    X = (gx + x) * s - width / 2.0
                    Y = (gy + y) * s + yoff
                    if flip:
                        rr = r - Y
                    else:
                        rr = r + Y
                    ang = ang_center + sign * (X / r) / DEG
                    pts.append(polar(rr, ang, c))
                if len(pts) > 2:
                    self.poly(pts, True, layer, fill=True)

    def text_width(self, text, size, bold=False):
        _, _, w, _ = self._glyph_runs(text, size, bold)
        return w

    # transforms ----------------------------------------------------------
    def merge(self, other, dx=0, dy=0, ang=0, scale=1.0):
        for it in other.items:
            self.items.append(transform_item(it, dx, dy, ang, scale))

    def bbox(self, layers=None):
        xs, ys = [], []
        for it in self.items:
            if layers and it['layer'] not in layers:
                continue
            for p in item_points(it, coarse=True):
                xs.append(p[0]); ys.append(p[1])
        if not xs:
            return (0, 0, 1, 1)
        return (min(xs), min(ys), max(xs), max(ys))


def _tol(r):
    return 2e-4 + 2e-6 * r


def _fit3(p1, p2, p3):
    ax, ay = p1; bx, by = p2; cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def transform_item(it, dx, dy, ang, scale, mirror=False):
    it = dict(it)
    def T(p):
        x, y = p[0] * scale, p[1] * scale
        if mirror:
            x = -x
        x, y = rot((x, y), ang)
        return (x + dx, y + dy)
    if it['t'] in ('circle', 'arc'):
        it['c'] = T(it['c']); it['r'] = it['r'] * scale
        if it['t'] == 'arc':
            a0, a1 = it['a0'], it['a1']
            if mirror:
                a0, a1 = 180 - a1, 180 - a0
            it['a0'], it['a1'] = a0 + ang, a1 + ang
    else:
        it['p'] = [T(p) for p in it['p']]
    return it


def item_points(it, step=0.4, coarse=False):
    if it['t'] == 'circle':
        n = 16 if coarse else max(24, int(2 * math.pi * it['r'] / step))
        return [polar(it['r'], 360.0 * i / n, it['c']) for i in range(n + 1)]
    if it['t'] == 'arc':
        span = it['a1'] - it['a0']
        n = 8 if coarse else max(4, int(span * DEG * it['r'] / step))
        return [polar(it['r'], it['a0'] + span * i / n, it['c']) for i in range(n + 1)]
    pts = list(it['p'])
    if it.get('closed'):
        pts = pts + [pts[0]]
    return pts


# ----------------------------------------------------------------- exporters
def _fmt(v):
    return f"{v:.3f}".rstrip('0').rstrip('.')


def write_svg_cnc(d, path, margin=5):
    """1:1 CNC / laser SVG.  Units are millimetres.  One Inkscape layer per
    machining operation."""
    x0, y0, x1, y1 = d.bbox()
    x0 -= margin; y0 -= margin; x1 += margin; y1 += margin
    W, H = x1 - x0, y1 - y0
    def P(p):
        return (p[0] - x0, y1 - p[1])
    out = [f'<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{_fmt(W)}mm" height="{_fmt(H)}mm" viewBox="0 0 {_fmt(W)} {_fmt(H)}">',
           f'<title>{d.title}</title>']
    for lname, (col, _, desc) in LAYERS.items():
        its = [i for i in d.items if i['layer'] == lname]
        if not its:
            continue
        sw = 0.1
        out.append(f'<g inkscape:groupmode="layer" inkscape:label="{lname}" id="{lname}" fill="none" stroke="{col}" stroke-width="{sw}">')
        out.append(f'<desc>{desc}</desc>')
        for it in its:
            if it['t'] == 'circle':
                c = P(it['c'])
                out.append(f'<circle cx="{_fmt(c[0])}" cy="{_fmt(c[1])}" r="{_fmt(it["r"])}"/>')
            elif it['t'] == 'arc':
                p0 = P(polar(it['r'], it['a0'], it['c'])); p1 = P(polar(it['r'], it['a1'], it['c']))
                large = 1 if (it['a1'] - it['a0']) > 180 else 0
                # CCW in math coords == sweep-flag 0 in SVG (y down)
                out.append(f'<path d="M{_fmt(p0[0])},{_fmt(p0[1])} A{_fmt(it["r"])},{_fmt(it["r"])} 0 {large} 0 {_fmt(p1[0])},{_fmt(p1[1])}"/>')
            else:
                pts = [P(p) for p in it['p']]
                dd = 'M' + ' L'.join(f'{_fmt(x)},{_fmt(y)}' for x, y in pts) + (' Z' if it.get('closed') else '')
                out.append(f'<path d="{dd}"/>')
        out.append('</g>')
    out.append('</svg>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))


def write_dxf(d, path):
    import ezdxf
    doc = ezdxf.new('R2010', setup=False)
    doc.units = ezdxf.units.MM
    doc.header['$INSUNITS'] = 4
    msp = doc.modelspace()
    for lname, (_, aci, desc) in LAYERS.items():
        doc.layers.add(lname, color=aci)
    for it in d.items:
        a = {'layer': it['layer']}
        if it['t'] == 'circle':
            msp.add_circle(it['c'], it['r'], dxfattribs=a)
        elif it['t'] == 'arc':
            msp.add_arc(it['c'], it['r'], it['a0'] % 360, it['a1'] % 360, dxfattribs=a)
        else:
            msp.add_lwpolyline([(round(x, 4), round(y, 4)) for x, y in it['p']], close=bool(it.get('closed')), dxfattribs=a)
    doc.saveas(path)


# ----------------------------------------------------------------- hand drawn renderer
class Jitter:
    """Smooth low-frequency wobble that imitates a steady hand with a pen."""
    def __init__(self, seed, amp, wavelength):
        rnd = random.Random(seed)
        self.terms = [(rnd.uniform(0.6, 1.4) * 2 * math.pi / wavelength * k, rnd.uniform(0, 2 * math.pi), amp / k)
                      for k in (1, 2.3, 5.1)]

    def __call__(self, s):
        return sum(a * math.sin(f * s + ph) for f, ph, a in self.terms)


def hand_paths(d, scale, rng, amp=0.35, layers_skip=('GUIDE',)):
    """Return list of (svg path string, stroke width, is_fill, colour) in sheet px."""
    res = []
    for it in d.items:
        if it['layer'] in layers_skip:
            continue
        pts = item_points(it, step=max(0.25, 1.2 / scale))
        if it.get('fill'):
            dd = 'M' + ' L'.join(f'{x*scale:.2f},{-y*scale:.2f}' for x, y in pts) + 'Z'
            res.append((dd, 0, True, it['layer']))
            continue
        if len(pts) < 2:
            continue
        # wobble perpendicular to the stroke, in sheet units
        jit = Jitter(rng.random() * 1e6, amp, rng.uniform(25, 60))
        P = np.array(pts) * scale
        P[:, 1] *= -1
        seg = np.diff(P, axis=0)
        L = np.hypot(seg[:, 0], seg[:, 1])
        s = np.concatenate([[0], np.cumsum(L)])
        tang = np.vstack([seg, seg[-1:]])
        nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
        nl = np.hypot(nrm[:, 0], nrm[:, 1]); nl[nl == 0] = 1
        nrm /= nl[:, None]
        off = np.array([jit(v) for v in s])
        # lines fade in/out at their ends like a pen stroke
        Q = P + nrm * off[:, None]
        # slight overshoot at the ends of open strokes
        if not it.get('closed') and it['t'] != 'circle' and len(Q) >= 2 and s[-1] > 3:
            ext = rng.uniform(0.2, 0.9)
            d0 = Q[0] - Q[1]; d0 /= (np.hypot(*d0) or 1)
            d1 = Q[-1] - Q[-2]; d1 /= (np.hypot(*d1) or 1)
            Q = np.vstack([Q[0] + d0 * ext, Q, Q[-1] + d1 * ext])
        dd = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in Q) + ('Z' if it.get('closed') else '')
        base = {'CUT_OUTER': 1.6, 'CUT_INNER': 1.2, 'ENGRAVE': 0.75, 'ENGRAVE_FINE': 0.45, 'BEND': 0.7}.get(it['layer'], 0.7)
        if it.get('w'):
            base = it['w']
        res.append((dd, base * rng.uniform(0.85, 1.15), False, it['layer']))
    return res
