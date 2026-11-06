"""Quadrants, universal discs, spherical & linear astrolabes and the other
observational instruments (pp. 116-150 of the book)."""
import math, csv, io
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union

from core import Drawing, polar, DEG, abjad, num, dms, rot
from geom import (PolarProj, EquinoxProj, sphere_circle, draw_projected, arc_intervals, seg_intervals,
                  horizon_frame, altaz_vec, ecl_to_eq, precess_star, unit, fit_circle)
from astrolabe import (Dims, clamp, numstyle, is_latin, sine_quadrant, asr_curve, unequal_hours, shadow_squares,
                       draw_saphea, saphea_rim, make_saphea_rule, make_plate, plate_lines, degree_ring,
                       SIGNS_AR, SIGNS_LA, select_stars, STARS, mater_outline, make_shackle_ring, make_alidade)


def ns_(spec):
    n = numstyle(spec)
    return 'abjad' if n == 'triple' else n


# =========================================================================== quadrant basics
def quadrant_outline(R, extra=None):
    pts = [(0, 0), (R, 0)] + [polar(R, a) for a in np.linspace(0, 90, 181)] + [(0, R)]
    shp = Polygon(pts)
    if extra is not None:
        shp = unary_union([shp, extra])
    return shp


def quadrant_limb(Dr, R, w, spec, from_x=True):
    """0..90 degree scale along the arc."""
    ns = ns_(spec)
    size = clamp(0.32 * w, 0.8, 6)
    Dr.arc((0, 0), R - w, 0, 90); Dr.arc((0, 0), R - 0.4 * w, 0, 90)
    for v in range(0, 91):
        a = v if from_x else 90 - v
        l = w * (0.4 if v % 10 == 0 else 0.3 if v % 5 == 0 else 0.15)
        Dr.line(polar(R - 0.02 * w, a), polar(R - 0.02 * w - l, a), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
        if v % 10 == 0 and 0 < v < 90:
            Dr.text_arc(num(v, ns), (0, 0), R - 0.72 * w, a, size)
    Dr.line((0, 0), (R, 0)); Dr.line((0, 0), (0, R))


def sights_pieces(L, hv=None):
    """Two pinnules for an edge of length L (flat development)."""
    Dv = Drawing(title='sights')
    w = clamp(0.10 * L, 5, 30)
    hv = hv or clamp(0.12 * L, 6, 40)
    for k, x0 in enumerate((0, w * 1.6)):
        Dv.poly([(x0 - w / 2, -w * 0.4), (x0 + w / 2, -w * 0.4), (x0 + w / 2, hv), (x0 - w / 2, hv)], True, 'CUT_OUTER')
        Dv.line((x0 - w / 2, 0), (x0 + w / 2, 0), 'BEND')
        Dv.hole((x0, hv * 0.6), clamp(0.012 * L, 0.8, 2.5) * (1 if k == 0 else 0.6))
    return Dv


def plumb_bob(size):
    Dp = Drawing(title='plumb')
    r = size / 2
    pts = [(0, -1.8 * size)] + [polar(r, a) for a in np.linspace(-30, 210, 40)]
    Dp.poly(pts, True, 'CUT_OUTER')
    Dp.hole((0, r * 0.4), max(0.6, size * 0.12))
    return Dp


def fold_to_quadrant(src):
    """Fold all arcs/circles/lines of a full plate drawing into the first
    quadrant (|x|,|y|), as done on the astrolabic (almucantar) quadrant."""
    out = Drawing()
    for it in src.items:
        if it['layer'] not in ('ENGRAVE', 'ENGRAVE_FINE'):
            continue
        if it['t'] in ('circle', 'arc'):
            c, r = it['c'], it['r']
            a_from, a_to = (0, 360) if it['t'] == 'circle' else (it['a0'], it['a1'])
            for sx in (1, -1):
                for sy in (1, -1):
                    for a0, a1 in arc_intervals(c, r, lambda p: p[0] * sx >= -1e-9 and p[1] * sy >= -1e-9, n=360, a_from=a_from, a_to=a_to):
                        cc = (c[0] * sx, c[1] * sy)
                        if sx * sy > 0:
                            b0, b1 = (a0, a1) if sx > 0 else (a0 + 180, a1 + 180)
                        else:
                            b0, b1 = (-a1, -a0) if sy < 0 else (180 - a1, 180 - a0)
                        out.arc(cc, r, b0, b1, it['layer'])
        elif it['t'] == 'poly' and not it.get('fill') and len(it['p']) == 2:
            p0, p1 = it['p']
            for sx in (1, -1):
                for sy in (1, -1):
                    for a, b in seg_intervals(p0, p1, lambda p: p[0] * sx >= -1e-9 and p[1] * sy >= -1e-9, n=200):
                        out.line((a[0] * sx, a[1] * sy), (b[0] * sx, b[1] * sy), it['layer'])
    return out


# =========================================================================== quadrant instruments
def build_sine_quadrant(spec):
    R = spec['R']
    parts, views = [], []
    w = clamp(0.08 * R, 5, 18)
    phi = spec.get('lat', 33.5)
    eps = spec.get('eps', 23.5)
    front = Drawing(title='front')
    lug = None
    shp = quadrant_outline(R)
    front.shape(shp)
    front.hole((0, 0), clamp(0.01 * R, 1.0, 2.0))
    quadrant_limb(front, R, w, spec)
    face = spec.get('front', 'sine')
    back = Drawing(title='back')
    back.shape(shp)
    back.hole((0, 0), clamp(0.01 * R, 1.0, 2.0))
    def fill(D, kind):
        if kind == 'sine':
            sine_quadrant(D, R - w, (1, 1), spec, n=60, eps=eps)
            asr_curve(D, R - w, (1, 1))
        elif kind == 'astrolabic':
            astrolabic_into(D, R - w, phi, spec)
        elif kind == 'horary':
            european_hours(D, R - w, phi, spec)
    fill(front, face)
    if spec.get('back'):
        quadrant_limb(back, R, w, spec)
        fill(back, spec['back'])
    size = clamp(0.03 * R, 1, 6)
    if spec.get('legend'):
        front.text(spec['legend'], polar(R * 0.55, 45), size, -45)
    parts.append(('front_back', 'جسم الربع - الوجه', front, 'brass', clamp(R / 75, 1.5, 4), 1))
    if spec.get('back'):
        parts.append(('back_face', 'جسم الربع - الظهر (نفس القطعة)', back, 'brass', None, 0))
    parts.append(('sights', 'الهدفتان (الشظيتان) - تثنى على خط الثني', sights_pieces(R), 'brass', clamp(R / 120, 0.8, 2), 1))
    parts.append(('plumb', 'الشاقول (ثقل الخيط) ومريّ الخيط', plumb_bob(clamp(0.06 * R, 5, 14)), 'brass', clamp(0.06 * R, 5, 14), 1))
    views.append(('front', front))
    if spec.get('back'):
        views.append(('back', back))
    return parts, views


def astrolabic_into(D, R_in, phi, spec):
    eps = spec.get('eps', 23.5)
    dm = Dims({'D': 2 * R_in / 0.85, 'eps': eps})
    dm.R_cap = R_in
    dm.proj = PolarProj(R_in, eps)
    tmp = Drawing()
    tmp.circle((0, 0), dm.R_cap); tmp.circle((0, 0), dm.proj.R_eq); tmp.circle((0, 0), dm.proj.R_can)
    sp = dict(spec); sp['D'] = 2 * R_in / 0.85 * 1.0
    sp['twilight'] = False
    plate_lines(tmp, dm, phi, sp, labels=False, hours=False)
    # ecliptic circle
    yc = (dm.proj.R_cap - dm.proj.R_can) / 2
    tmp.circle((0, yc), (dm.proj.R_cap + dm.proj.R_can) / 2)
    D.merge(fold_to_quadrant(tmp))
    ns = ns_(spec)
    size = clamp(0.035 * R_in, 0.8, 5)
    Z, S, W = horizon_frame(phi)
    for h in range(0, 90, 6 if R_in < 150 else 3):
        if h % 12:
            continue
        y = dm.proj.P(altaz_vec(phi, h, 0))[1]
        if 0 < y < R_in * 0.97:
            D.text(num(h, ns), (size * 0.9, y + size * 0.5), size * 0.8)
    D.text(('لعرض ' + dms(phi, 'abjad')) if not is_latin(spec) else ('LAT. ' + dms(phi)), polar(R_in * 0.5, 30), size, -60)


def european_hours(D, R_in, phi, spec):
    """Horary quadrant: radial distance encodes the solar declination
    (calendar arcs), the angle the altitude.  Hour curves = altitude of the
    Sun at each hour (equal hours from noon) for every declination."""
    eps = spec.get('eps', 23.5)
    r1, r2 = R_in * 0.35, R_in * 0.95
    def rr(d):
        return r1 + (d + eps) / (2 * eps) * (r2 - r1)
    for d in (-eps, -20.15, -11.47, 0, 11.47, 20.15, eps):
        D.arc((0, 0), rr(d), 0, 90, 'ENGRAVE' if d in (-eps, 0, eps) else 'ENGRAVE_FINE')
    for H in range(0, 7):
        pts = []
        for d in np.linspace(-eps, eps, 60):
            s = math.sin(phi * DEG) * math.sin(d * DEG) + math.cos(phi * DEG) * math.cos(d * DEG) * math.cos(15 * H * DEG)
            if s <= 0:
                continue
            h = math.asin(s) / DEG
            pts.append(polar(rr(d), h))
        if len(pts) > 1:
            D.poly(pts, False, 'ENGRAVE')
            D.text(str(12 - H) + ('/' + str(H) if H else ''), (pts[-1][0] + 2, pts[-1][1] + 2), clamp(0.03 * R_in, 1, 4))
    names = SIGNS_LA
    for i, d in enumerate((-eps, -20.15, -11.47, 0, 11.47, 20.15, eps)):
        D.text(['♑', '♒♐', '♓♏', '♈♎', '♉♍', '♊♌', '♋'][i] if False else ['CAP', 'AQ/SAG', 'PIS/SCO', 'AR/LIB', 'TAV/VIR', 'GEM/LEO', 'CANC'][i],
               polar(rr(d), 3), clamp(0.022 * R_in, 0.8, 3), 0)
    shadow_square_quadrant(D, R_in * 0.30, spec)


def shadow_square_quadrant(D, s, spec):
    D.poly([(0, 0), (s, 0), (s, s), (0, s)], True, 'ENGRAVE')
    for k in range(1, 12):
        t = s * k / 12
        D.line((s, t), (s * 0.9, t), 'ENGRAVE'); D.line((t, s), (t, s * 0.9), 'ENGRAVE')
    D.line((0, 0), (s, s), 'ENGRAVE_FINE')


def build_shakkaziya(spec):
    """Shakkaziya double quadrant: massive plate + net plate + spider, all
    quarters of the universal (Zarqali) projection, pivoting at the apex."""
    R = spec['R']
    w = clamp(0.07 * R, 5, 16)
    parts, views = [], []
    base = Drawing(title='base')
    shp = quadrant_outline(R)
    base.shape(shp)
    base.hole((0, 0), clamp(0.02 * R, 2, 5))
    quadrant_limb(base, R, w, spec)
    draw_saphea(base, R - w, spec, grid=5 if R > 120 else 10, both=False, quadrant=(1, 1))
    if spec.get('both_grids'):
        draw_saphea(base, R - w, spec, grid=5 if R > 120 else 10, both=True, quadrant=(1, 1))
    parts.append(('base', 'الصفيحة المصمتة (القاعدة) - مسقط الزرقالي', base, 'brass', clamp(R / 60, 2, 4), 1))
    # net plate (openwork 10 deg grid)
    net = Drawing(title='net')
    Rn = R - w - 0.5
    E = EquinoxProj(Rn)
    bars = []
    wb = clamp(0.012 * R, 0.8, 2.2)
    for k in range(-80, 90, 10):
        for axis, rho in ((np.array([0, 0, 1.0]), 90 - k), (np.array([math.sin(k * DEG), -math.cos(k * DEG), 0]), 90)):
            sc = sphere_circle(axis, rho, E)
            if sc[0] == 'circle':
                pts = [polar(sc[2], a, sc[1]) for a in np.linspace(0, 360, 721)]
            else:
                p, d = sc[1], sc[2]
                pts = [(p[0] - d[0] * 3 * R, p[1] - d[1] * 3 * R), (p[0] + d[0] * 3 * R, p[1] + d[1] * 3 * R)]
            bars.append(LineString(pts).buffer(wb / 2))
    q = quadrant_outline(Rn)
    rim = q.difference(quadrant_outline(Rn - 2.5 * wb).buffer(-1.5 * wb))
    netshape = unary_union([unary_union(bars).intersection(q), rim, Point(0, 0).buffer(4 * wb)])
    net.shape(netshape)
    net.hole((0, 0), clamp(0.02 * R, 2, 5))
    parts.append(('net', 'الصفيحة الشبكية (مفرغة) - شبكة كل ١٠°', net, 'brass', clamp(R / 120, 1, 2), 1))
    # spider: quarter ring, ecliptic radius, 7 star pointers
    sp = Drawing(title='spider')
    Rs = Rn
    ring = quadrant_outline(Rs).difference(Point(0, 0).buffer(Rs - 3 * wb))
    eps = spec.get('eps', 23.5)
    ecl = LineString([(0, 0), polar(Rs, 90 - eps)]).buffer(1.6 * wb)
    eq = LineString([(0, 0), (0, Rs)]).buffer(1.2 * wb)
    geoms = [ring, ecl, eq, Point(0, 0).buffer(5 * wb)]
    E2 = EquinoxProj(Rs)
    year = spec.get('year', 1400)
    names = []
    cnt = 0
    for ra, de, ar, la in STARS:
        a, d = precess_star(ra, de, year, eps)
        v = np.array([math.cos(d * DEG) * math.cos(a * DEG), math.cos(d * DEG) * math.sin(a * DEG), math.sin(d * DEG)])
        v = np.array([abs(v[0]), abs(v[1]), abs(v[2])])
        p = E2.P(v)
        if p[0] < 2 or p[1] < 2 or math.hypot(*p) > Rs - 4 * wb:
            continue
        anchor = polar(Rs - 1.5 * wb, math.atan2(p[1], p[0]) / DEG)
        geoms.append(LineString([anchor, p]).buffer(wb * 0.9))
        geoms.append(Polygon([p, (p[0] + 2.5 * wb, p[1] + 1.2 * wb), (p[0] + 2.5 * wb, p[1] - 1.2 * wb)]).buffer(0))
        names.append((la if is_latin(spec) else ar, p))
        cnt += 1
        if cnt >= spec.get('stars', 7):
            break
    spider = unary_union(geoms).intersection(quadrant_outline(Rs))
    sp.shape(spider)
    sp.hole((0, 0), clamp(0.02 * R, 2, 5))
    for nm, p in names:
        sp.circle(p, 0.4, 'ENGRAVE')
    parts.append(('spider', 'العنكبوت الربعي (٧ مؤشرات كواكب)', sp, 'brass', clamp(R / 120, 1, 2), 1))
    parts.append(('sights', 'الهدفتان', sights_pieces(R), 'brass', 1.0, 1))
    parts.append(('plumb', 'الشاقول', plumb_bob(clamp(0.06 * R, 5, 14)), 'brass', 6, 1))
    asm = Drawing(title='assembly')
    asm.merge(base); asm.merge(net); asm.merge(sp)
    views.append(('front', asm))
    sp.star_table = [(n, 0, 0) for n, _ in names]
    return parts, views


def build_meteoroscope(spec):
    R = spec['R']
    w = clamp(0.07 * R, 5, 16)
    parts, views = [], []
    f = Drawing(title='front')
    shp = quadrant_outline(R)
    f.shape(shp); f.hole((0, 0), 2.5)
    quadrant_limb(f, R, w, spec)
    draw_saphea(f, R - w, spec, grid=5, both=True, quadrant=(1, 1))
    b = Drawing(title='back')
    b.shape(shp); b.hole((0, 0), 2.5)
    quadrant_limb(b, R, w, spec)
    sine_quadrant(b, R - w, (1, 1), spec, n=60)
    rule = Drawing(title='rule')
    L = R - 2
    rw = clamp(0.06 * R, 4, 12)
    rule.shape(unary_union([box(0, -rw / 2, L, rw / 2), Point(0, 0).buffer(rw * 0.8)]))
    rule.hole((0, 0), 2.5)
    for k in range(0, 61):
        x = (R - w) * k / 60
        l = rw * (0.5 if k % 10 == 0 else 0.3 if k % 5 == 0 else 0.18)
        rule.line((x, rw / 2), (x, rw / 2 - l), 'ENGRAVE' if k % 5 == 0 else 'ENGRAVE_FINE')
        if k % 10 == 0 and k:
            rule.text(str(k), (x, -rw * 0.2), rw * 0.3)
    parts += [('front', 'جسم الربع - الوجه (مسقط عام بشبكتين)', f, 'brass', 3, 1),
              ('back', 'جسم الربع - الظهر (ربع جيب)', b, 'brass', None, 0),
              ('rule', 'المسطرة المتحركة على الظهر (مقسومة ٦٠)', rule, 'brass', 1.5, 1),
              ('sights', 'الهدفتان', sights_pieces(R), 'brass', 1.0, 1),
              ('plumb', 'الشاقول', plumb_bob(10), 'brass', 6, 1)]
    views += [('front', f), ('back', b)]
    return parts, views


# =========================================================================== universal disc (saphea)
def build_saphea(spec):
    D = spec['D']
    R = D / 2
    dm = Dims(spec)
    w = clamp(0.07 * R, 4, 14)
    parts, views = [], []
    front = Drawing(title='front')
    shape, holes, pin, geo = mater_outline(dm, spec)
    front.shape(shape)
    for x, y, r in holes:
        front.circle((x, y), r, 'CUT_INNER')
    front.hole(pin, clamp(0.02 * D, 1.5, 6))
    front.hole((0, 0), dm.pin_d + 0.1)
    saphea_rim(front, R, R - w, spec)
    draw_saphea(front, R - w, spec, grid=spec.get('grid', 5), both=spec.get('both', True), stars=spec.get('stars', 0))
    from astrolabe import make_back
    bspec = dict(spec)
    bspec['back'] = spec.get('back', ['alt', 'zodiac', 'calendar', 'shadow', 'moon'])
    back = make_back(dm, bspec)
    rule = make_saphea_rule(R - w, spec, spec.get('rule_len', 2 * (R - w)))
    alid = make_alidade(dm, spec, spec.get('alidade', D))
    parts += [('disc_front', 'القرص (الصفيحة الزرقالية) - الوجه', front, 'brass', spec.get('t', 3), 1),
              ('disc_back', 'القرص - الظهر (نفس القطعة)', back, 'brass', None, 0),
              ('rule', 'مسطرة الأفق المقسومة بالدرج (طول %d مم)' % spec.get('rule_len', 2 * (R - w)), rule, 'brass', clamp(D / 110, 1.2, 3), 1),
              ('alidade', 'العضادة بالهدفتين (طول %d مم)' % alid.L, alid, 'brass', clamp(D / 80, 1.5, 4), 1),
              ('sights', 'هدفتا العضادة', alid.vanes, 'brass', 1, 2)]
    sh, ring = make_shackle_ring(dm, spec)
    parts += [('shackle', 'العروة (الحمّالة)', sh, 'brass', clamp(0.012 * D, 1, 4), 1), ('ring', 'الحلقة', ring, 'brass', clamp(0.025 * D, 1.5, 6), 1)]
    views += [('front', front), ('back', back)]
    return parts, views


# =========================================================================== dastur & quadrant disc
def build_dastur(spec):
    D = spec['D']; R = D / 2
    dm = Dims(spec)
    phi = spec.get('lat', 31.5)
    parts, views = [], []
    front = Drawing(title='front')
    shape, holes, pin, geo = mater_outline(dm, spec)
    front.shape(shape)
    for x, y, r in holes:
        front.circle((x, y), r, 'CUT_INNER')
    front.hole(pin, 2); front.hole((0, 0), dm.pin_d + 0.1)
    from astrolabe import limb_scale
    limb_scale(front, dm, spec)
    P = dm.proj
    Z, S, W = horizon_frame(phi)
    inside = lambda p: math.hypot(*p) <= dm.R_cap
    for c in (dm.R_cap, P.R_eq, P.R_can):
        front.circle((0, 0), c)
    draw_projected(front, sphere_circle(Z, 90, P), inside, 'ENGRAVE', w=1.4)           # horizon
    draw_projected(front, sphere_circle(np.cross(Z, S), 90, P), inside, 'ENGRAVE')     # prime vertical
    front.line((0, -dm.R_cap), (0, dm.R_cap)); front.line((-dm.R_cap, 0), (dm.R_cap, 0))
    yc = (P.R_cap - P.R_can) / 2
    for a0, a1 in arc_intervals((0, yc), (P.R_cap + P.R_can) / 2, inside):
        front.arc((0, yc), (P.R_cap + P.R_can) / 2, a0, a1)
    stars = select_stars(spec, dm, spec.get('stars', 12))
    size = clamp(0.022 * D, 1, 5)
    for ra, de, ar, la in stars:
        r = P.r(de); th = ra - 180
        p = polar(r, th)
        front.circle(p, 0.8)
        # chord: line joining the star's rising and setting points on its day circle
        if abs(math.tan(phi * DEG) * math.tan(de * DEG)) < 1:
            H0 = math.acos(-math.tan(phi * DEG) * math.tan(de * DEG)) / DEG
            pa, pb = P.P_Hd(H0, de), P.P_Hd(-H0, de)
            front.line(pa, pb, 'ENGRAVE_FINE')
        front.text(ar, (p[0], p[1] - size), size * 0.8)
    back = Drawing(title='back')
    back.shape(shape)
    for x, y, r in holes:
        back.circle((x, y), r, 'CUT_INNER')
    back.hole(pin, 2); back.hole((0, 0), dm.pin_d + 0.1)
    Rin = R - dm.limb_w
    degree_ring(back, R - 0.5, Rin, 0, 10, lambda v: num(v % 90 if v % 90 else 90, 'abjad') if v % 90 else '', clamp(0.25 * dm.limb_w, 1, 5), direction=1)
    # full sine lattice over the whole disc
    n = 60
    for k in range(-n + 1, n):
        t = Rin * k / n
        L = math.sqrt(Rin * Rin - t * t)
        lay = 'ENGRAVE' if k % 5 == 0 else 'ENGRAVE_FINE'
        back.line((t, -L), (t, L), lay); back.line((-L, t), (L, t), lay)
    alid = make_alidade(dm, spec, D - 2)
    parts += [('front', 'القرص - الوجه (الدوائر الأساسية لعرض %s ومواضع الكواكب وأوتارها)' % dms(phi), front, 'brass', 3, 1),
              ('back', 'القرص - الظهر (شبكة جيوب كاملة)', back, 'brass', None, 0),
              ('alidade', 'عضادتان (مضافتان في النموذج)', alid, 'brass', 2, 2), ('sights', 'الهدفات', alid.vanes, 'brass', 1, 4)]
    sh, ring = make_shackle_ring(dm, spec)
    parts += [('shackle', 'العروة', sh, 'brass', 2, 1), ('ring', 'الحلقة', ring, 'brass', 3, 1)]
    views += [('front', front), ('back', back)]
    return parts, views


def build_quadrant_disc(spec):
    D = spec['D']; R = D / 2
    dm = Dims(spec)
    parts, views = [], []
    shape, holes, pin, geo = mater_outline(dm, spec)
    front = Drawing(title='front')
    front.shape(shape); front.hole(pin, 3); front.hole((0, 0), 3)
    for x, y, r in holes:
        front.circle((x, y), r, 'CUT_INNER')
    # sexagesimal quadrant in the lower right quarter
    Rq = R * 0.92
    q = Drawing()
    sine_quadrant(q, Rq, (1, -1), spec, n=60)
    front.merge(q)
    front.arc((0, 0), Rq, 270, 360)
    back = Drawing(title='back')
    back.shape(shape); back.hole(pin, 3); back.hole((0, 0), 3)
    for x, y, r in holes:
        back.circle((x, y), r, 'CUT_INNER')
    w = clamp(0.06 * R, 4, 14)
    for start, sgn in ((0, 1), (180, -1)):
        for v in range(0, 91):
            a = start + sgn * v
            l = w * (0.6 if v % 10 == 0 else 0.4 if v % 5 == 0 else 0.25)
            back.line(polar(R - 1, a), polar(R - 1 - l, a), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
            if v % 10 == 0 and 0 < v < 90:
                back.text_arc(abjad(v), (0, 0), R - 1 - 0.85 * w, a, w * 0.3)
    back.arc((0, 0), R - 1 - w, 0, 180); back.line((-R + 1, 0), (R - 1, 0))
    alid = make_alidade(dm, spec, D - 4)
    parts += [('front', 'القرص - وجه الربع الستيني (مبسوط ومنكوس ونصفا دائرة)', front, 'brass', 0.8, 1),
              ('back', 'القرص - الظهر (ربعان مقسومان ٩٠°)', back, 'brass', None, 0),
              ('alidade', 'العضادة', alid, 'brass', 1.5, 1), ('sights', 'الهدفتان', alid.vanes, 'brass', 0.8, 2)]
    sh, ring = make_shackle_ring(dm, spec)
    parts += [('shackle', 'العروة', sh, 'brass', 1.5, 1), ('ring', 'الحلقة', ring, 'brass', 3, 1)]
    views += [('front', front), ('back', back)]
    return parts, views


# =========================================================================== Indian circle
def build_indian_circle(spec):
    D = spec['D']; R = D / 2
    g = spec['gnomon']
    parts, views = [], []
    disc = Drawing(title='disc')
    disc.circle((0, 0), R, 'CUT_OUTER')
    disc.hole((0, 0), 4.2)
    degree_ring(disc, R - 1, R - 12, 90, 10, lambda v: abjad(v) if v else '', 3.2, direction=-1)
    for k in range(1, 8):
        disc.circle((0, 0), (R - 14) * k / 8, 'ENGRAVE' if k % 2 == 0 else 'ENGRAVE_FINE')
    disc.line((0, -R + 12), (0, R - 12)); disc.line((-R + 12, 0), (R - 12, 0))
    for nm, a in (('جنوب', 90), ('شمال', 270), ('شرق', 180), ('غرب', 0)):
        disc.text(nm, polar(R * 0.5, a + 6), 5)
    gn = Drawing(title='gnomon')
    # profile of a turned conical gnomon with a threaded spigot
    gn.poly([(-8, 0), (8, 0), (6, 4), (1.2, g - 2), (0, g), (-1.2, g - 2), (-6, 4)], True, 'CUT_OUTER')
    gn.poly([(-2, 0), (2, 0), (2, -6), (-2, -6)], True, 'CUT_OUTER')
    gn.line((-2.5, -3), (2.5, -3), 'GUIDE')
    parts += [('disc', 'القرص المستوي - الدائرة الهندية (قطر %d مم)' % D, disc, 'brass', 3, 1),
              ('gnomon', 'الشاخص (المقياس) ارتفاع %d مم - قطعة مخروطة بسن M4' % g, gn, 'brass (turned)', None, 1)]
    views.append(('front', disc))
    return parts, views


# =========================================================================== meridian instrument (Ibn al-Haytham)
def build_meridian_instrument(spec):
    H = spec['H']
    parts, views = [], []
    Rb = 180
    base = Drawing(title='lower semicircle')
    shp = unary_union([Point(0, 0).buffer(Rb).intersection(box(-Rb, -Rb, Rb, 0)), box(-Rb, -12, Rb, 0), Point(0, 0).buffer(30)])
    base.shape(shp)
    base.hole((0, 0), 20.2)
    for v in range(0, 181):
        a = 180 + v
        l = 10 if v % 10 == 0 else 6 if v % 5 == 0 else 3.5
        base.line(polar(Rb - 1, a), polar(Rb - 1 - l, a), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
        if v % 10 == 0 and 0 < v < 180:
            base.text_arc(abjad(v if v <= 90 else 180 - v), (0, 0), Rb - 18, a, 4)
    base.arc((0, 0), Rb - 12, 180, 360); base.arc((0, 0), Rb - 22, 180, 360)
    base.text('خط نصف النهار', (0, -Rb * 0.5), 5)
    base.line((0, 0), (0, -Rb + 12), 'ENGRAVE')
    ptr = Drawing(title='pointer')
    ptr.shape(unary_union([Polygon([(0, -4), (Rb - 4, 0), (0, 4)]), Point(0, 0).buffer(14)]))
    ptr.hole((0, 0), 20.2)
    top = Drawing(title='top plate')
    top.shape(unary_union([box(-110, -90, 110, 90)]))
    top.hole((0, 0), 20.2)
    top.circle((0, 0), 80, 'ENGRAVE')
    for v in range(0, 360, 5):
        top.line(polar(80, v), polar(80 - (6 if v % 10 == 0 else 3), v), 'ENGRAVE')
    alid = Drawing(title='alidade')
    alid.shape(unary_union([box(-130, -9, 130, 9), Point(0, 0).buffer(16)]))
    alid.hole((0, 0), 6.2)
    tube = Drawing(title='sighting tube (development)')
    Lt, dt = 180, 14
    tube.poly([(0, 0), (Lt, 0), (Lt, math.pi * dt), (0, math.pi * dt)], True, 'CUT_OUTER')
    parts += [('lower_semicircle', 'نصف الدائرة الأفقي السفلي المدرج (نصف قطر %d مم - تقدير من الصورة)' % Rb, base, 'brass', 4, 1),
              ('pointer', 'المؤشر السفلي المثبت في العمود', ptr, 'brass', 3, 1),
              ('top_plate', 'اللوح العلوي', top, 'brass', 4, 1),
              ('alidade', 'العضادة العلوية', alid, 'brass', 3, 1),
              ('tube', 'أنبوب الرصد (فرد)', tube, 'brass sheet', 0.6, 1),
              ('sights', 'الهدفتان', sights_pieces(260), 'brass', 1.5, 1)]
    col = Drawing(title='column')
    col.poly([(-20, 0), (20, 0), (20, H - 60), (-20, H - 60)], True, 'CUT_OUTER')
    col.line((0, 0), (0, H - 60), 'GUIDE')
    parts.append(('column', 'العمود الدوار (خشب صلد مقطع ٤٠×٤٠ مم) بطول %d مم' % (H - 60), col, 'hard wood', 40, 1))
    views.append(('base', base))
    return parts, views


# =========================================================================== triangle instrument (al-Khazini)
def build_triangle(spec):
    a = spec.get('leg', 200.0)
    c = a * math.sqrt(2)
    hgt = c / 2
    r = a / 2
    parts, views = [], []
    tri = Drawing(title='triangle')
    # hypotenuse horizontal on top, right-angle apex downwards
    A, B, C = (-c / 2, 0), (c / 2, 0), (0, -hgt)
    tri.poly([A, B, C], True, 'CUT_OUTER')
    tri.hole(C, 3.2)
    tri.hole((0, 0), 1.2)
    tri.arc((0, 0), r, 180, 360)
    tri.arc((0, 0), r - 8, 180, 360)
    for v in range(0, 181):
        ang = 180 + v
        l = 8 if v % 10 == 0 else 5 if v % 5 == 0 else 3
        tri.line(polar(r, ang), polar(r - l, ang), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
        if v % 10 == 0 and 0 < v < 180:
            tri.text_arc(abjad(v if v <= 90 else 180 - v), (0, 0), r - 12, ang, 3.5)
    tri.line((0, 0), (0, -r), 'ENGRAVE')
    slab = Drawing(title='base slab')
    Ls = c * 1.4
    slab.poly([(-Ls / 2, 0), (Ls / 2, 0), (Ls / 2, 30), (-Ls / 2, 30)], True, 'CUT_OUTER')
    for k in range(-60, 61):
        x = hgt * k / 60
        if abs(x) > Ls / 2 - 2:
            continue
        l = 12 if k % 10 == 0 else 8 if k % 5 == 0 else 4
        slab.line((x, 30), (x, 30 - l), 'ENGRAVE' if k % 5 == 0 else 'ENGRAVE_FINE')
        if k % 10 == 0 and k:
            slab.text(abjad(abs(k)), (x, 10), 4)
    slab.text('كل قسم = ١/٦٠ من ارتفاع المثلث (%.1f مم)' % (hgt / 60), (0, 3), 2.5)
    parts += [('triangle', 'المثلث القائم المتساوي الساقين (ساق %d مم) ونصف الدائرة المقسوم ١٨٠' % a, tri, 'brass', 3, 1),
              ('base', 'اللوح القاعدي المدرج (٦٠ جزءاً من ارتفاع المثلث)', slab, 'hard wood + brass strip', 20, 1),
              ('sights', 'الهدفتان على طرفي الوتر', sights_pieces(c), 'brass', 1.5, 1),
              ('plumb', 'الشاقول من مركز نصف الدائرة', plumb_bob(12), 'brass', 12, 1)]
    views.append(('front', tri))
    return parts, views


# =========================================================================== three altitude instruments (al-Samaw'al)
def build_altitude_table(spec):
    kind = spec['variant']
    Lt = spec['table']
    parts, views = [], []
    scale = Drawing(title='scale')
    if kind == 1:
        L = (Lt - 40) / 2.0          # two equal arms; distance of tips = 2L cos h
        sl = 2 * L
        f = lambda h: 2 * L * math.cos(h * DEG)
        txt = 'المسافة بين طرفي الذراعين = ٢ل جتا ع'
    elif kind == 2:
        L = Lt - 80                  # arm length; height on the vertical ruler = L sin h
        sl = L
        f = lambda h: L * math.sin(h * DEG)
        txt = 'الارتفاع على المسطرة القائمة = ل جا ع'
    else:
        L = Lt - 60                  # hinged arm with plumb: horizontal distance = L cos h
        sl = L
        f = lambda h: L * math.cos(h * DEG)
        txt = 'بعد موقع الشاقول على المسطرة = ل جتا ع'
    W = 22
    scale.poly([(-5, 0), (sl + 5, 0), (sl + 5, W), (-5, W)], True, 'CUT_OUTER')
    for k in range(0, 91):
        x = f(k)
        if x < -0.01 or x > sl + 0.01:
            continue
        l = 10 if k % 10 == 0 else 7 if k % 5 == 0 else 4
        scale.line((x, W), (x, W - l), 'ENGRAVE' if k % 5 == 0 else 'ENGRAVE_FINE')
        if k % 5 == 0:
            scale.text(abjad(k) if k else '٠', (x, 6), 3.2)
    scale.text(txt, (sl / 2, -4), 3)
    parts.append(('scale', 'المسطرة النحاسية المدرجة (حروف الجمل لكل ٥°) - طول %d مم' % sl, scale, 'brass', 1.5, 1))
    arm = Drawing(title='arm')
    aw = 18
    arm.poly([(0, -aw / 2), (L, -aw / 2), (L + 12, 0), (L, aw / 2), (0, aw / 2)], True, 'CUT_OUTER')
    arm.hole((8, 0), 4.2)
    arm.line((0, 0), (L + 12, 0), 'GUIDE')
    parts.append(('arm', 'الذراع (طول %d مم بين المحور والطرف)' % L, arm, 'brass', 3, 2 if kind != 2 else 1))
    parts.append(('sights', 'الهدفتان', sights_pieces(L), 'brass', 1.2, 1))
    table = Drawing(title='table')
    table.poly([(0, 0), (Lt, 0), (Lt, 60), (0, 60)], True, 'CUT_OUTER')
    table.line((20, 40), (Lt - 20, 40), 'GUIDE')
    parts.append(('table', 'الطاولة الخشبية %d مم' % Lt, table, 'hard wood', 60, 1))
    if kind == 2:
        vr = Drawing(title='vertical ruler')
        vr.poly([(0, 0), (24, 0), (24, L + 20), (0, L + 20)], True, 'CUT_OUTER')
        for k in range(0, 91, 1):
            y = L * math.sin(k * DEG)
            vr.line((24, y), (24 - (8 if k % 5 == 0 else 4), y), 'ENGRAVE' if k % 5 == 0 else 'ENGRAVE_FINE')
            if k % 10 == 0 and k:
                vr.text(abjad(k), (8, y), 3)
        parts.append(('vertical_ruler', 'المسطرة القائمة المتحركة على المجرى', vr, 'brass', 3, 1))
    if kind == 3:
        parts.append(('plumb', 'الشاقول', plumb_bob(14), 'brass', 14, 1))
    views.append(('scale', scale))
    return parts, views


# =========================================================================== spherical astrolabes
def sphere_paths(phi, eps, alm_step=6, az_step=10, hours=True):
    """Engraving curves on the sphere (equatorial frame, lat=declination,
    lon=hour angle) for latitude phi."""
    Z, S, W = horizon_frame(phi)
    paths = []
    def circle_pts(axis, rho, n=361):
        a = unit(axis)
        tmp = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
        u = unit(np.cross(a, tmp)); v = np.cross(a, u)
        return [math.cos(rho * DEG) * a + math.sin(rho * DEG) * (math.cos(t) * u + math.sin(t) * v) for t in np.linspace(0, 2 * math.pi, n)]
    for h in range(0, 90, alm_step):
        paths.append(('alm %d' % h, [p for p in circle_pts(Z, 90 - h)]))
    for A in range(0, 180, az_step):
        Dv = math.cos(A * DEG) * S + math.sin(A * DEG) * W
        pts = [p for p in circle_pts(np.cross(Z, Dv), 90) if np.dot(p, Z) >= 0]
        paths.append(('az %d' % A, pts))
    paths.append(('equator', circle_pts(np.array([0, 0, 1.0]), 90)))
    paths.append(('tropic N', circle_pts(np.array([0, 0, 1.0]), 90 - eps)))
    paths.append(('tropic S', circle_pts(np.array([0, 0, 1.0]), 90 + eps)))
    if hours and abs(math.tan(phi * DEG) * math.tan(eps * DEG)) < 1:
        for n in range(1, 12):
            pts = []
            for d in np.linspace(-eps, eps, 40):
                H0 = math.acos(-math.tan(phi * DEG) * math.tan(d * DEG)) / DEG
                Hh = H0 + n / 12 * (360 - 2 * H0)
                Hr, dr = Hh * DEG, d * DEG
                pts.append(np.array([math.cos(dr) * math.cos(Hr), math.cos(dr) * math.sin(Hr), math.sin(dr)]))
            paths.append(('hour %d' % n, pts))
    return paths


def ortho_view(paths, R, view):
    """Orthographic view of the sphere engraving. view 'front' (from south,
    looking north) or 'top' (from zenith)."""
    Dr = Drawing(title=view)
    Dr.circle((0, 0), R, 'CUT_OUTER')
    for name, pts in paths:
        seg = []
        for p in pts:
            if view == 'front':
                vis = p[0] >= 0
                q = (p[1] * R, p[2] * R)
            else:
                vis = True
                q = (p[1] * R, p[0] * R)
            if vis:
                seg.append(q)
            else:
                if len(seg) > 1:
                    Dr.poly(seg, False, 'ENGRAVE' if name.startswith(('alm 0', 'equator')) else 'ENGRAVE_FINE')
                seg = []
        if len(seg) > 1:
            Dr.poly(seg, False, 'ENGRAVE' if name.startswith(('alm 0', 'equator')) else 'ENGRAVE_FINE')
    return Dr


def unwrap_map(paths, R):
    """Equirectangular engraving template: x = hour angle * R, y = dec * R
    (arc lengths on the sphere).  Used for 4-axis rotary engraving."""
    Dr = Drawing(title='unwrap')
    Dr.poly([(-math.pi * R, -math.pi / 2 * R), (math.pi * R, -math.pi / 2 * R), (math.pi * R, math.pi / 2 * R), (-math.pi * R, math.pi / 2 * R)], True, 'GUIDE')
    for name, pts in paths:
        seg, last = [], None
        for p in pts:
            lon = math.atan2(p[1], p[0]); lat = math.asin(max(-1, min(1, p[2])))
            q = (lon * R, lat * R)
            if last is not None and abs(q[0] - last[0]) > math.pi * R:
                if len(seg) > 1:
                    Dr.poly(seg, False, 'ENGRAVE')
                seg = []
            seg.append(q); last = q
        if len(seg) > 1:
            Dr.poly(seg, False, 'ENGRAVE')
    return Dr


def paths_csv(paths, R):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['curve', 'point', 'x_mm', 'y_mm', 'z_mm', 'declination_deg', 'hour_angle_deg'])
    for name, pts in paths:
        for i, p in enumerate(pts):
            w.writerow([name, i, f'{p[0]*R:.3f}', f'{p[1]*R:.3f}', f'{p[2]*R:.3f}',
                        f'{math.asin(max(-1, min(1, p[2])))/DEG:.4f}', f'{math.atan2(p[1], p[0])/DEG:.4f}'])
    return out.getvalue()


def band_strip(Rc, width, ticks=None, labels=None, title='band', span=360):
    """Flat development of a great-circle band of the spherical rete:
    straight strip of length = arc length at centre radius Rc."""
    Dr = Drawing(title=title)
    L = 2 * math.pi * Rc * span / 360
    Dr.poly([(0, 0), (L, 0), (L, width), (0, width)], True, 'CUT_OUTER')
    if ticks:
        for v in range(0, span + 1, ticks):
            x = L * v / span
            l = width * (0.6 if v % 10 == 0 else 0.4 if v % 5 == 0 else 0.22)
            Dr.line((x, width), (x, width - l), 'ENGRAVE' if v % 5 == 0 else 'ENGRAVE_FINE')
    if labels:
        for i, lab in enumerate(labels):
            Dr.text(lab, (L * (i + 0.5) / len(labels), width * 0.22), width * 0.28)
    Dr.L = L
    return Dr


def build_spherical(spec):
    D = spec['D']; R = D / 2
    phi = spec['lat']; eps = spec.get('eps', 23.5)
    variant = spec.get('variant', 'nayrizi')
    parts, views = [], []
    paths = sphere_paths(phi, eps, alm_step=6 if D >= 120 else 10, az_step=10 if D >= 120 else 15)
    front = ortho_view(paths, R, 'front')
    top = ortho_view(paths, R, 'top')
    unwrap = unwrap_map(paths, R)
    blank = Drawing(title='hemisphere blank')
    rb = math.sqrt(2) * R + 3
    blank.circle((0, 0), rb, 'CUT_OUTER'); blank.circle((0, 0), R, 'GUIDE')
    parts.append(('sphere_blank', 'قرص خام لتشكيل نصف الكرة بالبرم/الطرق (×٢) - قطر %.0f مم' % (2 * rb), blank, 'brass', 1.2, 2))
    parts.append(('sphere_unwrap', 'خريطة حفر سطح الكرة (طول × عرض بأطوال الأقواس) - للمخرطة/المحور الرابع', unwrap, 'engraving template', None, 0))
    parts.append(('sphere_front', 'منظر أمامي لخطوط الكرة (المقنطرات والسموت والساعات) لعرض %s' % dms(phi), front, 'view', None, 0))
    parts.append(('sphere_top', 'منظر علوي من السمت', top, 'view', None, 0))
    tb = clamp(0.012 * D, 1.0, 2.0)
    wb = clamp(0.07 * D, 5, 14)
    Rc = R + tb / 2 + 0.3
    sign_names = SIGNS_LA if is_latin(spec) else SIGNS_AR
    ecl = band_strip(Rc, wb, ticks=1 if D >= 120 else 2, labels=sign_names, title='ecliptic band')
    span_ecl = 360 if variant in ('biruni', 'alfonso', 'musa') else 180
    if span_ecl == 180:
        ecl = band_strip(Rc, wb, ticks=1 if D >= 120 else 2, labels=sign_names[9:] + sign_names[:3], title='ecliptic half band', span=180)
    parts.append(('ecliptic_band', 'حلقة فلك البروج من العنكبوت (فرد، تُلف على قطر %.1f مم)' % (2 * Rc), ecl, 'brass', tb, 1))
    if variant in ('biruni', 'alfonso', 'marrakushi', 'musa'):
        eq = band_strip(Rc, wb * 0.7, ticks=5 if variant == 'marrakushi' else None, title='equator band',
                        span=180 if variant == 'marrakushi' else 360)
        parts.append(('equator_band', 'حلقة معدل النهار (فرد)', eq, 'brass', tb, 1))
    if variant == 'biruni':
        parts.append(('colure_band', 'حلقة المارة بالأقطاب الأربعة (فرد)', band_strip(Rc, wb * 0.7, title='colure'), 'brass', tb, 1))
    if variant in ('nayrizi', 'alfonso', 'musa'):
        q = band_strip(Rc + tb, wb * 0.8, ticks=1, title='altitude quadrant', span=90)
        mid = q.L
        q.poly([(0, wb * 0.33), (mid, wb * 0.33), (mid, wb * 0.47), (0, wb * 0.47)], True, 'CUT_INNER')
        parts.append(('alt_quadrant', 'ربع الارتفاع (شريط بمجرى في وسطه، فرد)', q, 'brass', tb, 1))
    # star pointers table: positions relative to the ecliptic band
    year = spec.get('year', 1000)
    stars = []
    for ra, de, ar, la in STARS[:spec.get('stars', 16)]:
        a, d = precess_star(ra, de, year, eps)
        from geom import eq_to_ecl
        lam, beta = eq_to_ecl(a, d, eps)
        if span_ecl == 180 and beta < 0 and variant == 'nayrizi':
            continue
        stars.append((ar, la, lam, beta))
    tabs = Drawing(title='star pointers')
    for i, (ar, la, lam, beta) in enumerate(stars):
        Lp = abs(beta) * DEG * Rc + wb / 2
        x = (i % 6) * 18; y = -(i // 6) * (Lp + 12) if False else -(i // 6) * 60
        Lp = min(Lp, 50)
        tabs.poly([(x - 2.5, y), (x + 2.5, y), (x + 0.4, y + Lp), (x - 0.4, y + Lp)], True, 'CUT_OUTER')
        tabs.text(la[:6], (x, y - 3), 2)
    parts.append(('star_pointers', 'مؤشرات الكواكب (طول كل مؤشر = عرض الكوكب × نصف القطر) - انظر الجدول', tabs, 'brass', tb, len(stars)))
    # kursi rings
    k = Drawing(title='kursi')
    for i, rr in enumerate((0.16 * D, 0.11 * D)):
        cx = i * 0.4 * D
        k.circle((cx, 0), rr, 'CUT_OUTER'); k.circle((cx, 0), rr * 0.6, 'CUT_INNER'); k.hole((cx, 0), 3)
        for a in range(0, 360, 60):
            k.hole(polar(rr * 0.8, a, (cx, 0)), rr * 0.18)
    parts.append(('kursi', 'الكراسي (أقراص مفرغة عند قطب البروج وقطب المعدل)', k, 'brass', tb, 1))
    gn = Drawing(title='gnomon')
    gh = clamp(0.08 * D, 5, 14)
    gn.poly([(-2, 0), (2, 0), (2, gh), (-2, gh)], True, 'CUT_OUTER')
    gn.hole((0, gh * 0.6), 1.0)
    parts.append(('gnomon', 'الشاخص الصغير (أسطوانة مثقوبة)', gn, 'brass', 4, 1))
    ring = Drawing(title='ring')
    ring.circle((0, 0), 0.1 * D, 'CUT_OUTER'); ring.circle((0, 0), 0.075 * D, 'CUT_INNER')
    parts.append(('ring', 'حلقة التعليق', ring, 'brass', 2, 1))
    if variant == 'marrakushi':
        sf = Drawing(title='safiha')
        Lb = R * math.pi / 2
        sf.poly([(-8, 0), (8, 0), (1.5, Lb), (-1.5, Lb)], True, 'CUT_OUTER')
        sf.hole((0, 3), 1.5); sf.hole((0, Lb - 3), 1.5)
        parts.append(('safiha', 'الصفيحة: مثلث كروي متساوي الساقين (ارتفاعه ربع دائرة = %.1f مم)' % Lb, sf, 'brass', 1, 1))
    if variant == 'musa':
        c = Drawing(title='coaster')
        c.poly([(-5, 0), (5, 0), (5, 8), (-5, 8)], True, 'CUT_OUTER'); c.hole((0, 4), 1)
        parts.append(('coaster', 'المزلقة المتحركة في مجرى ربع خط نصف النهار مع ثقب الرصد', c, 'brass', 1.5, 1))
    if variant == 'stand':
        st = Drawing(title='stand')
        Hs = spec.get('stand', 115)
        mer = band_strip(R + 2, 6, ticks=None, title='meridian ring')
        for latk in range(0, 91, 6):
            x = mer.L * latk / 360
            mer.hole((x, 3), 1.6)
            mer.hole((x + mer.L / 2, 3), 1.6)
        parts.append(('meridian_ring', 'حلقة نصف النهار بثقوب للعروض كل ٦° (فرد)', mer, 'brass', 2, 1))
        hz = Drawing(title='horizon ring')
        hz.circle((0, 0), R + 10, 'CUT_OUTER'); hz.circle((0, 0), R + 2.5, 'CUT_INNER')
        hz.circle((0, 0), R + 9, 'ENGRAVE')
        for a in range(0, 360, 5):
            hz.line(polar(R + 9, a), polar(R + (7 if a % 10 else 5.5), a), 'ENGRAVE')
        parts.append(('horizon_ring', 'حلقة الأفق للحامل', hz, 'brass', 2, 1))
        leg = Drawing(title='leg')
        leg.poly([(-3, 0), (3, 0), (2, Hs - R), (-2, Hs - R)], True, 'CUT_OUTER')
        parts.append(('legs', 'أرجل الحامل (×٣)، الارتفاع الكلي %.1f مم' % Hs, leg, 'brass', 3, 3))
    views += [('sphere front', front), ('sphere top', top)]
    star_rows = [(ar if not is_latin(spec) else la, lam, beta) for ar, la, lam, beta in stars]
    return parts, views, {'csv': paths_csv(paths, R), 'stars_ecl': star_rows}


# =========================================================================== linear astrolabe (al-Tusi's staff)
def build_linear(spec):
    Lt = spec['L']
    phi = spec.get('lat', 36.3)
    eps = spec.get('eps', 23.5)
    R_cap = (Lt - 30) / 2
    P = PolarProj(R_cap, eps)
    parts, views = [], []
    W = 26
    st = Drawing(title='staff')
    st.poly([(-Lt / 2, -W / 2), (Lt / 2, -W / 2), (Lt / 2, W / 2), (-Lt / 2, W / 2)], True, 'CUT_OUTER')
    st.line((-R_cap, 0), (R_cap, 0), 'ENGRAVE')
    st.text('M', (-R_cap - 4, 0), 3); st.text('M', (R_cap + 4, 0), 3); st.text('P', (0, 2.5), 3)
    st.line((0, -W / 2), (0, W / 2), 'ENGRAVE')
    # declinations: y = r(d) on the south half (x<0 as in Michel's diagram)
    for d in range(-int(eps), 91):
        x = -P.r(d)
        if abs(x) > R_cap + 0.01:
            continue
        l = 5 if d % 10 == 0 else 3.5 if d % 5 == 0 else 2
        st.line((x, 0), (x, -l), 'ENGRAVE' if d % 5 == 0 else 'ENGRAVE_FINE')
        if d % 10 == 0:
            st.text(abjad(abs(d)) if d else '٠', (x, -7.5), 2.2)
    # altitudes (meridian intersections of the almucantars)
    Z, S, W_ = horizon_frame(phi)
    for h in range(0, 91, 1):
        y1 = P.P(altaz_vec(phi, h, 0))[1]
        y2 = P.P(altaz_vec(phi, h, 180))[1] if h < 90 else y1
        for y in (y1, y2):
            if abs(y) <= R_cap:
                l = 5 if h % 10 == 0 else 3.5 if h % 5 == 0 else 2
                st.line((y, 0), (y, l), 'ENGRAVE' if h % 5 == 0 else 'ENGRAVE_FINE')
        if h % 10 == 0 and abs(y1) <= R_cap:
            st.text(abjad(h) if h else '٠', (y1, 7.5), 2.2)
    # centres of the almucantars (second face)
    st2 = Drawing(title='staff face 2')
    st2.poly([(-Lt / 2, -W / 2), (Lt / 2, -W / 2), (Lt / 2, W / 2), (-Lt / 2, W / 2)], True, 'CUT_OUTER')
    st2.line((-R_cap, 0), (R_cap, 0), 'ENGRAVE')
    st2.line((0, -W / 2), (0, W / 2), 'ENGRAVE')
    for h in range(0, 90, 2):
        y1 = P.P(altaz_vec(phi, h, 0))[1]
        y2 = P.P(altaz_vec(phi, h, 180))[1]
        c = (y1 + y2) / 2
        if abs(c) <= R_cap:
            st2.line((c, 0), (c, 4 if h % 10 == 0 else 2.5), 'ENGRAVE')
            if h % 10 == 0:
                st2.text(abjad(h) if h else '٠', (c, 7), 2.2)
    # chord scale of the equator circle: chord(t) = 2 R_eq sin(t/2), from P
    for t in range(0, 181, 2):
        x = 2 * P.R_eq * math.sin(t / 2 * DEG)
        if x <= R_cap:
            st2.line((x, 0), (x, -(4 if t % 10 == 0 else 2.5)), 'ENGRAVE')
            if t % 20 == 0:
                st2.text(abjad(t) if t else '٠', (x, -7), 2.2)
    st2.text('مقياس الأوتار', (R_cap * 0.5, -11), 2.5)
    st2.text('مراكز المقنطرات', (-R_cap * 0.5, 10.5), 2.5)
    st.text('الميول', (-R_cap * 0.5, -11), 2.5)
    st.text('الارتفاعات لعرض ' + dms(phi, 'abjad'), (R_cap * 0.4, 10.5), 2.5)
    parts += [('staff_face1', 'العصا - الوجه الأول: الميول والارتفاعات (طول %d مم)' % Lt, st, 'wood + paper', 14, 1),
              ('staff_face2', 'العصا - الوجه الثاني: مراكز المقنطرات ومقياس الأوتار', st2, 'wood + paper', None, 0)]
    wt = Drawing(title='weights')
    for i in range(3):
        wt.circle((i * 16, 0), 5, 'CUT_OUTER'); wt.hole((i * 16, 0), 1.2)
    parts.append(('weights', 'الأثقال النحاسية للخيوط (×٣) قطر ١٠ مم', wt, 'brass', 10, 3))
    views.append(('staff', st))
    return parts, views
