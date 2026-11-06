"""Planispheric astrolabe parts: mater, limb ring, throne, shackle & ring,
plates (tympans), rete, alidade, rule, pin and wedge, and back designs."""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

from core import Drawing, polar, DEG, abjad, num, dms, rot
from geom import (PolarProj, EquinoxProj, sphere_circle, draw_projected, arc_intervals, seg_intervals,
                  horizon_frame, eq_vec, altaz_vec, ecl_to_eq, precess_star, sun_longitude, julian_day,
                  MONTH_DAYS, unit)
from stars import STARS

SIGNS_AR = ['الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة', 'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت']
SIGNS_LA = ['ARIES', 'TAVRVS', 'GEMINI', 'CANCER', 'LEO', 'VIRGO', 'LIBRA', 'SCORPIO', 'SAGITTARIVS', 'CAPRICORNVS', 'AQVARIVS', 'PISCES']
MONTHS_LA = ['IANVARIVS', 'FEBRVARIVS', 'MARTIVS', 'APRILIS', 'MAIVS', 'IVNIVS', 'IVLIVS', 'AVGVSTVS', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
MONTHS_SY = ['كانون الآخر', 'شباط', 'آذار', 'نيسان', 'أيار', 'حزيران', 'تموز', 'آب', 'أيلول', 'تشرين الأول', 'تشرين الآخر', 'كانون الأول']
PLANETS_AR = {'Sa': 'زحل', 'Ju': 'المشتري', 'Ma': 'المريخ', 'So': 'الشمس', 'Ve': 'الزهرة', 'Me': 'عطارد', 'Lu': 'القمر'}
PLANETS_LA = {'Sa': 'SAT', 'Ju': 'IOV', 'Ma': 'MAR', 'So': 'SOL', 'Ve': 'VEN', 'Me': 'MER', 'Lu': 'LVN'}
CHALDEAN = ['Ma', 'So', 'Ve', 'Me', 'Lu', 'Sa', 'Ju']
TRIPL = {0: ['So', 'Ju', 'Sa'], 1: ['Ve', 'Lu', 'Ma'], 2: ['Sa', 'Me', 'Ju'], 3: ['Ve', 'Ma', 'Lu']}


def clamp(v, a, b):
    return max(a, min(b, v))


# =========================================================================== dims
class Dims:
    def __init__(self, spec):
        D = spec['D']
        self.D = D
        self.R = D / 2.0
        self.limb_w = clamp(0.085 * self.R, 4.0, 26.0)
        self.Rp = self.R - self.limb_w                 # seat of the plates
        self.R_cap = self.Rp - clamp(0.015 * self.R, 0.6, 4.0)
        self.pin_d = clamp(0.03 * D, 2.5, 12.0)
        self.eps = spec.get('eps', 23 + 35 / 60)
        self.proj = PolarProj(self.R_cap, self.eps)
        t = spec.get('t', None)
        self.t_mater = clamp(D / 55.0, 1.5, 8.0)
        self.t_limb = clamp(D / 70.0, 1.2, 8.0)
        self.t_plate = clamp(D / 130.0, 0.8, 3.0)
        self.t_rete = clamp(D / 110.0, 1.0, 4.0)
        self.t_alid = clamp(D / 80.0, 1.2, 5.0)


def style_of(spec):
    return spec.get('style', 'islamic')


def numstyle(spec):
    return spec.get('num', 'abjad')


def is_latin(spec):
    return spec.get('script', 'arabic') == 'latin'


# =========================================================================== throne / outline
def throne_param(dm, spec):
    R, D = dm.R, dm.D
    st = style_of(spec)
    w = 0.40 * D if D < 300 else 0.30 * D
    h = 0.17 * D if D < 300 else 0.12 * D
    hw = w / 2
    y0 = math.sqrt(max(R * R - hw * hw, 0))
    yb = y0 - 0.04 * D
    if st == 'islamic':
        body = Polygon([(-hw, yb), (hw, yb), (hw * 0.95, y0 + 0.02 * D), (w * 0.30, y0 + h * 0.42), (w * 0.12, y0 + h * 0.70),
                        (-w * 0.12, y0 + h * 0.70), (-w * 0.30, y0 + h * 0.42), (-hw * 0.95, y0 + 0.02 * D)])
        lobes = [Point(s * w * 0.37, y0 + 0.03 * D).buffer(w * 0.12) for s in (-1, 1)]
        lobes += [Point(s * w * 0.22, y0 + h * 0.45).buffer(w * 0.11) for s in (-1, 1)]
        lobes += [Point(0, y0 + h * 0.80).buffer(w * 0.13)]
        sh = unary_union([body] + lobes)
        holes = [(s * w * 0.22, y0 + h * 0.45, w * 0.085) for s in (-1, 1)] + [(0, y0 + h * 0.30, w * 0.10)]
    else:  # gothic / renaissance: pointed arch with side scrolls
        pts = [(-hw, yb), (hw, yb), (hw * 0.9, y0 + h * 0.15)]
        for k in range(0, 21):
            a = k / 20.0
            x = hw * 0.9 * (1 - a)
            yy = y0 + h * 0.15 + (h * 0.55) * math.sin(a * math.pi / 2)
            pts.append((x, yy))
        pts = pts + [(-x, y) for x, y in reversed(pts[3:-1])] + [(-hw * 0.9, y0 + h * 0.15)]
        body = Polygon(pts)
        lobes = [Point(s * hw * 0.92, y0 + h * 0.18).buffer(w * 0.07) for s in (-1, 1)]
        lobes += [Point(0, y0 + h * 0.80).buffer(w * 0.12)]
        sh = unary_union([body] + lobes)
        holes = [(s * w * 0.18, y0 + h * 0.32, w * 0.07) for s in (-1, 1)]
    pin = (0, y0 + h * 0.80)
    return sh.buffer(0.3).buffer(-0.3), holes, pin, (y0, h, w)


TRACED_DIR = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'traced')


def load_traced(spec, kind):
    import os, json
    p = os.path.join(TRACED_DIR, f"{spec['id']}_{kind}.json")
    if spec.get('traced') is False or not os.path.exists(p):
        return None
    return json.load(open(p))


def traced_polygon(data, scale):
    outers = [Polygon([(x * scale, y * scale) for x, y in p['pts']]).buffer(0) for p in data['polys'] if not p['hole']]
    holes = [Polygon([(x * scale, y * scale) for x, y in p['pts']]).buffer(0) for p in data['polys'] if p['hole']]
    g = unary_union(outers)
    if holes:
        g = g.difference(unary_union(holes))
    return g


def throne_shape(dm, spec):
    """Throne (kursi): traced from the photograph of the book when
    available, otherwise the parametric design."""
    data = load_traced(spec, 'throne')
    if data is None or not data['polys']:
        return throne_param(dm, spec)
    th = traced_polygon(data, dm.R)
    th = th.buffer(0.15).buffer(-0.15)
    minx, miny, maxx, maxy = th.bounds
    y0 = dm.R
    h = max(maxy - y0, 1.0)
    w = maxx - minx
    # suspension hole for the shackle near the top, only where the metal allows it
    hd = clamp(0.02 * dm.D, 1.5, 6)
    pin = None
    y = maxy - hd
    while y > y0 + hd:
        if th.buffer(-0.0).contains(Point(0, y).buffer(hd / 2 + max(1.0, 0.6 * hd))):
            pin = (0, y)
            break
        y -= 0.25
    return th, [], pin, (y0, h, w)


def mater_outline(dm, spec):
    if spec.get('shape') == '12gon':
        Rv = dm.R / math.cos(math.pi / 12)
        disc = Polygon([polar(Rv, 15 + 30 * i) for i in range(12)])
    else:
        disc = Point(0, 0).buffer(dm.R, resolution=256)
    th, holes, pin, geo = throne_shape(dm, spec)
    return unary_union([disc, th]), holes, pin, geo


def _cut_outline(Dr, shape):
    """Write a shapely polygon as cut lines, but replace the circular parts by
    true arcs where possible (keeps the CNC file exact)."""
    Dr.shape(shape)


# =========================================================================== scales
def degree_ring(Dr, r_out, r_in, start_ang, step_lab, labeller, size, direction=-1, span=360, zero_at=0,
                minor=1, ccw_numbers=False):
    """Degree scale between r_out (ticks start) and r_in (inner edge).
    direction -1: values increase clockwise."""
    w = r_out - r_in
    n = int(round(span / minor))
    Dr.circle((0, 0), r_out, 'ENGRAVE')
    Dr.circle((0, 0), r_out - 0.35 * w, 'ENGRAVE')
    Dr.circle((0, 0), r_in, 'ENGRAVE')
    for i in range(n + (0 if span == 360 else 1)):
        v = i * minor
        a = start_ang + direction * v
        if abs(v % 10) < 1e-9 or abs(v % 10 - 10) < 1e-9:
            l = 0.35 * w
        elif abs(v % 5) < 1e-9:
            l = 0.25 * w
        else:
            l = 0.15 * w
        Dr.line(polar(r_out, a), polar(r_out - l, a), 'ENGRAVE' if l > 0.2 * w else 'ENGRAVE_FINE')
    for v in np.arange(0, span + 1e-9, step_lab):
        if span == 360 and v >= 360:
            continue
        a = start_ang + direction * v
        lab = labeller(v)
        if lab:
            Dr.text_arc(lab, (0, 0), r_in + 0.30 * w, a, size)


def limb_scale(Dr, dm, spec):
    """Limb (hujra) scale: 360 degrees, 5 degree numbering; European
    instruments add the 24 hour ring."""
    ns = numstyle(spec)
    r_out = dm.R - 0.06 * dm.limb_w
    r_in = dm.Rp + 0.06 * dm.limb_w
    size = clamp(0.24 * dm.limb_w, 0.9, 6)
    if spec.get('limb_hours'):
        rm = r_in + 0.45 * (r_out - r_in)
        Dr.circle((0, 0), r_out, 'ENGRAVE')
        Dr.circle((0, 0), rm, 'ENGRAVE')
        for h in range(24):
            a = 90 - 15 * h
            Dr.line(polar(rm, a), polar(r_out, a), 'ENGRAVE')
            for q in range(1, 4):
                Dr.line(polar(r_out, a - 3.75 * q), polar(r_out - 0.25 * (r_out - rm), a - 3.75 * q), 'ENGRAVE_FINE')
            hr = 12 if h % 12 == 0 else h % 12
            Dr.text_arc(num(hr, 'roman' if ns != 'abjad' else 'abjad'), (0, 0), (rm + r_out) / 2, a - 7.5, size * 0.9)
        r_out = rm
    lab = (lambda v: num(v, ns)) if ns != 'triple' else (lambda v: abjad(v))
    step = 5 if dm.D >= 100 else 10
    degree_ring(Dr, r_out, r_in, 90, step, lambda v: num(v if v else 360, ns if ns != 'triple' else 'abjad'),
                size * 0.85 if not spec.get('limb_hours') else size * 0.75, direction=-1)


# =========================================================================== plate
def plate_lines(Dr, dm, phi, spec, half=None, zone=None, labels=True, hours=True):
    """Engrave the coordinate lines of latitude phi.  half = 'L'/'R' limits
    the drawing to one side of the meridian (folded / double plates)."""
    P = dm.proj
    R_cap = dm.R_cap
    Z, S, W = horizon_frame(phi)
    def side_ok(p):
        if half == 'L':
            return p[0] <= 1e-9
        if half == 'R':
            return p[0] >= -1e-9
        return True
    def in_cap(p):
        return p[0] * p[0] + p[1] * p[1] <= R_cap * R_cap and side_ok(p)
    def above(p):
        return in_cap(p) and float(np.dot(P.inv(p), Z)) >= -1e-12
    def below(p):
        return in_cap(p) and float(np.dot(P.inv(p), Z)) <= 1e-12

    D = dm.D
    a_step = spec.get('alm_step') or (10 if D < 100 else 6 if D < 160 else 3 if D < 250 else 2 if D < 400 else 1)
    z_step = spec.get('az_step') or (15 if D < 100 else 10 if D < 250 else 5)
    # horizon & almucantars
    for h in np.arange(0, 90, a_step):
        sc = sphere_circle(Z, 90 - h, P)
        lay = 'ENGRAVE' if (h % (a_step * 5 if a_step < 5 else 30) == 0 or h == 0) or a_step >= 6 else 'ENGRAVE_FINE'
        draw_projected(Dr, sc, in_cap, lay, w=1.4 if h == 0 else None)
    # zenith
    zp = P.P(Z)
    Dr.circle(zp, clamp(0.006 * D, 0.4, 2), 'ENGRAVE')
    # twilight line (18 deg below horizon)
    if spec.get('twilight', True) and phi < 60:
        sc = sphere_circle(-Z, 72, P)
        draw_projected(Dr, sc, in_cap, 'ENGRAVE_FINE')
    # azimuths (above horizon)
    for A in np.arange(z_step, 180, z_step):
        if abs(A - 90) < 1e-9 or True:
            Dvec = math.cos(A * DEG) * S + math.sin(A * DEG) * W
            axis = np.cross(Z, Dvec)
            sc = sphere_circle(axis, 90, P)
            draw_projected(Dr, sc, above, 'ENGRAVE' if abs(A - 90) < 1e-6 else 'ENGRAVE_FINE')
            # mirror (east side) – same circle family with -A
            Dvec = math.cos(A * DEG) * S - math.sin(A * DEG) * W
            sc = sphere_circle(np.cross(Z, Dvec), 90, P)
            draw_projected(Dr, sc, above, 'ENGRAVE' if abs(A - 90) < 1e-6 else 'ENGRAVE_FINE')
    # unequal hours below the horizon
    hours_ok = hours and abs(math.tan(phi * DEG) * math.tan(dm.eps * DEG)) < 1
    hour_pts = {}
    if hours_ok:
        for n in range(1, 12):
            pts = []
            for d in (-dm.eps, 0, dm.eps):
                H0 = math.acos(-math.tan(phi * DEG) * math.tan(d * DEG)) / DEG
                H = H0 + n / 12.0 * (360 - 2 * H0)
                pts.append(P.P_Hd(H, d))
            hour_pts[n] = pts
            from geom import fit_circle
            fc = fit_circle(*pts)
            if fc is None:
                pa, pb = pts[0], pts[2]
                for s0, s1 in seg_intervals(pa, pb, lambda p: side_ok(p)):
                    Dr.line(s0, s1, 'ENGRAVE')
            else:
                c, r = fc
                a0 = math.atan2(pts[0][1] - c[1], pts[0][0] - c[0]) / DEG
                am = math.atan2(pts[1][1] - c[1], pts[1][0] - c[0]) / DEG
                a1 = math.atan2(pts[2][1] - c[1], pts[2][0] - c[0]) / DEG
                # choose the arc a0->a1 that contains am
                def ccw_between(a, b, m):
                    return ((m - a) % 360) <= ((b - a) % 360)
                if ccw_between(a0, a1, am):
                    s, e = a0, a1
                else:
                    s, e = a1, a0
                if e < s:
                    e += 360
                for x0, x1 in arc_intervals(c, r, side_ok, n=200, a_from=s, a_to=e):
                    Dr.arc(c, r, x0, x1, 'ENGRAVE')
    # meridian & east-west line
    for s0, s1 in seg_intervals((0, -R_cap), (0, R_cap), lambda p: True):
        Dr.line(s0, s1, 'ENGRAVE')
    for s0, s1 in seg_intervals((-R_cap, 0), (R_cap, 0), side_ok):
        Dr.line(s0, s1, 'ENGRAVE')
    # labels -------------------------------------------------------------
    if not labels:
        return
    ns = numstyle(spec)
    if ns == 'triple':
        ns = 'abjad'
    size = clamp(0.022 * D, 0.9, 6)
    # almucantar numbers along the meridian (south side)
    lab_step = a_step * (2 if a_step < 6 else 1)
    if a_step <= 2:
        lab_step = 10
    for h in np.arange(lab_step, 90, lab_step):
        sc = sphere_circle(Z, 90 - h, P)
        y = P.P(altaz_vec(phi, h, 0))[1]
        if abs(y) < R_cap * 0.97:
            x = (size * 0.9) if half != 'L' else -(size * 0.9)
            Dr.text(num(h, ns), (x if half != 'R' else size * 0.9, y + size * 0.55), size * 0.75)
    # hour numbers near the Capricorn circle
    if hours_ok:
        for n in range(1, 13):
            d = -dm.eps
            H0 = math.acos(-math.tan(phi * DEG) * math.tan(d * DEG)) / DEG
            H = H0 + (n - 0.5) / 12.0 * (360 - 2 * H0)
            p = P.P_Hd(H, d * 0.93)
            if side_ok(p):
                Dr.text(num(n, ns), p, size * 0.8)
    # legend: latitude and longest day
    longest = 2 * math.acos(min(1, max(-1, -math.tan(phi * DEG) * math.tan(dm.eps * DEG)))) / DEG / 15.0
    if is_latin(spec):
        leg1 = 'LATITVDO ' + dms(phi)
        leg2 = 'HORAE ' + f"{int(longest)}° {int(round((longest % 1) * 60)):02d}'"
    else:
        leg1 = 'لعرض ' + dms(phi, 'abjad')
        leg2 = 'ساعات أطول نهار ' + dms(longest, 'abjad')
    yy = -P.R_can * 0.45
    xx = 0 if half is None else (-R_cap * 0.33 if half == 'L' else R_cap * 0.33)
    Dr.text(leg1, (xx, yy), size)
    Dr.text(leg2, (xx, yy - size * 1.9), size * 0.75)


def plate_frame(Dr, dm, spec, phi_label=None):
    """outline of a plate with key tab, centre hole, tropic & equator circles."""
    Rpl = dm.Rp - 0.15
    tabw = clamp(0.035 * dm.D, 2.0, 12.0)
    shape = unary_union([Point(0, 0).buffer(Rpl, resolution=256),
                         box(-tabw / 2, Rpl - 1.0, tabw / 2, Rpl + clamp(0.012 * dm.D, 1.0, 4.0))])
    Dr.shape(shape)
    Dr.hole((0, 0), dm.pin_d + 0.1)
    P = dm.proj
    Dr.circle((0, 0), dm.R_cap, 'ENGRAVE', w=1.2)
    Dr.circle((0, 0), P.R_eq, 'ENGRAVE')
    Dr.circle((0, 0), P.R_can, 'ENGRAVE')


def make_plate(dm, spec, phi, half=None, phi2=None, title='', mater_face=False):
    Dr = Drawing(title=title)
    if not mater_face:
        plate_frame(Dr, dm, spec)
    else:
        P = dm.proj
        Dr.circle((0, 0), dm.R_cap, 'ENGRAVE', w=1.2)
        Dr.circle((0, 0), P.R_eq, 'ENGRAVE')
        Dr.circle((0, 0), P.R_can, 'ENGRAVE')
    if phi2 is None:
        plate_lines(Dr, dm, phi, spec, half=half)
    else:  # doubly folded: left half phi, right half phi2
        plate_lines(Dr, dm, phi, spec, half='L')
        plate_lines(Dr, dm, phi2, spec, half='R')
    return Dr


def make_horizons_plate(dm, spec, title=''):
    """'Plate of horizons' (safihat al-afaq): horizon arcs of many latitudes,
    one family per quadrant."""
    Dr = Drawing(title=title)
    plate_frame(Dr, dm, spec)
    P = dm.proj
    ns = numstyle(spec)
    size = clamp(0.02 * dm.D, 0.9, 5)
    for s_q in range(4):
        sx = 1 if s_q in (0, 3) else -1
        sy = 1 if s_q in (0, 1) else -1
        def inq(p, sx=sx, sy=sy):
            return p[0] * sx >= 0 and p[1] * sy >= 0 and p[0] ** 2 + p[1] ** 2 <= dm.R_cap ** 2
        for phi in range(6, 67, 6):
            Z, S, W = horizon_frame(phi)
            sc = sphere_circle(Z, 90, P)
            c, r = sc[1], sc[2]
            # reflect into quadrant by drawing reflected circle
            for cc in [(c[0] * sx, c[1] * sy), (c[0], c[1])]:
                for a0, a1 in arc_intervals(cc, r, inq):
                    Dr.arc(cc, r, a0, a1, 'ENGRAVE_FINE')
    Dr.line((-dm.R_cap, 0), (dm.R_cap, 0)); Dr.line((0, -dm.R_cap), (0, dm.R_cap))
    Dr.text('صفيحة الآفاق' if not is_latin(spec) else 'TABVLA HORIZONTVM', (0, -dm.proj.R_can * 0.4), size)
    return Dr


# =========================================================================== rete
def select_stars(spec, dm, n):
    year = spec.get('year', 1000)
    out = []
    for ra, de, ar, la in STARS:
        a, d = precess_star(ra, de, year, dm.eps)
        if d < -dm.eps + 1.5 or d > 78:
            continue
        out.append((a, d, ar, la))
        if len(out) >= n:
            break
    return out


def rete_xy(dm, ra, dec):
    r = dm.proj.r(dec)
    th = ra - 180
    return polar(r, th)


def ecliptic_circle(dm):
    P = dm.proj
    yc = (P.R_cap - P.R_can) / 2
    return (0.0, yc), (P.R_cap + P.R_can) / 2


def connect_islands(g, w, R):
    """every loose piece of the rete is tied to the main body by a short
    straight stem (a cut part must be one piece); very small loose bits are
    dropped."""
    from shapely.ops import nearest_points
    for _ in range(30):
        parts = list(g.geoms) if hasattr(g, 'geoms') else [g]
        if len(parts) <= 1:
            return g
        parts.sort(key=lambda p: p.area, reverse=True)
        main, rest = parts[0], parts[1:]
        add = []
        keep = [main]
        for p in rest:
            if p.area < (0.015 * R) ** 2:
                continue
            a, b = nearest_points(p, main)
            add.append(LineString([a, b]).buffer(w / 2))
            keep.append(p)
        g = unary_union(keep + add).intersection(Point(0, 0).buffer(R, resolution=256))
    return g


def make_traced_rete(dm, spec, data, title=''):
    """Rete traced from the photograph (silver rete of the Hama astrolabe):
    scaled so that its outer ring is the Capricorn circle of the model; an
    exact outer ring and the central hub are added for strength."""
    Dr = Drawing(title=title)
    R = dm.R_cap
    g = traced_polygon(data, R)
    w_ring = clamp(0.045 * R, 1.3, 14)
    hub_r = clamp(0.085 * R, 2.5, 22)
    ring = Point(0, 0).buffer(R, resolution=256).difference(Point(0, 0).buffer(R - w_ring, resolution=256))
    g = unary_union([g, ring, Point(0, 0).buffer(hub_r, resolution=64)]).intersection(Point(0, 0).buffer(R, resolution=256))
    # drop specks and pin-holes too small to cut
    from shapely.geometry import MultiPolygon
    parts = [p for p in (g.geoms if hasattr(g, 'geoms') else [g]) if p.area > (0.02 * R) ** 2]
    clean = []
    for p in parts:
        ints = [i for i in p.interiors if Polygon(i).area > (0.025 * R) ** 2]
        clean.append(Polygon(p.exterior, ints))
    g = unary_union(clean)
    Dr.shape(g)
    Dr.hole((0, 0), dm.pin_d + 0.1)
    Dr.star_table = []
    Dr.traced = True
    return Dr


def make_rete(dm, spec, title='', rete_diam=None):
    data = load_traced(spec, 'rete')
    if data is not None:
        return make_traced_rete(dm, spec, data, title)
    Dr = Drawing(title=title)
    P = dm.proj
    R = dm.R_cap
    if rete_diam:
        pass  # rete diameter in the book equals the Capricorn circle of the model
    st = style_of(spec)
    k = R / 60.0
    w_ring = clamp(0.05 * R, 1.3, 14) if not spec.get('rete_hours') else clamp(0.11 * R, 3, 20)
    w_ecl = clamp(0.13 * R, 3.0, 36)
    w_bar = clamp(0.04 * R, 1.2, 10)
    w_stem = clamp(0.03 * R, 1.0, 7)
    hub_r = clamp(0.085 * R, 2.5, 22)
    ec, er = ecliptic_circle(dm)
    geoms = []
    outer = Point(0, 0).buffer(R + 0.0, resolution=256)
    ring = outer.difference(Point(0, 0).buffer(R - w_ring, resolution=256))
    geoms.append(ring)
    ecl = Point(ec).buffer(er, resolution=256).difference(Point(ec).buffer(er - w_ecl, resolution=256))
    geoms.append(ecl)
    geoms.append(Point(0, 0).buffer(hub_r, resolution=64))
    skel = []  # (shapely line) skeleton for anchoring star stems
    skel.append(Point(0, 0).buffer(R - w_ring / 2).exterior)
    skel.append(Point(ec).buffer(er - w_ecl / 2).exterior)
    manual = None
    if spec.get('manual_rete', __import__('os').environ.get('MANUAL_RETE') == '1'):
        try:
            import rete_manual, rete_manual_lib as RL
            manual = rete_manual.R.get(spec['id'])
        except ImportError:
            manual = None
    if manual is not None:
        from shapely import affinity as _aff
        k_ = manual['k']
        if manual.get('rim') is None:
            geoms.remove(ring)
            skel.pop(0)
        else:
            w_new = max(1.2, manual['rim'] / k_ * R)
            geoms.remove(ring)
            ring = outer.difference(Point(0, 0).buffer(R - w_new, resolution=256))
            geoms.insert(0, ring)
            skel[0] = Point(0, 0).buffer(R - w_new / 2).exterior
            w_ring = w_new
        tel = RL.transform(manual['elems'], k_, manual['rot'])
        mg, _, _, bosses = RL.build({'elems': tel})
        geoms.append(_aff.scale(mg, R, R, origin=(0, 0)))
        for sk_ in RL.skeleton(tel):
            skel.append(_aff.scale(sk_, R, R, origin=(0, 0)))
        Dr._bosses = [((c[0] * R, c[1] * R), r * R) for c, r in bosses]
    elif st == 'islamic':
        # meridian bar (lower) + lower equator arc + short equatorial bar
        b1 = LineString([(0, -R), (0, R)]).buffer(w_bar / 2)
        arc_pts = [polar(P.R_eq, a) for a in np.linspace(195, 345, 60)]
        eqarc = LineString(arc_pts)
        geoms += [b1, eqarc.buffer(w_bar / 2)]
        xb = math.sqrt(max(P.R_eq ** 2 * 0.0 + (er - w_ecl) ** 2 - ec[1] ** 2, 0))
        geoms.append(LineString([(-R, 0), (R, 0)]).buffer(w_bar / 2).intersection(Point(0, 0).buffer(P.R_eq * 0.55)))
        skel += [LineString([(0, -R), (0, R)]), eqarc]
    else:
        cross = unary_union([LineString([(0, -R), (0, R)]).buffer(w_bar / 2), LineString([(-R, 0), (R, 0)]).buffer(w_bar / 2)])
        geoms.append(cross)
        skel += [LineString([(0, -R), (0, R)]), LineString([(-R, 0), (R, 0)])]
        if st in ('gothic', 'renaissance'):
            # quatrefoil / ribbon ornament inside the lower half
            for cx in (-0.42 * R, 0.42 * R):
                c0 = (cx, -0.42 * R)
                qf = unary_union([Point(c0[0] + dx, c0[1] + dy).buffer(0.09 * R).exterior.buffer(w_bar * 0.35)
                                  for dx, dy in ((0.07 * R, 0), (-0.07 * R, 0), (0, 0.07 * R), (0, -0.07 * R))])
                geoms.append(qf)
                geoms.append(LineString([c0, (cx * 1.6, -0.42 * R * 1.6)]).buffer(w_stem / 2))
                geoms.append(LineString([c0, (0, -0.42 * R)]).buffer(w_stem / 2))
    skel_u = unary_union(skel)
    if manual is not None:
        skel_u = unary_union([s_ for s_ in skel if True])
    # thumb knob (lower, inside the ring)
    if manual is None:
        knob_c = polar(R - w_ring - 0.06 * R, -70)
        geoms.append(Point(knob_c).buffer(0.05 * R))
        geoms.append(LineString([knob_c, polar(R - w_ring / 2, -70)]).buffer(w_bar / 2))

    stars = select_stars(spec, dm, spec.get('stars', 20))
    star_info = []
    leaf_L = clamp(0.20 * R, 6, 60)
    leaf_W = clamp(0.065 * R, 2.2, 18)
    body_union = unary_union(geoms)
    for ra, de, ar, la in stars:
        sp = rete_xy(dm, ra, de)
        spt = Point(sp)
        if body_union.buffer(-0.2).contains(spt):
            star_info.append((sp, None, ar, la, ra, de))
            continue
        if spt.distance(Point(0, 0)) > R - w_ring - 0.4:
            star_info.append((sp, None, ar, la, ra, de))
            continue
        # nearest skeleton point
        from shapely.ops import nearest_points
        anc = nearest_points(skel_u, spt)[0]
        ax_, ay_ = anc.x, anc.y
        dx, dy = sp[0] - ax_, sp[1] - ay_
        dist = math.hypot(dx, dy) or 1e-6
        ux, uy = dx / dist, dy / dist
        L = leaf_L
        base = (sp[0] - ux * L, sp[1] - uy * L)
        # leaf (almond) pointer: tip exactly at the star
        nx, ny = -uy, ux
        lp = []
        for t in np.linspace(0, 1, 24):
            wv = leaf_W / 2 * math.sin(math.pi * t) ** 0.8 * (1 - 0.55 * t)
            lp.append((base[0] + ux * L * t + nx * wv, base[1] + uy * L * t + ny * wv))
        for t in np.linspace(1, 0, 24):
            wv = leaf_W / 2 * math.sin(math.pi * t) ** 0.8 * (1 - 0.55 * t)
            lp.append((base[0] + ux * L * t - nx * wv, base[1] + uy * L * t - ny * wv))
        leaf = Polygon(lp).buffer(0)
        if manual is not None and manual.get('ptr', 'leaf') != 'leaf':
            leaf = RL.pointer(manual['ptr'], base, sp, leaf_W)
        # gently curved stem from anchor to the leaf base
        mid = ((ax_ + base[0]) / 2 + nx * 0.12 * dist, (ay_ + base[1]) / 2 + ny * 0.12 * dist)
        stem_pts = [((1 - t) ** 2 * ax_ + 2 * (1 - t) * t * mid[0] + t * t * base[0],
                     (1 - t) ** 2 * ay_ + 2 * (1 - t) * t * mid[1] + t * t * base[1]) for t in np.linspace(0, 1, 20)]
        geoms.append(leaf)
        if dist > L * 1.05:
            geoms.append(LineString(stem_pts).buffer(w_stem / 2))
            # small ornamental ring on long stems
            if dist > 0.3 * R and st == 'islamic' and manual is None:
                m2 = stem_pts[10]
                geoms.append(Point(m2).buffer(w_stem * 1.4).difference(Point(m2).buffer(w_stem * 0.6)))
        star_info.append((sp, (base, (ux, uy), L), ar, la, ra, de))
    rete = unary_union(geoms).buffer(0.25).buffer(-0.25)
    rete = rete.intersection(Point(0, 0).buffer(R, resolution=256))
    rete = connect_islands(rete, w_stem, R)
    Dr.geom = rete
    Dr.shape(rete)
    Dr.hole((0, 0), dm.pin_d + 0.1)
    for c_, r_ in getattr(Dr, '_bosses', []):
        Dr.circle(c_, max(0.3, r_ * 0.3), 'ENGRAVE')
    Dr.manual = manual is not None
    # ---- engraving on the ecliptic ring
    ns = numstyle(spec)
    if ns == 'triple':
        ns = 'abjad'
    def ray_circle(theta, c, r):
        # intersection of ray from origin at angle theta with circle (c,r), farthest root
        ux, uy = math.cos(theta * DEG), math.sin(theta * DEG)
        b = -2 * (ux * c[0] + uy * c[1])
        cc = c[0] ** 2 + c[1] ** 2 - r * r
        disc = b * b - 4 * cc
        if disc < 0:
            return None
        t = (-b + math.sqrt(disc)) / 2
        return (ux * t, uy * t)
    r_o, r_i = er, er - w_ecl
    r_t = er - 0.42 * w_ecl  # end of ticks zone
    Dr.circle(ec, r_t, 'ENGRAVE')
    step = 1 if R >= 45 else 2
    for lam in np.arange(0, 360, step):
        ra, de = ecl_to_eq(lam, 0, dm.eps)
        th = ra - 180
        p_out = ray_circle(th, ec, r_o)
        if lam % 30 == 0:
            p_in = ray_circle(th, ec, r_i)
            lay = 'ENGRAVE'
        elif lam % 10 == 0:
            p_in = ray_circle(th, ec, r_o - 0.42 * w_ecl); lay = 'ENGRAVE'
        elif lam % 5 == 0:
            p_in = ray_circle(th, ec, r_o - 0.30 * w_ecl); lay = 'ENGRAVE_FINE'
        else:
            p_in = ray_circle(th, ec, r_o - 0.18 * w_ecl); lay = 'ENGRAVE_FINE'
        if p_out and p_in:
            Dr.line(p_out, p_in, lay)
    names = SIGNS_LA if is_latin(spec) else SIGNS_AR
    size = clamp(0.30 * w_ecl, 0.9, 9)
    for i, nm in enumerate(names):
        lam = i * 30 + 15
        ra, de = ecl_to_eq(lam, 0, dm.eps)
        p = ray_circle(ra - 180, ec, (r_t + r_i) / 2)
        ang = math.atan2(p[1] - ec[1], p[0] - ec[0]) / DEG
        tw = Dr.text_width(nm, size)
        sz = size if tw < 0.9 * (math.pi * 2 * r_i / 12) else size * 0.9 * (math.pi * 2 * r_i / 12) / tw
        Dr.text_arc(nm, ec, (r_t + r_i) / 2 - 0.15 * size, ang, sz)
    # star names inside leaves + marking dot at the tip
    names_out = []
    for sp, leafd, ar, la, ra, de in star_info:
        nm = la if is_latin(spec) else ar
        names_out.append((nm, ra, de))
        Dr.circle(sp, clamp(0.006 * R, 0.25, 1.2), 'ENGRAVE')
        if leafd is None:
            continue
        base, (ux, uy), L = leafd
        cx, cy = base[0] + ux * L * 0.42, base[1] + uy * L * 0.42
        ang = math.atan2(uy, ux) / DEG
        if ang > 90 or ang < -90:
            ang += 180
        tsz = leaf_W * 0.38
        tw = Dr.text_width(nm, tsz)
        if tw > L * 0.62:
            tsz = tsz * L * 0.62 / tw
        if tsz >= 0.7 and not body_union.intersects(Point(cx, cy).buffer(L * 0.32)):
            Dr.text(nm, (cx, cy), tsz, ang)
    if spec.get('rete_hours'):
        ro, ri = R - 0.3, R - w_ring + 0.3
        Dr.circle((0, 0), (ro + ri) / 2, 'ENGRAVE')
        for h in range(24):
            a = 90 - 15 * h
            Dr.line(polar(ro, a), polar(ri, a), 'ENGRAVE')
            for q in (1, 2, 3):
                Dr.line(polar(ro, a - 3.75 * q), polar((ro + ri) / 2, a - 3.75 * q), 'ENGRAVE_FINE')
            Dr.text_arc(num(12 if h % 12 == 0 else h % 12, 'roman'), (0, 0), ri + 0.22 * (ro - ri), a - 7.5, 0.3 * (ro - ri))
    Dr.star_table = names_out
    return Dr


def make_grid_rete(dm, spec, title=''):
    """Rete of the universal astrolabe (Ibn al-Sarraj): the lower half carries
    an openwork 5-degree grid of the universal projection, the upper half the
    ecliptic and the star pointers."""
    base = make_rete(dm, spec, title=title)
    R = dm.R_cap
    E = EquinoxProj(R)
    bars = []
    wb = clamp(0.012 * R, 0.6, 2)
    for k in range(-85, 90, 5):
        for (axis, rho) in ((np.array([0, 0, 1.0]), 90 - k), (np.array([math.sin(k * DEG), -math.cos(k * DEG), 0]), 90)):
            sc = sphere_circle(axis, rho, E)
            if sc[0] == 'circle':
                c, r = sc[1], sc[2]
                pts = [polar(r, a, c) for a in np.linspace(0, 360, 721)]
            else:
                p, d = sc[1], sc[2]
                pts = [(p[0] - d[0] * 2 * R, p[1] - d[1] * 2 * R), (p[0] + d[0] * 2 * R, p[1] + d[1] * 2 * R)]
            bars.append(LineString(pts).buffer(wb / 2))
    lower = Point(0, 0).buffer(R).intersection(box(-R, -R, R, 0))
    grid = unary_union(bars).intersection(lower)
    shp = unary_union([base.geom, grid])
    base.items = [it for it in base.items if it['layer'] not in ('CUT_OUTER', 'CUT_INNER')]
    base.shape(shp)
    base.hole((0, 0), dm.pin_d + 0.1)
    return base


# =========================================================================== back designs
def back_rings(Dr, dm, spec, features):
    """Concentric rings on the back, from the rim inwards.  Returns inner radius."""
    R = dm.R
    ns = numstyle(spec)
    if ns == 'triple':
        ns = 'abjad'
    lat = is_latin(spec) or spec.get('back_latin')
    r = R - 0.02 * R
    size = clamp(0.028 * R * 2 / 2, 0.9, 7)
    year = spec.get('year', 1000)
    def lam_angle(lam):
        return 180 - lam
    for f in features:
        if f == 'alt':
            w = clamp(0.075 * R, 3, 20)
            Dr.circle((0, 0), r, 'ENGRAVE')
            degree_ring(Dr, r, r - w, 0, 10, lambda v: num(v if v <= 90 else (180 - v if v <= 180 else (v - 180 if v <= 270 else 360 - v)), ns) if v % 90 != 0 else '',
                        size * 0.8, direction=1)
            r -= w
        elif f == 'alt90':
            # altitude quadrants in the two upper quadrants only
            w = clamp(0.075 * R, 3, 20)
            for start in (0, 180):
                for v in range(0, 91):
                    a = start + (v if start == 0 else -v) if False else (v if start == 0 else 180 - v)
                    l = w * (0.6 if v % 10 == 0 else 0.4 if v % 5 == 0 else 0.25)
                    Dr.line(polar(r, a), polar(r - l, a), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
                    if v % 10 == 0 and 0 < v < 90:
                        Dr.text_arc(num(v, ns), (0, 0), r - 0.78 * w, a, size * 0.75)
            Dr.arc((0, 0), r, 0, 180); Dr.arc((0, 0), r - w, 0, 180)
            r -= w
        elif f == 'zodiac':
            w = clamp(0.11 * R, 4, 30)
            Dr.circle((0, 0), r); Dr.circle((0, 0), r - 0.35 * w); Dr.circle((0, 0), r - w)
            for lam in range(0, 360):
                a = lam_angle(lam)
                l = 0.35 * w if lam % 30 == 0 else (0.30 * w if lam % 10 == 0 else 0.22 * w if lam % 5 == 0 else 0.12 * w)
                if lam % 30 == 0:
                    Dr.line(polar(r, a), polar(r - w, a))
                else:
                    Dr.line(polar(r, a), polar(r - l, a), 'ENGRAVE_FINE' if lam % 5 else 'ENGRAVE')
            for i in range(12):
                for dv in (10, 20):
                    Dr.text_arc(num(dv, ns), (0, 0), r - 0.55 * w + 0.0, lam_angle(i * 30 + dv), size * 0.55)
                Dr.text_arc((SIGNS_LA if lat else SIGNS_AR)[i], (0, 0), r - 0.80 * w, lam_angle(i * 30 + 15), size * 0.85)
            r -= w
        elif f in ('decans', 'triplicities'):
            w = clamp(0.065 * R, 3, 18)
            Dr.circle((0, 0), r); Dr.circle((0, 0), r - w)
            P = PLANETS_LA if lat else PLANETS_AR
            if f == 'decans':
                for k in range(36):
                    Dr.line(polar(r, lam_angle(k * 10)), polar(r - w, lam_angle(k * 10)), 'ENGRAVE' if k % 3 == 0 else 'ENGRAVE_FINE')
                    Dr.text_arc(P[CHALDEAN[k % 7]], (0, 0), r - 0.62 * w, lam_angle(k * 10 + 5), size * 0.55)
            else:
                for s in range(12):
                    Dr.line(polar(r, lam_angle(s * 30)), polar(r - w, lam_angle(s * 30)))
                    lords = TRIPL[s % 4]
                    Dr.text_arc(' '.join(P[x] for x in lords), (0, 0), r - 0.62 * w, lam_angle(s * 30 + 15), size * 0.5)
            r -= w
        elif f in ('calendar', 'calendar_syriac'):
            w = clamp(0.12 * R, 4, 30)
            Dr.circle((0, 0), r); Dr.circle((0, 0), r - 0.35 * w); Dr.circle((0, 0), r - w)
            y = year
            doy = 0
            names = MONTHS_SY if (f == 'calendar_syriac' or not lat) else MONTHS_LA
            for m in range(12):
                for dday in range(1, MONTH_DAYS[m] + 1):
                    jd = julian_day(y, m + 1, dday) + 0.5
                    lam = sun_longitude(jd)
                    a = lam_angle(lam)
                    if dday == 1:
                        Dr.line(polar(r, a), polar(r - w, a))
                    else:
                        l = 0.30 * w if dday % 10 == 0 else 0.22 * w if dday % 5 == 0 else 0.12 * w
                        Dr.line(polar(r, a), polar(r - l, a), 'ENGRAVE' if dday % 5 == 0 else 'ENGRAVE_FINE')
                    if dday in (10, 20, 30):
                        Dr.text_arc(num(dday, ns), (0, 0), r - 0.55 * w, a, size * 0.5)
                jd = julian_day(y, m + 1, 15) + 0.5
                Dr.text_arc(names[m], (0, 0), r - 0.80 * w, lam_angle(sun_longitude(jd)), size * 0.75)
            r -= w
        elif f == 'shadow_ring':
            w = clamp(0.05 * R, 2, 12)
            Dr.circle((0, 0), r - w)
            r -= w
    return r


def shadow_squares(Dr, r_in, spec, n=12, y_top=0.0):
    s = r_in * 0.68
    ns = numstyle(spec)
    if ns == 'triple':
        ns = 'abjad'
    lat = is_latin(spec) or spec.get('back_latin')
    b = s * 0.13
    size = clamp(b * 0.6, 0.8, 6)
    y0 = y_top
    Dr.poly([(-s, y0), (-s, y0 - s), (s, y0 - s), (s, y0)], False)
    Dr.poly([(-s + b, y0), (-s + b, y0 - s + b), (s - b, y0 - s + b), (s - b, y0)], False)
    Dr.line((0, y0), (0, y0 - s))
    for k in range(1, n + 1):
        t = k / n * s
        L = 'ENGRAVE'
        # vertical sides
        Dr.line((-s, y0 - (s - t) * 0 - t * 0 - (s - t)), (-s + b, y0 - (s - t)), L)
        # bottom (both halves)
        Dr.line((-s + t, y0 - s), (-s + t, y0 - s + b), L)
        Dr.line((s - t, y0 - s), (s - t, y0 - s + b), L)
        Dr.line((s, y0 - (s - t)), (s - b, y0 - (s - t)), L)
        if k % 3 == 0 and k < n:
            Dr.text(num(k, ns), (-s + b / 2, y0 - (s - t) + size * 0.8), size)
            Dr.text(num(k, ns), (s - b / 2, y0 - (s - t) + size * 0.8), size)
            Dr.text(num(k, ns), (-s + t - size * 0.8, y0 - s + b / 2), size, 90)
            Dr.text(num(k, ns), (s - t + size * 0.8, y0 - s + b / 2), size, -90)
    if lat:
        Dr.text('VMBRA VERSA', (-s / 2, y0 - s / 2), size)
        Dr.text('VMBRA RECTA', (s / 2, y0 - s / 2), size)
    else:
        Dr.text('الظل المعكوس', (-s / 2, y0 - s / 2), size)
        Dr.text('الظل المستوي', (s / 2, y0 - s / 2), size)
    return s


def sine_quadrant(Dr, r_in, quad, spec, n=None, eps=23.583):
    """quad: (sx, sy) signs of the quadrant."""
    sx, sy = quad
    n = n or (60 if r_in > 40 else 30)
    ns = numstyle(spec)
    for k in range(1, n):
        t = r_in * k / n
        L = math.sqrt(r_in * r_in - t * t)
        lay = 'ENGRAVE' if k % 5 == 0 else 'ENGRAVE_FINE'
        Dr.line((sx * t, 0), (sx * t, sy * L), lay)
        Dr.line((0, sy * t), (sx * L, sy * t), lay)
    Dr.line((0, 0), (sx * r_in, 0)); Dr.line((0, 0), (0, sy * r_in))
    # semicircles on the two radii (for sine/cosine conversion)
    a0 = 0 if sx > 0 else 180
    c1 = (sx * r_in / 2, 0)
    for a0_, a1_ in arc_intervals(c1, r_in / 2, lambda p: p[1] * sy >= 0):
        Dr.arc(c1, r_in / 2, a0_, a1_)
    c2 = (0, sy * r_in / 2)
    for a0_, a1_ in arc_intervals(c2, r_in / 2, lambda p: p[0] * sx >= 0):
        Dr.arc(c2, r_in / 2, a0_, a1_)
    # arc of maximum declination
    rd = r_in * math.sin(eps * DEG)
    for a0_, a1_ in arc_intervals((0, 0), rd, lambda p: p[0] * sx >= 0 and p[1] * sy >= 0):
        Dr.arc((0, 0), rd, a0_, a1_, 'ENGRAVE')
    # degree scale on the arc (inside)
    for v in range(0, 91):
        a = math.atan2(sy * math.sin(v * DEG), sx * math.cos(v * DEG)) / DEG
        l = r_in * (0.05 if v % 10 == 0 else 0.035 if v % 5 == 0 else 0.02)
        Dr.line(polar(r_in, a), polar(r_in - l, a), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
    Dr.arc((0, 0), r_in, *sorted([math.atan2(0, sx) / DEG, math.atan2(sy, 0) / DEG]) if not (sx < 0 and sy < 0) else (180, 270))


def asr_curve(Dr, r_in, quad, phi_list=None):
    """Curve of the afternoon prayer: for each noon altitude Hm the point of
    the thread (at angle Hm) at distance R*sin(h_asr), cot h_asr = 1 + cot Hm."""
    sx, sy = quad
    pts = []
    for Hm in np.linspace(2, 90, 120):
        ha = math.atan(1 / (1 + 1 / math.tan(Hm * DEG)))
        rr = r_in * math.sin(ha)
        pts.append((sx * rr * math.cos(Hm * DEG), sy * rr * math.sin(Hm * DEG)))
    Dr.poly(pts, False, 'ENGRAVE')


def unequal_hours(Dr, r_in, quad, spec):
    sx, sy = quad
    ns = numstyle(spec)
    size = clamp(0.05 * r_in, 0.8, 6)
    for k in range(1, 7):
        c = (0, sy * r_in / (2 * math.sin(15 * k * DEG)))
        rr = abs(c[1])
        for a0, a1 in arc_intervals(c, rr, lambda p: p[0] * sx >= 0 and p[1] * sy >= 0 and math.hypot(*p) <= r_in + 1e-6):
            Dr.arc(c, rr, a0, a1)
        pk = polar(r_in * 0.93, math.atan2(sy * math.sin(15 * k * DEG), sx * math.cos(15 * k * DEG)) / DEG)
        Dr.text(num(k, ns if ns != 'triple' else 'abjad'), (pk[0] - sx * size, pk[1] - sy * size * 0.2), size)
        Dr.text(num(12 - k, ns if ns != 'triple' else 'abjad'), (pk[0] - sx * size * 2.4, pk[1] - sy * size * 0.2), size * 0.8)
    Dr.line((0, 0), (sx * r_in, 0)); Dr.line((0, 0), (0, sy * r_in))


def zodiac_quadrant(Dr, r_in, quad, spec, which):
    """Quadrants with the names of the signs (as on the Wasiti mater):
    radial lines at the signs' altitude of the Sun at noon is not implied –
    the original simply lists signs; we engrave 3 sectors of 30 deg each."""
    sx, sy = quad
    size = clamp(0.06 * r_in, 0.8, 6)
    base = math.atan2(sy, sx) / DEG
    a_start = math.atan2(0, sx) / DEG
    for i in range(4):
        a = a_start + (90 * (1 if (sx * sy) > 0 else -1)) * i / 3
        Dr.line((0, 0), polar(r_in, a))
    for i in range(3):
        a = a_start + (90 * (1 if (sx * sy) > 0 else -1)) * (i + 0.5) / 3
        nm = SIGNS_AR[(which * 3 + i) % 12]
        Dr.text(nm, polar(r_in * 0.62, a), size, a - 90 if sy > 0 else a + 90)
    for rr in (r_in * 0.35, r_in * 0.85):
        for a0, a1 in arc_intervals((0, 0), rr, lambda p: p[0] * sx >= 0 and p[1] * sy >= 0):
            Dr.arc((0, 0), rr, a0, a1)


def dominical_diagram(Dr, r, spec):
    year = spec.get('year', 1400)
    Dr.circle((0, 0), r); Dr.circle((0, 0), r * 0.72); Dr.circle((0, 0), r * 0.45)
    size = clamp(0.09 * r, 0.8, 6)
    for i in range(28):
        y = year + i
        a = 90 - i * 360 / 28
        Dr.line(polar(r * 0.45, a - 360 / 56), polar(r, a - 360 / 56), 'ENGRAVE_FINE')
        def letter(yy, m, d):
            wd = int((julian_day(yy, m, d) + 1.5) % 7)  # 0 = Sunday
            return 'AGFEDCB'[wd]
        L = letter(y, 1, 1)
        leap = (y % 4 == 0)
        if leap:
            L = letter(y, 1, 1) + letter(y, 3, 1)
            # dominical letter after Feb 29
            wd = int((julian_day(y, 3, 1) + 1.5) % 7)
            L = letter(y, 1, 1) + 'AGFEDCB'[(wd - 3) % 7] if False else letter(y, 1, 1) + 'GFEDCBA'[(['AGFEDCB'.index(letter(y, 1, 1))][0]) % 7]
        Dr.text(L, polar(r * 0.86, a), size, a - 90)
        Dr.text(str(y % 100).zfill(2), polar(r * 0.59, a), size * 0.75, a - 90)
    Dr.text(str(year), (0, 0), size)


def make_back(dm, spec, title=''):
    """Back of the mater according to spec['back'] (list of feature names)."""
    Dr = Drawing(title=title)
    shape, holes, pin, geo = mater_outline(dm, spec)
    Dr.shape(shape)
    for x, y, r in holes:
        Dr.circle((x, y), r, 'CUT_INNER')
    if pin:
        Dr.hole(pin, clamp(0.02 * dm.D, 1.5, 6))
    Dr.hole((0, 0), dm.pin_d + 0.1)
    feats = spec.get('back', ['alt', 'shadow'])
    rings = [f for f in feats if f in ('alt', 'alt90', 'zodiac', 'calendar', 'calendar_syriac', 'decans', 'triplicities')]
    r_in = back_rings(Dr, dm, spec, rings)
    Dr.line((-r_in, 0), (r_in, 0)); Dr.line((0, -r_in), (0, r_in))
    Dr.circle((0, 0), r_in)
    eps = dm.eps
    if 'saphea' in feats:
        draw_saphea(Dr, r_in, spec, grid=spec.get('saphea_grid', 5), both=True, stars=spec.get('saphea_stars', 0))
    else:
        if 'shadow' in feats:
            shadow_squares(Dr, r_in, spec, n=spec.get('shadow_n', 12))
        if 'sine' in feats:
            sine_quadrant(Dr, r_in, (-1, 1), spec, eps=eps)
        if 'sine_r' in feats:
            sine_quadrant(Dr, r_in, (1, 1), spec, eps=eps)
        if 'hours' in feats:
            unequal_hours(Dr, r_in, (1, 1), spec)
        if 'hours_l' in feats:
            unequal_hours(Dr, r_in, (-1, 1), spec)
        if 'zodiac_quads' in feats:
            zodiac_quadrant(Dr, r_in, (1, 1), spec, 0)
            zodiac_quadrant(Dr, r_in, (-1, -1), spec, 1)
            zodiac_quadrant(Dr, r_in, (1, -1), spec, 2)
            sine_quadrant(Dr, r_in, (-1, 1), spec, eps=eps)
        if 'dominical' in feats:
            dominical_diagram(Dr, r_in * 0.36, spec)
        if 'moon' in feats:
            Dr.circle((0, r_in * 0.45), r_in * 0.18)
            for k in range(30):
                a = 90 - k * 12
                Dr.line(polar(r_in * 0.18, a, (0, r_in * 0.45)), polar(r_in * 0.15, a, (0, r_in * 0.45)))
    if spec.get('legend_back'):
        size = clamp(0.035 * dm.R, 1, 8)
        Dr.text(spec['legend_back'], (0, r_in * 0.25 if 'shadow' in feats else -r_in * 0.5), size)
    return Dr


# =========================================================================== mater inside, limb ring
def make_limb_ring(dm, spec, title=''):
    Dr = Drawing(title=title)
    shape, holes, pin, geo = mater_outline(dm, spec)
    tabw = clamp(0.035 * dm.D, 2.0, 12.0) + 0.2
    notch = box(-tabw / 2, dm.Rp - 1, tabw / 2, dm.Rp + clamp(0.012 * dm.D, 1.0, 4.0) + 0.1)
    ring = shape.difference(Point(0, 0).buffer(dm.Rp, resolution=256)).difference(notch)
    Dr.shape(ring)
    for x, y, r in holes:
        Dr.circle((x, y), r, 'CUT_INNER')
    if pin:
        Dr.hole(pin, clamp(0.02 * dm.D, 1.5, 6))
    limb_scale(Dr, dm, spec)
    # ornament on the throne: concentric outline
    y0, h, w = geo
    th, _, _, _ = throne_shape(dm, spec)
    inner = th.buffer(-clamp(0.012 * dm.D, 0.8, 4)).difference(Point(0, 0).buffer(dm.R + 0.5))
    if not inner.is_empty and load_traced(spec, 'throne') is None:
        Dr.shape(inner, 'ENGRAVE', 'ENGRAVE')
    if spec.get('legend_throne'):
        Dr.text(spec['legend_throne'], (0, y0 + h * 0.12), clamp(0.025 * dm.D, 1, 7))
    return Dr


def make_mater_inside(dm, spec, title=''):
    Dr = Drawing(title=title)
    shape, holes, pin, geo = mater_outline(dm, spec)
    Dr.shape(shape)
    for x, y, r in holes:
        Dr.circle((x, y), r, 'CUT_INNER')
    if pin:
        Dr.hole(pin, clamp(0.02 * dm.D, 1.5, 6))
    Dr.hole((0, 0), dm.pin_d + 0.1)
    Dr.circle((0, 0), dm.Rp, 'GUIDE')
    mi = spec.get('mater_inside')
    if not mi:
        return Dr
    if 'proj' in mi:
        sub = make_plate(dm, spec, mi['proj'], mater_face=True)
        Dr.merge(sub)
    if 'gazetteer' in mi:
        gazetteer(Dr, dm, spec, mi['gazetteer'], mi.get('lon0', 0), mi.get('lat_only', False))
    return Dr


def gazetteer(Dr, dm, spec, cities, lon_offset, lat_only=False):
    """City table in concentric rings: name / longitude / latitude (abjad)."""
    R = dm.Rp - 0.03 * dm.R
    nrings = 4 if len(cities) > 30 else 3
    per = math.ceil(len(cities) / nrings)
    w = R * 0.62 / nrings
    size = clamp(w * 0.28, 0.8, 7)
    idx = 0
    Dr.circle((0, 0), R)
    for k in range(nrings):
        ro = R - k * w
        ri = ro - w
        Dr.circle((0, 0), ri)
        Dr.circle((0, 0), ri + w * 0.5, 'ENGRAVE_FINE')
        for j in range(per):
            if idx >= len(cities):
                break
            a0 = 90 - j * 360 / per
            Dr.line(polar(ro, a0), polar(ri, a0), 'ENGRAVE_FINE')
            name, lat, lon = cities[idx]
            am = a0 - 180 / per
            Dr.text_arc(name, (0, 0), ri + w * 0.70, am, size * 0.9)
            L = lon + lon_offset
            Dr.text_arc((dms(lat, 'abjad') if lat_only else dms(L % 360, 'abjad') + '  ' + dms(lat, 'abjad')), (0, 0), ri + w * 0.20, am, size * 0.8)
            idx += 1
    Dr.text('عروض البلدان' if lat_only else 'أطوال البلدان وعروضها', (0, 0.12 * R), size * 1.2)


# =========================================================================== alidade / rule / pin / wedge
def make_alidade(dm, spec, length=None, title='', double=True, right_angle_pointer=False):
    L = length or (2 * dm.R - 2)
    D = dm.D
    w = clamp(0.055 * L, 3, 30)
    hub = clamp(0.09 * L, 4, 40)
    Dr = Drawing(title=title)
    hl = L / 2
    # counter-changed (offset) bar: fiducial edge on the centre line
    bar1 = Polygon([(-hl, 0), (-hl + 0.12 * L, w * 0.5), (0, w * 0.5), (0, 0)])
    bar2 = Polygon([(0, 0), (0, -w * 0.5), (hl - 0.12 * L, -w * 0.5), (hl, 0)])
    body1 = Polygon([(-hl + 0.12 * L, 0), (-hl + 0.12 * L, w * 0.5), (0, w * 0.5), (0, 0)])
    shp = unary_union([bar1, bar2, Point(0, 0).buffer(hub / 2), body1])
    if not double:
        shp = unary_union([bar2, Point(0, 0).buffer(hub / 2), Polygon([(-hub, -w * 0.5), (0, -w * 0.5), (0, 0), (-hub, 0)])])
    if right_angle_pointer:
        shp = unary_union([shp, Polygon([(0, 0), (w * 0.4, 0), (0.02, 0.4 * L), (-w * 0.1, 0)])])
    Dr.shape(shp)
    Dr.hole((0, 0), dm.pin_d + 0.1)
    # sight vane slots (tabs are soldered/riveted into these)
    vane_x = 0.30 * L
    vane_w = clamp(0.10 * L, 4, 40)
    for s in ((-1, 1) if double else (1,)):
        x = s * vane_x
        Dr.poly([(x - 0.6, -w * 0.45 * (1 if s > 0 else -0) - (0 if s > 0 else 0)),], False)
        yv = -w * 0.25 if s > 0 else w * 0.25
        Dr.poly([(x - vane_w / 2, yv - 0.5), (x + vane_w / 2, yv - 0.5), (x + vane_w / 2, yv + 0.5), (x - vane_w / 2, yv + 0.5)], True, 'CUT_INNER')
    Dr.line((-hl, 0), (hl, 0), 'GUIDE')
    # vanes as separate flat pieces (bend along BEND line)
    vanes = Drawing(title='sights')
    hv = clamp(0.11 * L, 5, 45)
    for s in (0,):
        x0 = 0
        pts = [(-vane_w / 2, 0), (vane_w / 2, 0), (vane_w / 2, hv), (vane_w * 0.25, hv + vane_w * 0.25), (-vane_w * 0.25, hv + vane_w * 0.25), (-vane_w / 2, hv)]
        vanes.poly(pts + [], True, 'CUT_OUTER')
        vanes.poly([(-vane_w / 2 + 0.4, -w * 0.5), (vane_w / 2 - 0.4, -w * 0.5), (vane_w / 2 - 0.4, 0), (-vane_w / 2 + 0.4, 0)], False, 'CUT_OUTER')
        vanes.line((-vane_w / 2, 0), (vane_w / 2, 0), 'BEND')
        vanes.hole((0, hv * 0.55), clamp(0.012 * L, 0.8, 3))
        vanes.hole((0, hv * 0.25), clamp(0.006 * L, 0.6, 1.5))
    Dr.vanes = vanes
    Dr.L = L
    return Dr


def make_rule(dm, spec, radius, title=''):
    """Front rule (ostensor) with a declination scale computed from the
    projection: mark for declination d at radius r(d)."""
    Dr = Drawing(title=title)
    w = clamp(0.06 * radius, 3, 20)
    hub = clamp(0.16 * radius, 5, 40)
    shp = unary_union([Polygon([(0, 0), (0, -w / 2), (radius - w, -w / 2), (radius, 0), (radius - 2, 0.0)]),
                       Polygon([(0, 0), (0, w / 2 * 0.0), (radius, 0), (0, 0)]),
                       Point(0, 0).buffer(hub / 2), Polygon([(-hub / 2, -w / 2), (0, -w / 2), (0, 0), (-hub / 2, 0)])])
    shp = unary_union([shp, box(0, -w / 2, radius - w, 0)])
    Dr.shape(shp)
    Dr.hole((0, 0), dm.pin_d + 0.1)
    P = dm.proj
    size = clamp(0.35 * w, 0.8, 5)
    for d in range(-int(dm.eps), 61):
        r = P.r(d)
        if r > radius - 1:
            continue
        l = w * (0.55 if d % 10 == 0 else 0.35 if d % 5 == 0 else 0.2)
        Dr.line((r, 0), (r, -l), 'ENGRAVE' if d % 5 == 0 else 'ENGRAVE_FINE')
        if d % 10 == 0:
            Dr.text(str(abs(d)) if numstyle(spec) != 'abjad' else abjad(abs(d)) if d else '٠', (r, -w * 0.78), size * 0.8)
    return Dr


def make_pin_wedge(dm, spec, stack_t):
    """Pin (qutb) and wedge (faras, 'horse') – drawn flat with dimensions."""
    pin = Drawing(title='pin')
    d = dm.pin_d
    L = stack_t + 2.2 * d
    head = 1.8 * d
    # pin as profile view (turned part)
    pin.poly([(-head / 2, 0), (head / 2, 0), (head / 2, 0.35 * d), (d / 2, 0.45 * d), (d / 2, L), (-d / 2, L), (-d / 2, 0.45 * d), (-head / 2, 0.35 * d)], True, 'CUT_OUTER')
    slot_w = max(0.8, 0.28 * d); slot_y = stack_t + 0.45 * d
    pin.poly([(-d / 2, slot_y), (d / 2, slot_y), (d / 2, slot_y + 0.9 * d), (-d / 2, slot_y + 0.9 * d)], True, 'GUIDE')
    pin.line((-head, slot_y + 0.45 * d), (head, slot_y + 0.45 * d), 'GUIDE')
    pin.L, pin.slot_y, pin.slot_w = L, slot_y, slot_w
    # wedge ('horse'): tapered key, with horse-head finial
    wedge = Drawing(title='wedge')
    wl = 3.2 * d + 6
    hgt0, hgt1 = 0.9 * d, 0.55 * d
    pts = [(0, 0), (wl, 0), (wl, hgt1), (0.35 * wl, hgt0)]
    head_pts = [(0.35 * wl, hgt0), (0.25 * wl, hgt0 + 0.5 * d), (0.12 * wl, hgt0 + 0.9 * d), (0.02 * wl, hgt0 + 0.75 * d),
                (0.06 * wl, hgt0 + 0.45 * d), (0.0, hgt0 * 0.6)]
    wedge.poly(pts + head_pts[1:], True, 'CUT_OUTER')
    wedge.circle((0.11 * wl, hgt0 + 0.62 * d), max(0.25, 0.08 * d), 'ENGRAVE')
    wedge.thick = slot_w - 0.1
    return pin, wedge


def make_shackle_ring(dm, spec):
    D = dm.D
    ring = Drawing(title='ring')
    ro = clamp(0.12 * D, 6, 60) / 1.0
    ri = ro * 0.78
    ring.circle((0, 0), ro, 'CUT_OUTER')
    ring.circle((0, 0), ri, 'CUT_INNER')
    sh = Drawing(title='shackle')
    w = clamp(0.06 * D, 3, 25)
    L = clamp(0.20 * D, 8, 80)
    t = clamp(0.012 * D, 1, 4)
    sh.poly([(-w / 2, 0), (w / 2, 0), (w / 2, L), (-w / 2, L)], True, 'CUT_OUTER')
    hd = clamp(0.02 * D, 1.5, 6)
    sh.hole((0, w * 0.6), hd)
    sh.hole((0, L - w * 0.6), hd)
    sh.line((-w / 2, L * 0.38), (w / 2, L * 0.38), 'BEND')
    sh.line((-w / 2, L * 0.62), (w / 2, L * 0.62), 'BEND')
    return sh, ring


# =========================================================================== saphea (universal disc) drawing
def draw_saphea(Dr, R, spec, grid=5, both=True, stars=0, quadrant=None, ecl_lines=True, labels=True):
    """Universal projection on the plane of the solstitial colure.
    Equatorial grid (parallels + hour circles) and, if both, the ecliptic
    grid rotated by the obliquity."""
    E = EquinoxProj(R)
    eps = spec.get('eps', 23 + 35 / 60)
    def ins(p):
        ok = p[0] * p[0] + p[1] * p[1] <= R * R * (1 + 1e-9)
        if quadrant:
            ok = ok and p[0] * quadrant[0] >= -1e-9 and p[1] * quadrant[1] >= -1e-9
        return ok
    def grid_family(rotation, layer_major, layer_minor):
        c, s = math.cos(rotation * DEG), math.sin(rotation * DEG)
        Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        for k in np.arange(-90 + grid, 90, grid):
            lay = layer_major if k % 10 == 0 or grid >= 10 else layer_minor
            pole = Rx @ np.array([0, 0, 1.0])
            draw_projected(Dr, sphere_circle(pole, 90 - k, E), ins, lay)
            ax = Rx @ np.array([math.sin(k * DEG), -math.cos(k * DEG), 0])
            draw_projected(Dr, sphere_circle(ax, 90, E), ins, lay)
        draw_projected(Dr, sphere_circle(Rx @ np.array([0, 0, 1.0]), 90, E), ins, 'ENGRAVE', w=1.3)
    grid_family(0, 'ENGRAVE', 'ENGRAVE_FINE')
    if both:
        grid_family(eps, 'ENGRAVE_FINE', 'ENGRAVE_FINE')
    elif ecl_lines:
        c, s = math.cos(eps * DEG), math.sin(eps * DEG)
        draw_projected(Dr, sphere_circle(np.array([0, -s, c]), 90, E), ins, 'ENGRAVE', w=1.3)
    if quadrant is None:
        Dr.circle((0, 0), R, 'ENGRAVE')
    if stars:
        year = spec.get('year', 1200)
        size = clamp(0.025 * R, 0.8, 5)
        cnt = 0
        for ra, de, ar, la in STARS:
            a, d = precess_star(ra, de, year, eps)
            # stars are placed by RA/Dec on the equatorial grid, both halves
            v = np.array([math.cos(d * DEG) * math.cos(a * DEG), math.cos(d * DEG) * math.sin(a * DEG), math.sin(d * DEG)])
            if v[0] < 0:
                v = np.array([-v[0], -v[1], v[2]])  # fold the far hemisphere (12h rotation)
            p = E.P(v)
            if not ins(p):
                continue
            Dr.circle(p, clamp(0.008 * R, 0.4, 2), 'ENGRAVE')
            Dr.text(la if is_latin(spec) else ar, (p[0], p[1] - size * 1.1), size * 0.8)
            cnt += 1
            if cnt >= stars:
                break


def saphea_rim(Dr, R_out, R_in, spec):
    ns = numstyle(spec)
    size = clamp(0.3 * (R_out - R_in), 0.8, 6)
    degree_ring(Dr, R_out, R_in, 0, 10, lambda v: num(v % 90 if v % 90 else 90, ns) if v % 90 else '', size, direction=1)


def make_saphea_rule(R, spec, length, title=''):
    """Horizon rule of the universal disc: degree divisions at d = R tan(t/2)."""
    Dr = Drawing(title=title)
    w = clamp(0.07 * length, 4, 25)
    hl = length / 2
    Dr.shape(unary_union([box(-hl, -w / 2, hl, w / 2), Point(0, 0).buffer(w * 0.7)]))
    Dr.hole((0, 0), clamp(0.03 * 2 * R, 2.5, 10) + 0.1)
    ns = numstyle(spec)
    size = clamp(0.3 * w, 0.8, 5)
    for t in range(0, 91):
        d = R * math.tan(t / 2 * DEG)
        if d > hl - 0.5:
            continue
        l = w * (0.45 if t % 10 == 0 else 0.3 if t % 5 == 0 else 0.18)
        for s in (-1, 1):
            Dr.line((s * d, w / 2), (s * d, w / 2 - l), 'ENGRAVE' if t % 5 == 0 else 'ENGRAVE_FINE')
            if t % 10 == 0 and t:
                Dr.text(num(t, ns), (s * d, -w * 0.2), size * 0.8)
    Dr.line((-hl, 0.0), (hl, 0.0), 'GUIDE')
    return Dr
