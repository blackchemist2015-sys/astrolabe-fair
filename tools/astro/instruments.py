"""Assembly of each instrument from its parts + the catalogue of all the
instruments of pages 79-150 of the book (Sezgin, Science and Technology in
Islam, vol. II)."""
import math
from core import Drawing, dms, transform_item
from astrolabe import (Dims, make_plate, make_horizons_plate, make_rete, make_grid_rete, make_back, make_limb_ring,
                       make_mater_inside, make_alidade, make_rule, make_pin_wedge, make_shackle_ring,
                       make_saphea_rule, draw_saphea, clamp)
from others import (build_sine_quadrant, build_shakkaziya, build_meteoroscope, build_saphea, build_dastur,
                    build_quadrant_disc, build_indian_circle, build_meridian_instrument, build_triangle,
                    build_altitude_table, build_spherical, build_linear)
from shapely.geometry import box, Point
from shapely.ops import unary_union


def fade(d):
    """copy of a drawing with engraving demoted to fine lines (for assembly views)."""
    o = Drawing()
    for it in d.items:
        it = dict(it)
        if it['layer'] in ('ENGRAVE', 'TEXT'):
            it['layer'] = 'ENGRAVE_FINE'
        if it['layer'] == 'TEXT':
            continue
        o.items.append(it)
    return o


def build_astrolabe(spec):
    dm = Dims(spec)
    if spec.get('rete_d'):
        # rete diameter given by the book = Capricorn circle of the model
        from geom import PolarProj
        dm.R_cap = min(spec['rete_d'] / 2, dm.R_cap)
        dm.proj = PolarProj(dm.R_cap, dm.eps)
    parts, views = [], []
    inside = make_mater_inside(dm, spec)
    back = make_back(dm, spec)
    limb = make_limb_ring(dm, spec)
    parts.append(('mater_inside', 'الأم (الجسم) - الوجه الداخلي' + (' (عليه نقش)' if spec.get('mater_inside') else ''), inside, 'brass', dm.t_mater, 1))
    parts.append(('mater_back', 'الأم - الظهر (نفس القطعة، يُحفر على الوجه الآخر)', back, 'brass', None, 0))
    parts.append(('limb_ring', 'الحجرة (الحافة المرتفعة) مع وجه الكرسي - تُلحم على الأم', limb, 'brass', dm.t_limb, 1))
    n_pl = 0
    first_plate = None
    for i, pl in enumerate(spec.get('plates', [])):
        n_pl += 1
        faces = []
        if pl[0] == 'horizons':
            faces = [('a', make_horizons_plate(dm, spec), 'صفيحة الآفاق')]
        elif pl[0] == 'fold':
            faces = [('a', make_plate(dm, spec, pl[1], phi2=pl[2]), 'وجه مطوي لعرضين %s / %s' % (dms(pl[1]), dms(pl[2])))]
            if len(pl) > 3:
                faces.append(('b', make_plate(dm, spec, pl[3], phi2=pl[4]), 'وجه مطوي لعرضين %s / %s' % (dms(pl[3]), dms(pl[4]))))
        else:
            faces.append(('a', make_plate(dm, spec, pl[0]), 'لعرض %s' % dms(pl[0])))
            if len(pl) > 1 and pl[1] is not None:
                faces.append(('b', make_plate(dm, spec, pl[1]), 'لعرض %s' % dms(pl[1])))
        for j, (side, d, lab) in enumerate(faces):
            parts.append((f'plate{i+1}{side}', f'الصفيحة {i+1} - الوجه {"الأول" if side == "a" else "الثاني"} ({lab})', d,
                          'brass', dm.t_plate if j == 0 else None, 1 if j == 0 else 0))
            if first_plate is None:
                first_plate = d
    rete = None
    if spec.get('rete', True):
        if spec.get('grid_rete'):
            rete = make_grid_rete(dm, spec)
        else:
            rete = make_rete(dm, spec)
        if spec.get('rete_hours'):
            # hour scale engraved on the rete rim (European instruments without room on the limb)
            for h in range(24):
                a = 90 - 15 * h
                rete.line((0, 0), (0, 0), 'GUIDE')
        parts.append(('rete', 'العنكبوت (الشبكة) - %d كوكباً' % len(rete.star_table), rete, 'brass', dm.t_rete, 1))
    rule = None
    if spec.get('rule'):
        rule = make_rule(dm, spec, spec['rule'])
        parts.append(('rule', 'المسطرة الأمامية بمقياس الميول (نصف قطر %d مم)' % spec['rule'], rule, 'brass', clamp(dm.t_rete, 1, 3), 1))
    alid = None
    if spec.get('alidade', True):
        alid = make_alidade(dm, spec, spec.get('alidade_len'), right_angle_pointer=spec.get('alidade_pointer', False))
        parts.append(('alidade', 'العضادة ذات الهدفتين (طول %d مم)' % round(alid.L), alid, 'brass', dm.t_alid, 1))
        parts.append(('sights', 'هدفتا العضادة (تُثنيان على خط الثني)', alid.vanes, 'brass', clamp(dm.t_alid * 0.6, 0.8, 3), 2))
    if spec.get('back_bar'):
        bar = make_saphea_rule(dm.R - clamp(0.075 * dm.R, 3, 20), spec, 2 * dm.R - 4)
        parts.append(('back_bar', 'المسطرة الأفقية على الظهر (مسقط الزرقالي) مع خط الشفق', bar, 'brass', 2, 1))
        cur = Drawing(title='cursor')
        cw = clamp(0.1 * dm.R, 6, 20)
        cur.poly([(-cw / 2, -cw), (cw / 2, -cw), (cw / 2, cw), (-cw / 2, cw)], True, 'CUT_OUTER')
        cur.poly([(-cw / 2 + 1.5, -cw * 0.3), (cw / 2 - 1.5, -cw * 0.3), (cw / 2 - 1.5, cw * 0.3), (-cw / 2 + 1.5, cw * 0.3)], True, 'CUT_INNER')
        cur.line((0, -cw), (0, cw), 'ENGRAVE')
        parts.append(('cursor', 'المؤشر المنزلق (cursor)', cur, 'brass', 1.5, 1))
        br = Drawing(title='brachiolus')
        L1 = dm.R * 0.55
        br.shape(unary_union([box(0, -2.5, L1, 2.5), Point(0, 0).buffer(4), Point(L1, 0).buffer(4)]))
        br.hole((0, 0), 2.1); br.hole((L1, 0), 2.1)
        parts.append(('brachiolus', 'ذراع البراكيولوس (مفصلي) ×٢', br, 'brass', 1.5, 2))
    stack = dm.t_mater + n_pl * dm.t_plate + (dm.t_rete if rete else 0) + (dm.t_alid if alid else 0) + (dm.t_rete if rule else 0) + 0.5
    pin, wedge = make_pin_wedge(dm, spec, stack)
    parts.append(('pin', 'القطب (المحور) - منظر جانبي لقطعة مخروطة، قطر %.1f مم وطول %.1f مم' % (dm.pin_d, pin.L), pin, 'brass (turned)', None, 1))
    parts.append(('wedge', 'الفرس (الإسفين)', wedge, 'brass', round(wedge.thick, 2), 1))
    sh, ring = make_shackle_ring(dm, spec)
    parts.append(('shackle', 'العروة (الحمّالة) - تُثنى على خطي الثني', sh, 'brass', clamp(0.012 * dm.D, 1, 4), 1))
    parts.append(('ring', 'الحلقة', ring, 'brass', clamp(0.025 * dm.D, 1.5, 6), 1))
    # assembly views
    front = Drawing(title='front assembly')
    front.merge(fade(limb))
    if first_plate is not None:
        front.merge(fade(first_plate))
    elif spec.get('mater_inside'):
        front.merge(fade(inside))
    if rete is not None:
        front.merge(rete)
    if rule is not None:
        front.merge(rule, ang=-35)
    backv = Drawing(title='back assembly')
    backv.merge(back)
    if alid is not None:
        for it in alid.items:
            if it['layer'] != 'GUIDE':
                backv.items.append(transform_item(it, 0, 0, 35, 1))
    views += [('front', front), ('back', backv)]
    extra = {'dims': dm, 'stars': rete.star_table if rete is not None else []}
    return parts, views, extra


BUILDERS = {
    'astrolabe': build_astrolabe, 'sine_quadrant': build_sine_quadrant, 'shakkaziya': build_shakkaziya,
    'meteoroscope': build_meteoroscope, 'saphea': build_saphea, 'dastur': build_dastur,
    'quadrant_disc': build_quadrant_disc, 'indian': build_indian_circle, 'meridian': build_meridian_instrument,
    'triangle': build_triangle, 'alt_table': build_altitude_table, 'spherical': build_spherical, 'linear': build_linear,
}


def build(spec):
    r = BUILDERS[spec['builder']](spec)
    if len(r) == 2:
        return r[0], r[1], {}
    return r
