"""Build all workshop drawings.

Version 2: exact drawings (true circles and arcs, no hand-drawn wobble),
identical cut outline on both faces of every piece, thrones (and the silver
rete of A2.17) traced from the photographs of the book, and overlay sheets
of the book photographs at true scale.

usage:  python3 trace_all.py /path/Volume2EN.pdf     (once: traces + photos)
        python3 build.py [--only A2.14,A3.03] [--book /path/Volume2EN.pdf] [--out ../../instruments_v2]

For every instrument:
  cnc/<part>.svg  - 1:1 vector, mm, one layer per machining operation
  cnc/<part>.dxf  - same geometry, true ARC/CIRCLE entities
  <slug>_workshop.pdf - hand-drawn sheets: overview + every part at 1:1
  <slug>_overview.jpg - hand-drawn overview sheet
  README.md       - data from the book, parts list, computed tables, assumptions
"""
import os, sys, io, math, random, argparse, base64, subprocess, json, shutil
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import Drawing, write_svg_cnc, write_dxf, hand_paths, LAYERS, dms, transform_item
from catalog import INSTRUMENTS
from instruments import build

INK = {'CUT_OUTER': '#5b2410', 'CUT_INNER': '#6e2c16', 'ENGRAVE': '#2a1a0c', 'ENGRAVE_FINE': '#4d3a26',
       'TEXT': '#1f160b', 'BEND': '#8a5a20', 'GUIDE': '#7a8a6a'}
MAT_AR = {'brass': 'نحاس أصفر', 'brass (turned)': 'نحاس أصفر (خراطة)', 'hard wood': 'خشب صلد', 'view': 'منظر',
          'engraving template': 'قالب حفر', 'brass sheet': 'صاج نحاس', 'wood + paper': 'خشب وورق',
          'hard wood + brass strip': 'خشب صلد + شريط نحاس'}

_PAPER = None


def paper_b64():
    global _PAPER
    if _PAPER is None:
        from PIL import Image, ImageFilter
        rng = np.random.default_rng(7)
        h, w = 424, 600
        base = np.zeros((h, w, 3))
        base[:] = (238, 226, 197)
        low = rng.normal(0, 1, (h // 8 + 1, w // 8 + 1))
        low = np.array(Image.fromarray(((low - low.min()) / (np.ptp(low)) * 255).astype('uint8')).resize((w, h), Image.BICUBIC)) / 255.0
        fine = rng.normal(0, 1, (h, w))
        img = base + (low[..., None] - 0.5) * 18 + fine[..., None] * 3.5
        yy, xx = np.mgrid[0:h, 0:w]
        vig = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
        img -= vig[..., None] * np.array([16, 20, 26])
        im = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
        bio = io.BytesIO()
        im.save(bio, 'JPEG', quality=72)
        _PAPER = base64.b64encode(bio.getvalue()).decode()
    return _PAPER


STYLE = {'CUT_OUTER': ('#a00000', 0.35), 'CUT_INNER': ('#a00000', 0.28), 'ENGRAVE': ('#000000', 0.18),
         'ENGRAVE_FINE': ('#3a3a3a', 0.09), 'BEND': ('#c06000', 0.2), 'GUIDE': ('#60a060', 0.1), 'TEXT': ('#000000', 0)}


def f3(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.')


def exact_svg(sheet, W, H, images=()):
    """Exact technical rendering of a sheet Drawing (mm, y up): circles and
    arcs are written as SVG circles/arcs, nothing is sampled or wobbled."""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{f3(W)}mm" height="{f3(H)}mm" viewBox="0 {f3(-H)} {f3(W)} {f3(H)}">',
           f'<rect x="0" y="{f3(-H)}" width="{f3(W)}" height="{f3(H)}" fill="#ffffff"/>']
    for (x, y, w, h, b64, op) in images:
        out.append(f'<image x="{f3(x)}" y="{f3(-y - h)}" width="{f3(w)}" height="{f3(h)}" opacity="{op}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{b64}"/>')
    def P(p):
        return f'{f3(p[0])},{f3(-p[1])}'
    fills = []
    for lay, (col, sw) in STYLE.items():
        its = [i for i in sheet.items if i['layer'] == lay]
        if not its:
            continue
        dash = ' stroke-dasharray="1.5,1"' if lay in ('BEND', 'GUIDE') else ''
        out.append(f'<g fill="none" stroke="{col}" stroke-linecap="round" stroke-linejoin="round"{dash}>')
        for it in its:
            w = sw * (it['w'] / 1.0 if it.get('w') else 1.0)
            if it['t'] == 'circle':
                out.append(f'<circle cx="{f3(it["c"][0])}" cy="{f3(-it["c"][1])}" r="{f3(it["r"])}" stroke-width="{f3(w)}"/>')
            elif it['t'] == 'arc':
                from core import polar as _pl
                p0 = _pl(it['r'], it['a0'], it['c']); p1 = _pl(it['r'], it['a1'], it['c'])
                large = 1 if it['a1'] - it['a0'] > 180 else 0
                out.append(f'<path d="M{P(p0)} A{f3(it["r"])},{f3(it["r"])} 0 {large} 0 {P(p1)}" stroke-width="{f3(w)}"/>')
            elif it.get('fill'):
                fills.append('M' + ' L'.join(P(p) for p in it['p']) + 'Z')
            else:
                out.append(f'<path d="M' + ' L'.join(P(p) for p in it['p']) + ('Z' if it.get('closed') else '') + f'" stroke-width="{f3(w)}"/>')
        out.append('</g>')
    if fills:
        out.append('<path fill="#000000" fill-rule="evenodd" d="' + ' '.join(fills) + '"/>')
    out.append('</svg>')
    return '\n'.join(out)


def hand_svg(sheet, W, H, seed=1, amp=0.0, texture=False, images=()):
    return exact_svg(sheet, W, H, images)


def frame(sheet, W, H, title, subtitle):
    m = 8
    sheet.poly([(m, m), (W - m, m), (W - m, H - m), (m, H - m)], True, 'ENGRAVE', w=2.2)
    sheet.poly([(m + 2.5, m + 2.5), (W - m - 2.5, m + 2.5), (W - m - 2.5, H - m - 2.5), (m + 2.5, H - m - 2.5)], True, 'ENGRAVE', w=0.9)
    sheet.text(title, (W / 2, H - m - 14), 9 if W > 400 else 6.5, bold=True)
    if subtitle:
        sheet.text(subtitle, (W / 2, H - m - 24 if W > 400 else H - m - 24), 4.6 if W > 400 else 3.6)


def place(sheet, d, cx, cy, maxw, maxh, max_scale=1.0):
    x0, y0, x1, y1 = d.bbox()
    w, h = max(x1 - x0, 1e-3), max(y1 - y0, 1e-3)
    s = min(maxw / w, maxh / h, max_scale)
    ox = cx - (x0 + x1) / 2 * s
    oy = cy - (y0 + y1) / 2 * s
    for it in d.items:
        if it['layer'] == 'GUIDE':
            continue
        sheet.items.append(transform_item(it, ox, oy, 0, s))
    return s


def scale_label(s):
    if abs(s - 1) < 1e-6:
        return 'مقياس ١:١'
    if s < 1:
        return 'مقياس ١:%s' % fmt_ar(1 / s)
    return 'مقياس %s:١' % fmt_ar(s)


def fmt_ar(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return s.translate(str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫'))


def overview_sheet(spec, parts, views):
    W, H = 594.0, 420.0
    sheet = Drawing()
    frame(sheet, W, H, spec['title_ar'], '%s — Sezgin, Science and Technology in Islam II, p. %d — Inv. %s' % (spec['title_en'], spec['page'], spec['id']))
    top = H - 46
    # views on the left
    vcount = max(1, len(views))
    vw = 270 if vcount >= 2 else 300
    vh = (top - 24) / min(vcount, 2) - 12
    for i, (nm, d) in enumerate(views[:2]):
        cx = 20 + vw / 2
        cy = top - (i + 0.5) * (vh + 12)
        s = place(sheet, d, cx, cy, vw - 10, vh - 6)
        lab = {'front': 'الوجه - مجمّع', 'back': 'الظهر - مجمّع'}.get(nm, nm)
        sheet.text(lab + ' (' + scale_label(s) + ')', (cx, cy - vh / 2 - 2), 4)
    # parts grid on the right
    pp = [p for p in parts if p[5] and p[5] > 0 or p[0] in ('mater_back',)]
    x0, x1 = 20 + vw + 10, W - 20
    n = len(pp)
    cols = max(2, int(math.ceil(math.sqrt(n * 1.15))))
    rows = int(math.ceil(n / cols))
    cw = (x1 - x0) / cols
    ch = (top - 30) / max(rows, 1)
    for k, (key, name, d, mat, t, q) in enumerate(pp):
        r, c = divmod(k, cols)
        cx = x1 - (c + 0.5) * cw
        cy = top - (r + 0.5) * ch + 4
        s = place(sheet, d, cx, cy, cw - 8, ch - 16)
        short = name.split(' - ')[0].split(' (')[0]
        sheet.text('%d) %s' % (k + 1, short), (cx, cy - (ch - 16) / 2 - 3.5), 3.2)
        sheet.text(scale_label(s) + ('   ×%d' % q if q and q > 1 else ''), (cx, cy - (ch - 16) / 2 - 8), 2.4)
    sheet.text('المقاسات الدقيقة في ملفات CNC (DXF/SVG) وفي صفحات ١:١ من ملف PDF', (W / 2, 16), 3.4)
    return sheet, W, H


def part_page(spec, idx, key, name, d, mat, t, q):
    x0, y0, x1, y1 = d.bbox()
    w, h = x1 - x0, y1 - y0
    margin = 22
    W = max(210.0, w + 2 * margin)
    H = max(297.0, h + 2 * margin + 70)
    if W > H and w > h:
        W, H = max(297.0, w + 2 * margin), max(210.0, h + 2 * margin + 70)
    sheet = Drawing()
    frame(sheet, W, H, spec['title_ar'], '%d) %s' % (idx, name))
    cx, cy = W / 2, (H - 46 + 58) / 2
    place(sheet, d, cx, cy, W - 2 * margin, H - 46 - 58, 1.0)
    # dimension: overall width
    yy = cy - h / 2 - 8
    sheet.line((cx - w / 2, yy), (cx + w / 2, yy), 'ENGRAVE_FINE')
    for xx in (cx - w / 2, cx + w / 2):
        sheet.line((xx, yy - 2), (xx, yy + 2), 'ENGRAVE_FINE')
    sheet.text('%s مم' % fmt_ar(round(w, 1)), (cx, yy - 4), 3.2)
    xx = cx + w / 2 + 8
    if xx < W - 12:
        sheet.line((xx, cy - h / 2), (xx, cy + h / 2), 'ENGRAVE_FINE')
        sheet.text('%s مم' % fmt_ar(round(h, 1)), (xx + 4, cy), 3.2, 90)
    # title block
    holes = sorted({round(it['r'] * 2, 2) for it in d.items if it['t'] == 'circle' and it['layer'] == 'CUT_INNER' and it['r'] < 15})
    lines = ['المادة: %s' % MAT_AR.get(mat, mat),
             'السُّمك: %s مم' % fmt_ar(t) if t else 'السُّمك: — (وجه آخر لنفس القطعة)' if q == 0 else 'السُّمك: —',
             'العدد: %s' % fmt_ar(q) if q else '',
             'أقطار الثقوب: ' + '، '.join(fmt_ar(v) for v in holes[:6]) + ' مم' if holes else '',
             'الرسم بمقياس ١:١ — قِس قبل القص؛ الملف الدقيق: cnc/%s.dxf' % key]
    yb = 30
    for i, L in enumerate([l for l in lines if l]):
        sheet.text(L, (W - 20, yb + 30 - i * 6.5), 3.3, anchor='end')
    return sheet, W, H


def svg_to_pdf_bytes(svg):
    import cairosvg
    return cairosvg.svg2pdf(bytestring=svg.encode('utf-8'))


def readme(spec, parts, extra, files, ref_files):
    L = []
    L.append(f"# {spec['title_ar']}\n")
    L.append(f"**{spec['title_en']}** — رقم الجرد في متحف المعهد: `{spec['id']}` — الكتاب: فؤاد سزكين، *العلوم والتقنية في الإسلام* ج٢، صفحة **{spec['page']}**.\n")
    L.append('## بيانات النموذج كما في الكتاب\n')
    L.append('> ' + spec['model'] + '\n')
    L.append('## الملفات\n')
    L.append(f"- `{files['pdf']}` — **ملف الحِرفي**: لوحة عامة مرسومة بأسلوب الرسم اليدوي، ثم كل قطعة على صفحة مستقلة بمقياس ١:١ للطباعة والنقل على النحاس.")
    L.append(f"- `{files['jpg']}` — اللوحة العامة كصورة.")
    L.append('- `cnc/` — لكل قطعة ملف `DXF` وملف `SVG` بالمليمتر ومقياس ١:١ لآلة CNC / الليزر / الحفر:')
    L.append('  - `CUT_OUTER` قص المحيط الخارجي، `CUT_INNER` قص الفتحات والتفريغ والثقوب')
    L.append('  - `ENGRAVE` حفر الخطوط الأساسية، `ENGRAVE_FINE` حفر الخطوط الثانوية، `TEXT` حفر الكتابة (محيطات حروف مغلقة)')
    L.append('  - `BEND` خط ثني، `GUIDE` خط مساعد لا يُحفر')
    if files.get('groups'):
        L.append('- `cnc/<قطعة>__CUT_ONLY.dxf/svg` — **خط القص فقط** للقطع ذات الوجهين: يُقص مرة واحدة، ثم يُحفر الوجه الأول بملفه، وتُقلب القطعة ويُحفر الوجه الثاني بملفه. خط القص في ملفَي الوجهين **متطابق تماماً**:')
        for parent, faces in files['groups']:
            L.append('  - `' + parent + '` ← ' + '، '.join('`%s`' % f for f in faces))
    if files.get('overlay'):
        L.append('- `cnc/photo_overlay_front.svg` و`photo_overlay_back.svg` — صورة الكتاب مصححة المنظور وبمقاس النموذج تحت خطوط الرسم، لمطابقة الزخارف أو تتبع تفاصيل إضافية في Inkscape. وفي آخر ملف PDF صفحتا مطابقة.')
    if 'csv' in extra:
        L.append('- `cnc/sphere_engraving.csv` — نقاط خطوط الكرة (x,y,z بالمليمتر + الميل وزاوية الساعة) لآلة حفر ذات محور رابع/خامس.')
    if ref_files:
        L.append('- `reference/` — صفحات الكتاب المرجعية للمقارنة الشكلية والزخرفية.')
    L.append('')
    L.append('## قائمة القطع\n')
    L.append('| # | القطعة | المادة | السمك (مم) | العدد | الأبعاد الكلية (مم) | الملف |')
    L.append('|---|---|---|---|---|---|---|')
    for i, (key, name, d, mat, t, q) in enumerate(parts, 1):
        x0, y0, x1, y1 = d.bbox()
        L.append(f"| {i} | {name} | {MAT_AR.get(mat, mat)} | {t if t else '—'} | {q if q else 'وجه'} | {x1-x0:.1f} × {y1-y0:.1f} | `cnc/{key}.dxf` |")
    L.append('')
    dm = extra.get('dims')
    if dm is not None:
        P = dm.proj
        L.append('## القيم المحسوبة للإسقاط\n')
        L.append('| البند | القيمة |')
        L.append('|---|---|')
        L.append(f'| القطر الخارجي للأم | {dm.D:.1f} مم |')
        L.append(f'| عرض الحجرة (الحافة) | {dm.limb_w:.2f} مم |')
        L.append(f'| قطر مقعد الصفائح | {2*dm.Rp:.2f} مم |')
        L.append(f'| الميل الكلي المستعمل | {dms(dm.eps)} |')
        L.append(f'| نصف قطر مدار الجدي | {P.R_cap:.3f} مم |')
        L.append(f'| نصف قطر معدل النهار | {P.R_eq:.3f} مم |')
        L.append(f'| نصف قطر مدار السرطان | {P.R_can:.3f} مم |')
        L.append(f'| قطر القطب (المحور) | {dm.pin_d:.2f} مم |')
        L.append('')
        L.append('الإسقاط: إسقاط مجسَّم (ستيريوغرافي) من القطب الجنوبي على مستوى معدل النهار؛ نصف قطر دائرة الميل δ = نق_المعدل × ظا((٩٠−δ)/٢). '
                 'كل مقنطرة وسمت وخط ساعة زمانية حُسب كدائرة حقيقية (مركز ونصف قطر) ثم قُصّ عند حدوده بدقة ١٠⁻⁷ درجة.\n')
    stars = extra.get('stars') or []
    if stars:
        L.append('## الكواكب على العنكبوت (محسوبة لسنة الصنع)\n')
        L.append('| الكوكب | المطلع المستقيم | الميل |')
        L.append('|---|---|---|')
        for nm, ra, de in stars:
            L.append(f'| {nm} | {ra:.2f}° | {de:+.2f}° |')
        L.append('')
        L.append('مواضع الكواكب: من فهرس حديث (J2000) مع تقديم الاعتدالين إلى سنة الصنع (٥٠٫٢٩ ثانية/سنة في الطول) وبالميل الكلي المستعمل في الآلة.\n')
    if extra.get('stars_ecl'):
        L.append('## مؤشرات الكواكب على عنكبوت الكرة\n')
        L.append('| الكوكب | الطول في البروج | العرض |')
        L.append('|---|---|---|')
        for nm, lam, beta in extra['stars_ecl']:
            L.append(f'| {nm} | {lam:.2f}° | {beta:+.2f}° |')
        L.append('')
    if spec.get('assume'):
        L.append('## افتراضات (قيم لم يذكرها الكتاب)\n')
        for a in spec['assume']:
            L.append('- ' + a)
        L.append('')
    L.append('## ملاحظات التنفيذ\n')
    L.append('- الملفات بمقياس ١:١ بالمليمتر. إذا رغبت بقطر مختلف كبّر الملف كله بنسبة واحدة (كل الخطوط محسوبة نسبياً).')
    L.append('- الحفر على الظهر (`*_back`) يُنفذ على الوجه الآخر من نفس القطعة: اقلب القطعة حول المحور الرأسي وطابق ثقب المركز.')
    L.append('- الكرسي (العروة المزخرفة) منقول بالتتبع الآلي من صورة الكتاب (تصحيح المنظور، فصل المعدن عن الخلفية، تناظر حول المحور) ومكبر إلى قطر النموذج؛ إن لم تتوفر صورة استُعمل التصميم الهندسي.')
    L.append('- العنكبوت: حسابي (مواضع الكواكب دقيقة) إلا عنكبوت حماة A2.17 المنقول من الصورة. تفاصيل زخرف العنكبوت الأصلي ظاهرة في صفحة المطابقة في PDF وفي `photo_overlay_front.svg` لمن أراد تتبعها.')
    L.append('- الرسومات دقيقة: دوائر وأقواس حقيقية بلا تعرج.')
    return '\n'.join(L) + '\n'


def extract_reference(book, page, outdir):
    if not book or not os.path.exists(book):
        return []
    os.makedirs(outdir, exist_ok=True)
    pdfp = page + 6
    files = []
    for p in (pdfp,):
        base = os.path.join(outdir, f'book_page_{page}')
        subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', '90', '-jpeg', '-jpegopt', 'quality=78', '-singlefile', book, base], check=True)
        files.append(base + '.jpg')
    return files


PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache', 'rectified')
NOT_PIECES = ('view', 'engraving template')


def unify_faces(parts):
    """Both faces of a piece get exactly the same cut geometry: the cut layers
    of the first face are copied into every following face file (qty 0).
    Returns list of (parent_key, [face keys])."""
    groups = []
    parent = None
    for k, (key, name, d, mat, t, q) in enumerate(parts):
        if q and q > 0 and mat not in NOT_PIECES:
            parent = (key, d)
            groups.append([key, [key]])
        elif q == 0 and parent is not None and mat not in NOT_PIECES:
            pd = parent[1]
            d.items = [it for it in d.items if it['layer'] not in ('CUT_OUTER', 'CUT_INNER')]
            d.items = [dict(it) for it in pd.items if it['layer'] in ('CUT_OUTER', 'CUT_INNER')] + d.items
            groups[-1][1].append(key)
    return [(g[0], g[1]) for g in groups if len(g[1]) > 1]


def cut_only(d):
    o = Drawing(title=d.title)
    o.items = [dict(it) for it in d.items if it['layer'] in ('CUT_OUTER', 'CUT_INNER')]
    return o


def photo_meta(spec, side, maxpx=900):
    p = os.path.join(PHOTO_DIR, 'meta.json')
    if not os.path.exists(p):
        return None
    m = json.load(open(p)).get(f"{spec['id']}_{side}")
    if not m:
        return None
    from PIL import Image
    im = Image.open(os.path.join(PHOTO_DIR, m['file'])).convert('RGB')
    k = min(1.0, float(maxpx) / max(im.size))
    im = im.resize((int(im.size[0] * k), int(im.size[1] * k)))
    bio = io.BytesIO()
    im.save(bio, 'JPEG', quality=78)
    m = dict(m)
    m['scale_px'] = k
    m['b64'] = base64.b64encode(bio.getvalue()).decode()
    return m


def photo_rect_mm(m, D, cx_mm, cy_mm, scale=1.0):
    """placement of the rectified photo so that its mater rim = diameter D."""
    s = (D / 2) / m['r'] * scale
    x = cx_mm - m['cx'] * s
    ytop = cy_mm + m['cy'] * s
    return (x, ytop - m['h'] * s, m['w'] * s, m['h'] * s)


def overlay_page(spec, title, d, m, D):
    """1:1 page: book photograph (rectified, scaled to the model) under the
    cut outline of our drawing – to check and to trace the decoration."""
    x0, y0, x1, y1 = d.bbox()
    s = (D / 2) / m['r']
    W = max(297.0, m['w'] * s + 40, x1 - x0 + 40)
    H = max(210.0, m['h'] * s + 80, y1 - y0 + 80)
    sheet = Drawing()
    frame(sheet, W, H, spec['title_ar'], title)
    cx, cy = W / 2, (H - 40) / 2 + 6
    for it in d.items:
        if it['layer'] in ('CUT_OUTER', 'CUT_INNER'):
            sheet.items.append(transform_item(it, cx, cy, 0, 1.0))
    x, y, w, h = photo_rect_mm(m, D, cx, cy)
    sheet.text('صورة الكتاب مصححة المنظور ومكبرة إلى مقاس النموذج — الخط الأحمر: خط القص في ملفات CNC', (W / 2, 14), 3.4)
    return sheet, W, H, [(x, y, w, h, m['b64'], 0.85)]


def overlay_svg_file(path, d, m, D):
    x0, y0, x1, y1 = d.bbox()
    s = (D / 2) / m['r']
    W = max(x1 - x0, m['w'] * s) + 20
    H = max(y1 - y0, m['h'] * s) + 20
    cx, cy = W / 2, H / 2
    sheet = Drawing()
    for it in d.items:
        if it['layer'] != 'GUIDE':
            sheet.items.append(transform_item(it, cx, cy, 0, 1.0))
    x, y, w, h = photo_rect_mm(m, D, cx, cy)
    svg = exact_svg(sheet, W, H, [(x, y, w, h, m['b64'], 0.9)])
    with open(path, 'w') as f:
        f.write(svg)


def run(spec, outroot, book):
    parts, views, extra = build(spec)
    num = INSTRUMENTS.index(spec) + 1
    folder = f"{num:02d}_{spec['id'].replace('.', '_')}_{spec['slug']}"
    out = os.path.join(outroot, folder)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'cnc'))
    groups = unify_faces(parts)
    for key, name, d, mat, t, q in parts:
        d.title = f"{spec['title_en']} — {key}"
        write_svg_cnc(d, os.path.join(out, 'cnc', key + '.svg'))
        write_dxf(d, os.path.join(out, 'cnc', key + '.dxf'))
    pd_ = {p[0]: p[2] for p in parts}
    for parent, faces in groups:
        c = cut_only(pd_[parent])
        write_svg_cnc(c, os.path.join(out, 'cnc', parent + '__CUT_ONLY.svg'))
        write_dxf(c, os.path.join(out, 'cnc', parent + '__CUT_ONLY.dxf'))
    if 'csv' in extra:
        with open(os.path.join(out, 'cnc', 'sphere_engraving.csv'), 'w') as f:
            f.write(extra['csv'])
    from pypdf import PdfWriter, PdfReader
    import cairosvg
    D = spec.get('D')
    mf = photo_meta(spec, 'front') if D else None
    mb = photo_meta(spec, 'back') if D else None
    sheet, W, H = overview_sheet(spec, parts, views)
    imgs = []
    mthumb = photo_meta(spec, 'front', 320) if mf else None
    if mthumb:
        mf_t = mthumb
        # small book photograph in the lower left corner for comparison
        sz = 70
        s = sz / max(mf_t['w'], mf_t['h'])
        imgs.append((14, 22, mf_t['w'] * s, mf_t['h'] * s, mf_t['b64'], 1.0))
        sheet.text('صورة الكتاب', (14 + mf_t['w'] * s / 2, 18), 3)
    from PIL import Image
    svg = exact_svg(sheet, W, H, imgs)
    jpg = f"{spec['slug']}_overview.jpg"
    png_bytes = cairosvg.svg2png(bytestring=svg.encode(), output_width=3000)
    from PIL import Image
    Image.open(io.BytesIO(png_bytes)).convert('RGB').save(os.path.join(out, jpg), 'JPEG', quality=86)
    writer = PdfWriter()
    def add(svgtxt):
        for pg in PdfReader(io.BytesIO(svg_to_pdf_bytes(svgtxt))).pages:
            writer.add_page(pg)
    add(svg)
    face_of = {}
    for parent, faces in groups:
        for f_ in faces[1:]:
            face_of[f_] = parent
    for i, (key, name, d, mat, t, q) in enumerate(parts, 1):
        nm = name
        if key in face_of:
            nm = name + ' — القص مطابق تماماً للوجه الأول (%s)' % face_of[key]
        sh, w_, h_ = part_page(spec, i, key, nm, d, mat, t, q)
        add(exact_svg(sh, w_, h_))
    # overlay pages with the book photographs
    if mf or mb:
        front_d = next((v for n, v in views if n == 'front'), None)
        back_d = next((v for n, v in views if n == 'back'), None)
        for m, d, side, lab in ((mf, front_d, 'front', 'مطابقة الوجه مع صورة الكتاب'), (mb, back_d, 'back', 'مطابقة الظهر مع صورة الكتاب')):
            if m and d is not None:
                sh, w_, h_, im = overlay_page(spec, lab, d, m, D)
                png = cairosvg.svg2png(bytestring=exact_svg(sh, w_, h_, im).encode(), output_width=int(w_ / 25.4 * 150))
                bio = io.BytesIO()
                Image.open(io.BytesIO(png)).convert('RGB').save(bio, 'PDF', resolution=150, quality=80)
                for pg in PdfReader(io.BytesIO(bio.getvalue())).pages:
                    writer.add_page(pg)
                overlay_svg_file(os.path.join(out, 'cnc', f'photo_overlay_{side}.svg'), d, m, D)
    pdfname = f"{spec['slug']}_workshop.pdf"
    with open(os.path.join(out, pdfname), 'wb') as f:
        writer.write(f)
    refs = extract_reference(book, spec['page'], os.path.join(out, 'reference'))
    with open(os.path.join(out, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme(spec, parts, extra, {'pdf': pdfname, 'jpg': jpg, 'groups': groups, 'overlay': bool(mf or mb)}, refs))
    return folder, parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--book', default='')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'instruments_v2'))
    a = ap.parse_args()
    only = set(x for x in a.only.split(',') if x)
    os.makedirs(a.out, exist_ok=True)
    index = []
    for spec in INSTRUMENTS:
        if only and spec['id'] not in only:
            continue
        print('building', spec['id'], spec['slug'], flush=True)
        folder, parts = run(spec, a.out, a.book)
        index.append((spec, folder, len([p for p in parts if p[5]])))
    allidx = []
    for i, s in enumerate(INSTRUMENTS):
        fo = f"{i+1:02d}_{s['id'].replace('.', '_')}_{s['slug']}"
        if os.path.isdir(os.path.join(a.out, fo)):
            n = len([x for x in os.listdir(os.path.join(a.out, fo, 'cnc')) if x.endswith('.dxf') and '__CUT_ONLY' not in x])
            allidx.append({'id': s['id'], 'page': s['page'], 'title_ar': s['title_ar'], 'title_en': s['title_en'], 'folder': fo, 'parts': n})
    with open(os.path.join(a.out, 'index.json'), 'w') as f:
        json.dump(allidx, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
