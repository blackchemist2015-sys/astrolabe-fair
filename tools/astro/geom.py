"""
Spherical astronomy and stereographic projection used to compute every
engraved line.  Nothing here is traced from pictures: all circles are
obtained from the projection of the corresponding circle of the sphere.

Plate convention (front of a northern astrolabe, viewed from the front):
  centre = north celestial pole, +y = upper meridian (south), +x = west.
  A point of hour angle H (west positive) and declination d lies at
  radius r(d) = R_eq * tan((90-d)/2) and plate angle such that
  x = r sin H, y = r cos H.
"""
import math
import numpy as np
from core import DEG, polar

EPS_DEFAULT = 23 + 35 / 60.0  # 23;35 deg - the value of the Ma'munic tables


# ------------------------------------------------------------------ vectors
def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def eq_vec(H, d):
    """unit vector, equatorial frame: X toward (H=0,d=0) i.e. south point of the
    equator on the meridian, Y toward west (H=90), Z north pole."""
    H, d = H * DEG, d * DEG
    return np.array([math.cos(d) * math.cos(H), math.cos(d) * math.sin(H), math.sin(d)])


def vec_Hd(v):
    v = unit(v)
    return math.atan2(v[1], v[0]) / DEG, math.asin(max(-1, min(1, v[2]))) / DEG


# ------------------------------------------------------------------ polar stereographic projection (astrolabe)
class PolarProj:
    def __init__(self, R_cap, eps=EPS_DEFAULT):
        self.eps = eps
        self.R_cap = R_cap
        self.R_eq = R_cap / math.tan((90 + eps) / 2 * DEG)
        self.R_can = self.r(eps)

    def r(self, d):
        return self.R_eq * math.tan((90 - d) / 2 * DEG)

    def dec_of_r(self, r):
        return 90 - 2 * math.atan(r / self.R_eq) / DEG

    def P(self, v):
        v = unit(v)
        k = self.R_eq / (1 + v[2])
        # plate x = west component, plate y = meridian component
        return (k * v[1], k * v[0])

    def inv(self, p):
        X, Y = p[1] / self.R_eq, p[0] / self.R_eq
        q = X * X + Y * Y
        return np.array([2 * X, 2 * Y, 1 - q]) / (1 + q)

    def P_Hd(self, H, d):
        r = self.r(d)
        return (r * math.sin(H * DEG), r * math.cos(H * DEG))


class EquinoxProj:
    """Projection of the universal disc (saphaea): from the vernal equinox
    point onto the plane of the solstitial colure.  Frame: x = equinox
    direction, z = north pole.  Disc radius R  (the colure itself)."""
    def __init__(self, R):
        self.R = R

    def P(self, v):
        v = unit(v)
        k = self.R / (1 + v[0])
        # +x on disc = toward the Cancer solstice(y), +y on disc = north pole
        return (k * v[1], k * v[2])

    def inv(self, p):
        a, b = p[0] / self.R, p[1] / self.R
        q = a * a + b * b
        return np.array([1 - q, 2 * a, 2 * b]) / (1 + q)


# ------------------------------------------------------------------ circle fitting
def fit_circle(p1, p2, p3):
    ax, ay = p1; bx, by = p2; cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9 * max(1, abs(ax) + abs(bx) + abs(cx)):
        return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def sphere_circle(axis, rho_deg, proj, avoid=None):
    """Project the small/great circle of angular radius rho around `axis`.
    Returns ('circle', centre, r) or ('line', point, direction)."""
    a = unit(axis)
    tmp = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    u = unit(np.cross(a, tmp)); v = np.cross(a, u)
    rho = rho_deg * DEG
    def pt(t):
        return math.cos(rho) * a + math.sin(rho) * (math.cos(t) * u + math.sin(t) * v)
    # choose sample points far from the projection pole
    ts = np.linspace(0, 2 * math.pi, 37)[:-1]
    if isinstance(proj, PolarProj):
        bad = lambda w: w[2]
    else:
        bad = lambda w: w[0]
    good = sorted(ts, key=lambda t: bad(pt(t)), reverse=True)
    # pick three well separated points among good ones
    chosen = [good[0]]
    for t in good[1:]:
        if all(abs(((t - c + math.pi) % (2 * math.pi)) - math.pi) > 0.6 for c in chosen):
            chosen.append(t)
        if len(chosen) == 3:
            break
    ps = [proj.P(pt(t)) for t in chosen]
    fc = fit_circle(*ps)
    if fc is None or fc[1] > 1e5:
        d = np.subtract(ps[1], ps[0])
        return ('line', ps[0], tuple(d / np.linalg.norm(d)))
    return ('circle', fc[0], fc[1])


# ------------------------------------------------------------------ clipping helpers
def arc_intervals(c, r, inside, n=720, a_from=0.0, a_to=360.0):
    """Return list of (a0,a1) sub-arcs of circle (c,r) where inside(p) holds.
    Ends refined by bisection to 1e-7 deg."""
    angs = np.linspace(a_from, a_to, n + 1)
    flags = [inside(polar(r, a, c)) for a in angs]
    def refine(a, b, fa):
        for _ in range(40):
            m = (a + b) / 2
            if inside(polar(r, m, c)) == fa:
                a = m
            else:
                b = m
        return (a + b) / 2
    res, start = [], None
    for i in range(len(angs)):
        if flags[i] and start is None:
            start = angs[i] if i == 0 else refine(angs[i - 1], angs[i], False)
        if not flags[i] and start is not None:
            end = refine(angs[i - 1], angs[i], True)
            res.append([start, end]); start = None
    if start is not None:
        res.append([start, angs[-1]])
    # merge wrap-around for full circles
    full = abs((a_to - a_from) - 360) < 1e-9
    if full and len(res) >= 2 and res[0][0] == a_from and abs(res[-1][1] - a_to) < 1e-9:
        res[0][0] = res[-1][0] - 360
        res.pop()
    if full and len(res) == 1 and res[0][0] == a_from and res[0][1] == a_to:
        return [(0, 360)]
    return [tuple(x) for x in res]


def seg_intervals(p0, p1, inside, n=400):
    out, start = [], None
    def P(t):
        return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
    ts = np.linspace(0, 1, n + 1)
    fl = [inside(P(t)) for t in ts]
    def refine(a, b, fa):
        for _ in range(40):
            m = (a + b) / 2
            if inside(P(m)) == fa:
                a = m
            else:
                b = m
        return (a + b) / 2
    for i, t in enumerate(ts):
        if fl[i] and start is None:
            start = t if i == 0 else refine(ts[i - 1], t, False)
        if not fl[i] and start is not None:
            out.append((P(start), P(refine(ts[i - 1], t, True)))); start = None
    if start is not None:
        out.append((P(start), P(1)))
    return out


def draw_projected(D, sc, inside, layer='ENGRAVE', line_extent=1000, w=None):
    """Draw projected sphere circle `sc` clipped by `inside` predicate."""
    if sc[0] == 'circle':
        for a0, a1 in arc_intervals(sc[1], sc[2], inside):
            D.arc(sc[1], sc[2], a0, a1, layer, w)
    else:
        p, dvec = sc[1], sc[2]
        p0 = (p[0] - dvec[0] * line_extent, p[1] - dvec[1] * line_extent)
        p1 = (p[0] + dvec[0] * line_extent, p[1] + dvec[1] * line_extent)
        for a, b in seg_intervals(p0, p1, inside, n=4000):
            D.line(a, b, layer, w)


# ------------------------------------------------------------------ horizon frame
def horizon_frame(phi):
    """unit vectors (equatorial frame) of zenith, south and west points."""
    Z = eq_vec(0, phi)
    S = eq_vec(0, phi - 90)
    W = np.array([0.0, 1.0, 0.0])
    return Z, S, W


def altaz_vec(phi, alt, az_from_south_west):
    Z, S, W = horizon_frame(phi)
    a, A = alt * DEG, az_from_south_west * DEG
    return math.cos(a) * (math.cos(A) * S + math.sin(A) * W) + math.sin(a) * Z


# ------------------------------------------------------------------ ecliptic / sun / stars
def ecl_to_eq(lam, beta, eps):
    l, b, e = lam * DEG, beta * DEG, eps * DEG
    x = math.cos(b) * math.cos(l)
    y = math.cos(b) * math.sin(l) * math.cos(e) - math.sin(b) * math.sin(e)
    z = math.cos(b) * math.sin(l) * math.sin(e) + math.sin(b) * math.cos(e)
    ra = math.atan2(y, x) / DEG % 360
    dec = math.asin(z) / DEG
    return ra, dec


def eq_to_ecl(ra, dec, eps):
    a, d, e = ra * DEG, dec * DEG, eps * DEG
    x = math.cos(d) * math.cos(a)
    y = math.cos(d) * math.sin(a) * math.cos(e) + math.sin(d) * math.sin(e)
    z = -math.cos(d) * math.sin(a) * math.sin(e) + math.sin(d) * math.cos(e)
    return math.atan2(y, x) / DEG % 360, math.asin(z) / DEG


def true_obliquity(year):
    T = (year - 2000) / 100.0
    return 23.439291 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T ** 3


def precess_star(ra2000, dec2000, year, eps_instr):
    """Precess J2000 star to the epoch `year` (rigorous enough for engraving:
    constant precession in longitude, latitude fixed) and return RA/Dec
    computed with the obliquity the instrument maker used."""
    lam, beta = eq_to_ecl(ra2000, dec2000, 23.4392911)
    lam_e = lam + 50.29 / 3600.0 * (year - 2000)
    return ecl_to_eq(lam_e % 360, beta, eps_instr)


def julian_day(y, m, d):
    """Julian calendar date -> JD (for medieval instruments)."""
    if m <= 2:
        y -= 1; m += 12
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d - 1524.5


def gregorian_jd(y, m, d):
    if m <= 2:
        y -= 1; m += 12
    A = y // 100; B = 2 - A + A // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5


def sun_longitude(jd):
    n = jd - 2451545.0
    L = 280.460 + 0.9856474 * n
    g = (357.528 + 0.9856003 * n) * DEG
    return (L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360


MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
