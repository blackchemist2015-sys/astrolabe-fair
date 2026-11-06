"""Trace the outline of the mater + throne (kursi) from the photographs of
the book, so that the cut outline reproduces the original decoration.

The photo is segmented (instrument vs. background), the mater circle is
fitted on the lower part of the contour, the suspension ring is removed,
the silhouette is symmetrised about the vertical axis and returned in
millimetres (centre of the mater = origin, y up) scaled to the diameter
of the model given by the book."""
import math
import numpy as np
import cv2


def segment(img):
    """foreground mask: brass is a saturated yellow, the backgrounds of the
    photographs (black, white, grey gradients) are unsaturated."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 1] > 50) & (hsv[..., 2] > 55) & (hsv[..., 0] >= 5) & (hsv[..., 0] <= 40)).astype(np.uint8) * 255
    k = max(3, int(min(img.shape[:2]) * 0.006)) | 1
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lbl, st, _ = cv2.connectedComponentsWithStats(m)
    kk = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    m = (lbl == kk).astype(np.uint8) * 255
    # fill interior holes that are not background-coloured openwork:
    # holes of the mater disc (silver rete, shadows) are filled, holes in the
    # throne stay (they are checked against the background colour)
    inv = cv2.bitwise_not(m)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(inv)
    hsvb = hsv.reshape(-1, 3)
    border = np.concatenate([hsv[:5].reshape(-1, 3), hsv[-5:].reshape(-1, 3), hsv[:, :5].reshape(-1, 3), hsv[:, -5:].reshape(-1, 3)]).astype(float)
    bgv = np.median(border[:, 2])
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if x == 0 or y == 0 or x + w >= m.shape[1] or y + h >= m.shape[0]:
            continue
        reg = lbl == i
        v = hsv[..., 2][reg].astype(float)
        sat = hsv[..., 1][reg].astype(float)
        # a real hole shows the background: similar brightness, low saturation
        if abs(np.median(v) - bgv) < 45 and np.median(sat) < 60:
            continue
        m[reg] = 255
    return m


def segment_color(img):
    h, w = img.shape[:2]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    border = np.concatenate([lab[:6].reshape(-1, 3), lab[-6:].reshape(-1, 3), lab[:, :6].reshape(-1, 3), lab[:, -6:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    d = np.sqrt(((lab - bg) ** 2).sum(2))
    # brass is saturated yellow: weight b* channel strongly
    sat = np.abs(lab[..., 2] - 128) + 0.5 * np.abs(lab[..., 1] - 128)
    score = d + 1.2 * sat
    _, m = cv2.threshold(np.clip(score, 0, 255).astype(np.uint8), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lbl, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    return (lbl == k).astype(np.uint8) * 255


def fit_circle(pts):
    x, y = pts[:, 0].astype(float), pts[:, 1].astype(float)
    A = np.stack([x, y, np.ones_like(x)], 1)
    b = x * x + y * y
    c = np.linalg.lstsq(A, b, rcond=None)[0]
    cx, cy = c[0] / 2, c[1] / 2
    return cx, cy, math.sqrt(c[2] + cx * cx + cy * cy)


def mater_circle(mask, polygon=False):
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :]
    # first guess from the lower 60% of the bounding box
    y0, y1 = c[:, 1].min(), c[:, 1].max()
    sel = c[c[:, 1] > y0 + 0.45 * (y1 - y0)]
    cx, cy, r = fit_circle(sel)
    for _ in range(4):
        ang = np.degrees(np.arctan2(-(c[:, 1] - cy), c[:, 0] - cx))
        dist = np.hypot(c[:, 0] - cx, c[:, 1] - cy)
        ok = (ang < 30) & (ang > -210) & (np.abs(dist - r) < 0.04 * r)
        ok |= (ang > 150) & (np.abs(dist - r) < 0.04 * r)
        if ok.sum() > 50:
            cx, cy, r = fit_circle(c[ok])
    return cx, cy, r


def throne_mask(mask, cx, cy, r):
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    out = mask.copy()
    out[(xx - cx) ** 2 + (yy - cy) ** 2 <= (r * 1.0) ** 2] = 0
    out[yy > cy] = 0
    # cut away the suspension ring: walking up the centre line, the throne
    # ends where the silhouette becomes a narrow neck (shackle) – the ring
    # starts above it.
    top_disc = int(cy - r)
    band = out[:, int(cx - 0.7 * r): int(cx + 0.7 * r)]
    widths = (band > 0).sum(1)
    cut = None
    neck = 0.075 * r
    y = top_disc
    seen_wide = False
    while y > 0:
        if widths[y] > 2 * neck:
            seen_wide = True
        if seen_wide and widths[y] < neck:
            # check that it stays narrow for a while (neck) or ends
            cut = y
            break
        y -= 1
    if cut is not None:
        out[:cut] = 0
    # thin links (shackle, chain) are removed by an opening
    k = max(3, int(0.012 * r)) | 1
    out = cv2.morphologyEx(out, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lbl, st, _ = cv2.connectedComponentsWithStats(out)
    if n > 1:
        # keep components touching the disc
        keep = np.zeros_like(out)
        for i in range(1, n):
            ys, xs = np.nonzero(lbl == i)
            if (np.hypot(xs - cx, ys - cy) < r * 1.03).any() and st[i, cv2.CC_STAT_AREA] > (0.02 * r) ** 2:
                keep[lbl == i] = 255
        out = keep
    return out


def symmetrise(m, cx):
    h, w = m.shape
    M = np.float32([[-1, 0, 2 * cx], [0, 1, 0]])
    mir = cv2.warpAffine(m, M, (w, h), flags=cv2.INTER_NEAREST)
    a = ((m.astype(np.float32) + mir.astype(np.float32)) / 2 >= 127).astype(np.uint8) * 255
    return a


def trace_outline(path, D_mm, upscale=2, show=None):
    img = cv2.imread(path)
    img = cv2.resize(img, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    mask = segment(img)
    cx, cy, r = mater_circle(mask)
    th = throne_mask(mask, cx, cy, r)
    th = symmetrise(th, cx)
    # union with an overlap band into the disc so that the outline is closed
    h, w = th.shape
    yy, xx = np.mgrid[0:h, 0:w]
    th[((xx - cx) ** 2 + (yy - cy) ** 2 <= (r * 1.0) ** 2) & ((xx - cx) ** 2 + (yy - cy) ** 2 >= (r * 0.93) ** 2) & (yy < cy) & (np.abs(xx - cx) < np.abs(np.nonzero(th.any(0))[0] - cx).max() if th.any() else 0)] = 255
    s = (D_mm / 2) / r
    cs, hier = cv2.findContours(th, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for i, c in enumerate(cs):
        if len(c) < 8:
            continue
        eps = 0.0025 * r
        c2 = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        pts = [((x - cx) * s, (cy - y) * s) for x, y in c2]
        is_hole = hier[0][i][3] >= 0
        if abs(cv2.contourArea(c)) * s * s < (0.008 * D_mm) ** 2:
            continue
        polys.append((pts, is_hole))
    if show:
        vis = img.copy()
        cv2.circle(vis, (int(cx), int(cy)), int(r), (0, 0, 255), 3)
        cv2.drawContours(vis, cs, -1, (255, 0, 0), 3)
        cv2.imwrite(show, vis[max(0,int(cy-1.6*r)):int(cy-0.6*r), max(0,int(cx-0.8*r)):int(cx+0.8*r)])
    return polys, (cx, cy, r)


# ---------------------------------------------------------------------------
# v2: perspective (ellipse) rectification, throne with explicit cut height,
# silver rete extraction, rectified photo for overlays
def rectify(path, upscale=2, fit='lower'):
    """Load a photo, fit an ellipse to the rim of the mater and warp the
    image so that the rim becomes an exact circle.  Returns
    (image, mask, cx, cy, r) in the rectified image."""
    img = cv2.imread(path)
    img = cv2.resize(img, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
    mask = segment(cv2.GaussianBlur(img, (5, 5), 0))
    cx, cy, r = mater_circle(mask)
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    ang = np.degrees(np.arctan2(-(c[:, 1] - cy), c[:, 0] - cx))
    dist = np.hypot(c[:, 0] - cx, c[:, 1] - cy)
    ok = (np.abs(dist - r) < 0.05 * r) & ((ang < 40) | (ang > 140) | (ang < -0))
    ok &= ~((ang > 40) & (ang < 140))          # skip the throne
    pts = c[ok]
    if len(pts) > 30:
        (ex, ey), (MA, ma), th = cv2.fitEllipse(pts)
        a, b = MA / 2, ma / 2
        R = math.sqrt(a * b)
        t = math.radians(th)
        Rm = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
        S = np.diag([R / a, R / b])
        A = Rm @ S @ Rm.T
        M = np.hstack([A, (np.array([ex, ey]) - A @ np.array([ex, ey]))[:, None]]).astype(np.float32)
        h, w = img.shape[:2]
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        mask = cv2.warpAffine(mask, M, (w, h), flags=cv2.INTER_NEAREST)
        cx, cy, r = ex, ey, R
    return img, mask, cx, cy, r


def contours_mm(m, cx, cy, s, eps_px, min_area_mm2):
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    if hier is None:
        return polys
    for i, c in enumerate(cs):
        if len(c) < 6:
            continue
        if abs(cv2.contourArea(c)) * s * s < min_area_mm2:
            continue
        c2 = cv2.approxPolyDP(c, eps_px, True)[:, 0, :]
        if len(c2) < 3:
            continue
        polys.append(([((x - cx) * s, (cy - y) * s) for x, y in c2], hier[0][i][3] >= 0))
    return polys


def throne_v2(path, D_mm, cut_h, upscale=3):
    """Throne silhouette (with its openwork) above the mater, cut at
    cut_h * r above the rim (to drop shackle and ring)."""
    img, mask, cx, cy, r = rectify(path, upscale)
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    out = mask.copy()
    out[yy < int(cy - r - cut_h * r)] = 0
    out[yy > cy] = 0
    # keep only what is attached to the rim
    n, lbl, st, _ = cv2.connectedComponentsWithStats(out)
    keep = np.zeros_like(out)
    for i in range(1, n):
        ys, xs = np.nonzero(lbl == i)
        if (np.hypot(xs - cx, ys - cy) < r * 1.02).any():
            keep[lbl == i] = 255
    out = keep
    out[(xx - cx) ** 2 + (yy - cy) ** 2 < (0.97 * r) ** 2] = 0
    k = max(3, int(0.01 * r)) | 1
    out = cv2.morphologyEx(out, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    out = symmetrise(out, cx)
    s = (D_mm / 2) / r
    return contours_mm(out, cx, cy, s, 0.002 * r, (0.012 * D_mm) ** 2), (img, cx, cy, r)


def silver_rete(path, R_cap_mm, upscale=3):
    """Silver rete on a brass astrolabe (Hama 1299): segment the low-saturation
    bright metal inside the limb and vectorise it."""
    img, mask, cx, cy, r = rectify(path, upscale)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 1] < 75) & (hsv[..., 2] > 115)).astype(np.uint8) * 255
    h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.hypot(xx - cx, yy - cy)
    m[rr > 0.86 * r] = 0
    k = max(3, int(0.008 * r)) | 1
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    # outer radius of the rete = radius containing 99% of the mask
    rs = rr[m > 0]
    r_out = np.percentile(rs, 99.5)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(m)
    k0 = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    m = (lbl == k0).astype(np.uint8) * 255
    s = R_cap_mm / r_out
    return contours_mm(m, cx, cy, s, 0.0015 * r, (0.004 * R_cap_mm * 2) ** 2), (img, cx, cy, r, r_out)


def photo_for_overlay(path, out_jpg, upscale=2, quality=80):
    img, mask, cx, cy, r = rectify(path, upscale)
    cv2.imwrite(out_jpg, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    h, w = img.shape[:2]
    return cx, cy, r, w, h
