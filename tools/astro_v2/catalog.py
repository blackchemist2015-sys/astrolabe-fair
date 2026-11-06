"""Catalogue of the instruments shown on pages 79-150 of
F. Sezgin, Science and Technology in Islam, vol. II (Frankfurt 2010).
`model` repeats the data of the book ("Our model: ...");
`assume` lists every value that the book does not give and that had to be
chosen (always stated in the README of the instrument)."""
from cities import CITIES_ISLAMIC, CITIES_IRAN

CLIM3, CLIM4, CLIM5, CLIM6, CLIM7 = 30 + 22 / 60, 36.0, 40 + 56 / 60, 45 + 1 / 60, 48 + 32 / 60

I = []


def add(**k):
    I.append(k)


# ------------------------------------------------------------------ astrolabes
add(id='A2.25', page=86, builder='astrolabe', slug='nastulus_kuwait',
    title_ar='أسطرلاب نسطولس (٣١٥هـ/٩٢٧م)', title_en='Astrolabe of Nastulus (315/927)',
    model='Brass, etched. Mater with bracket and suspension ring with a diameter of 170 mm. One disc.',
    D=170, year=927, plates=[(33, 36)], stars=17, back=['alt', 'shadow'],
    assume=['عرضا الصفيحة ٣٣° (بغداد) و٣٦° مأخوذان من وصف الأصل في الكتاب (الأصل قطره ١٧٣ مم وسمكه ٤ مم).',
            'عدد الكواكب ١٧ كما في الأصل.', 'تصميم الظهر (مقياس الارتفاع ومربعا الظل) غير مذكور في الكتاب.'])

add(id='A2.26', page=87, builder='astrolabe', slug='nastulus_cairo_mater',
    title_ar='الأسطرلاب الثاني لنسطولس (الأم فقط)', title_en='The second astrolabe of Nastulus (mater only)',
    model='Brass, etched. Mater with a diameter of 130 mm. Without rete, alidade or disc.',
    D=130, year=930, plates=[], rete=False, alidade=False, back=['alt'],
    mater_inside={'gazetteer': CITIES_ISLAMIC[:64], 'lat_only': True},
    assume=['في الأصل أسماء ٦٤ مدينة مع عروضها على باطن الأم؛ الكتاب لا يذكر القائمة، فوضعنا ٦٤ مدينة إسلامية بعروضها الحديثة المحسوبة (يُستبدل بنص الأصل إن توفر).'])

add(id='A2.27', page=88, builder='astrolabe', slug='hamid_al_wasiti',
    title_ar='أسطرلاب حامد بن علي الواسطي', title_en='The astrolabe of Hamid b. Ali al-Wasiti',
    model='Brass, etched. Mater with bracket and suspension ring with a diameter of 111 mm. One disc.',
    D=111, year=950, plates=[(32 + 10 / 60, 33 + 20 / 60)], stars=12, back=['alt', 'zodiac_quads'],
    assume=['عرضا الصفيحة: واسط ٣٢°١٠\' وبغداد ٣٣°٢٠\' (غير مذكورين).',
            'الظهر حسب الكتاب: ثلاثة أرباع عليها أسماء البروج والربع الرابع ربع جيب.',
            'العنكبوت في الأصل لاحق (ق ٨هـ) ومثبت؛ رسمنا عنكبوتاً بسيطاً بـ١٢ كوكباً.'])

add(id='A2.14', page=89, builder='astrolabe', slug='ahmad_b_khalaf',
    title_ar='أسطرلاب أحمد بن خلف (نحو ٣٤٠هـ/٩٥٠م)', title_en='Astrolabe of Ahmad b. Khalaf (ca. 340/950)',
    model='Brass, engraved. Mater with bracket and suspension ring with a diameter of 130 mm. 4 discs for the latitudes 21°/24°; 30°/31°; 34°/36°; 37°/39°. Rete with 17 star pointers. Double pointer with sights on the back.',
    D=130, year=950, plates=[(21, 24), (30, 31), (34, 36), (37, 39)], stars=17, back=['alt'],
    assume=['الظهر في الصورة يحمل مقياس الارتفاع وخطي القطرين فقط.'])

add(id='A2.28', page=90, builder='astrolabe', slug='al_khujandi',
    title_ar='أسطرلاب الخجندي (٣٧٤هـ/٩٨٤م)', title_en='The astrolabe of al-Khujandi (374/984)',
    model='Diameter: 151 mm. Thickness: 6 mm.',
    D=151, year=984, plates=[(21, 27), (30, 33), (36, 39), (66 + 17 / 60, None)], stars=20, back=['alt', 'shadow'],
    assume=['الصفائح من وصف الأصل: ٢١، ٢٧، ٣٠، ٣٣، ٣٦، ٣٩ و٦٦°١٧\' (لم نرسم صفيحة مطرح الشعاعات).',
            'السمك الكلي ٦ مم: وزعناه على الأم والحجرة والصفائح.', 'عدد الكواكب ٢٠ (غير مذكور).'])

add(id='A2.18', page=91, builder='astrolabe', slug='carolingian_catalan',
    title_ar='الأسطرلاب الكتالوني (ق ١٠م) - أقدم أسطرلاب لاتيني', title_en='Catalan ("Carolingian") astrolabe, 10th c.',
    model='Brass, engraved. Mater with bracket and suspension ring. Diameter: 152 mm (with engraving for the latitude of 36°). 2 discs for the latitudes 39°/41°30\'; 45°/47°30\'. Rete with 20 star pointers. Double pointer with sights at the back. Calendars and shadow square. Latin lettering.',
    D=152, year=980, plates=[(39, 41.5), (45, 47.5)], mater_inside={'proj': 36}, stars=20, script='latin', num='roman',
    back=['alt', 'zodiac', 'calendar', 'shadow'], style='islamic',
    assume=['الأرقام اللاتينية مكتوبة بالأرقام الرومانية.'])

add(id='A2.29', page=92, builder='astrolabe', slug='lupitus_barcelona',
    title_ar='أسطرلاب لوبيتوس البرشلوني (Sententiae astrolabii)', title_en='Astrolabe after Lupitus of Barcelona',
    model='Brass, etched. Diameter: 135 mm, thickness: 5 mm. Made by M. Brunold.',
    D=135, year=990, plates=[(CLIM3, CLIM4), (CLIM5, CLIM6)], stars=27, script='latin', num='triple',
    back=['alt', 'zodiac', 'calendar'],
    assume=['الأقاليم ٣ و٤ و٥ و٦ بعروض بطلميوس: ٣٠°٢٢\' و٣٦° و٤٠°٥٦\' و٤٥°١\'.',
            'مقياس الحجرة مرقم بالجمّل (والأصل مرقم ثلاث مرات).', 'دائرة التقويم ٣٦٥ يوماً بأرقام الجمّل.'])

add(id='A2.11', page=94, builder='astrolabe', slug='sylvester_ii',
    title_ar='الأسطرلاب المنسوب للبابا سلفستر الثاني (٣٨٠هـ/٩٩٠م)', title_en='Astrolabe attributed to Pope Sylvester II',
    model='Brass, engraved. Mater with bracket and suspension ring, outer diameter 130 mm. Rete with 25 star pointers. 2 discs for the latitudes 30°/42° and 36°/38°. On the back calendars and shadow square. Double pointer with sights.',
    D=130, year=990, plates=[(30, 42), (36, 38)], stars=25, back=['alt', 'zodiac', 'calendar', 'shadow'], back_latin=True,
    assume=['الوجه بالعربية والظهر باللاتينية كما يصف الكتاب.'])

add(id='A2.12', page=95, builder='astrolabe', slug='ibn_as_saffar_toledo',
    title_ar='أسطرلاب محمد بن الصفار - طليطلة (٤٢٠هـ/١٠٢٩م)', title_en='Astrolabe of Muhammad b. as-Saffar, Toledo 1029',
    model='Brass, engraved. Mater with bracket and suspension ring with a diameter of 135 mm. 9 discs ... and one projection for the latitude of 72°. Rete with 29 star pointers. Double pointer with sights on the back. Calendar circle, shadow square.',
    D=135, year=1029, plates=[(6, 10.5), (14.5, 17.5), (21 + 40 / 60, 25), (28, 30), (32, 34 + 20 / 60), (36.5, 38.5), (40, 42), (45, 66)],
    mater_inside={'proj': 72}, stars=29, back=['alt', 'zodiac', 'calendar', 'shadow'], assume=[])

add(id='A2.13', page=96, builder='astrolabe', slug='an_naqqash_zaragoza',
    title_ar='أسطرلاب أحمد بن محمد النقاش - سرقسطة (٤٧٢هـ/١٠٧٩م)', title_en='Astrolabe of Ahmad b. Muhammad an-Naqqash, Zaragoza 1079',
    model='Brass, engraved. Mater with bracket and suspension ring with a diameter of 124 mm. 5 discs for the latitudes 21°/25°; 34°/37°; 35°/38°; 36°/39°; 38°/41°. Rete with 23 star pointers. Double pointer with sights. Calendar circle, shadow square and Arabic inscription on the back.',
    D=124, year=1079, plates=[(21, 25), (34, 37), (35, 38), (36, 39), (38, 41)], stars=23, back=['alt', 'zodiac', 'calendar', 'shadow'],
    legend_back='صنعه أحمد بن محمد النقاش بسرقسطة', assume=['نص الكتابة على الظهر مختصر (الأصل في المتحف الوطني الجرماني بنورنبرغ WI 353).'])

add(id='A2.05', page=97, builder='astrolabe', slug='ibrahim_b_said_valencia',
    title_ar='أسطرلاب إبراهيم بن سعيد السهلي - بلنسية (٤٧٨هـ/١٠٨٦م)', title_en='Astrolabe of Ibrahim b. Said as-Sahli, Valencia 1086',
    model='Brass, engraved. Mater with bracket and suspension ring with a diameter of 176 mm. 8 discs for the latitudes 13°/19°; 25°/32°; 30°/38°; 32°/35°; 37°/39°; 30°/40°; 38°/41°; 66°/42°. Rete with 28 star pointers. Double pointer with sights, length 166 mm.',
    D=176, year=1086, plates=[(13, 19), (25, 32), (30, 38), (32, 35), (37, 39), (30, 40), (38, 41), (66, 42)],
    mater_inside={'proj': 72}, stars=28, alidade_len=166, back=['alt', 'zodiac', 'calendar', 'shadow'],
    legend_back='صنعه إبراهيم بن سعيد ببلنسية', assume=['الحفر الثالث عشر لعرض ٧٢° على باطن الأم كما في الأصل.'])

add(id='A2.30', page=98, builder='astrolabe', slug='al_khamairi_1216_paris',
    title_ar='أسطرلاب محمد بن الفتوح الخمائري - إشبيلية (٦١٣هـ/١٢١٦م) بصفيحة باريس', title_en='Astrolabe of al-Khamairi, Seville 1216 (Paris plate)',
    model='Brass, etched. Diameter: 73 mm.',
    D=73, year=1216, plates=[(21 + 40 / 60, 25), (33.5, 37.5), (38.5, 34.5), (35.5, 31.5), (48 + 22 / 60, None)], stars=12,
    script='latin', num='latin', back=['alt', 'shadow'],
    assume=['القطر ٧٣ مم كما في الكتاب (يبدو صغيراً؛ تحقق إن كان ١٧٣ مم – الملفات المتجهة تُكبر بنسبة ثابتة).',
            'العروض الأصلية من جدول الكتاب ص ٩٩، وصفيحة باريس ٤٨°٢٢\'.', 'أسماء الكواكب والأرقام لاتينية كما في الحفر المتأخر.'])

add(id='A2.31', page=100, builder='astrolabe', slug='al_khamairi_1228',
    title_ar='أسطرلاب الخمائري (٦٢٦هـ/١٢٢٨م) بالتقويم الإسلامي والمسيحي', title_en='Astrolabe of al-Khamairi 1228 with calendars',
    model='Brass, etched. Diameter: 165 mm. 5 discs for the latitudes: 30°30\'/32°30\'; 33°30\'/34°30\'; 35°30\'/36°30\'; 37°30\'/38°30\'; 39°30\'/40°.',
    D=165, year=1228, plates=[(30.5, 32.5), (33.5, 34.5), (35.5, 36.5), (37.5, 38.5), (39.5, 40)], stars=20,
    back=['alt', 'zodiac', 'calendar', 'calendar_syriac', 'shadow'], back_latin=True,
    assume=['تقويمان على الظهر: الشهور اللاتينية والشهور السريانية، محسوبان من طول الشمس لسنة ١٢٢٨م.', 'عدد الكواكب ٢٠.'])

add(id='A2.24', page=101, builder='astrolabe', slug='marine_museum_istanbul',
    title_ar='أسطرلاب متحف البحرية بإسطنبول (٦١٩هـ/١٢٢٢م) - قطر ٥٦ سم', title_en='Astrolabe of the Marine Museum, Istanbul (619/1222)',
    model='Brass, etched; diameter: 56 cm.',
    D=560, year=1222, eps=23 + 51 / 60, plates=[(30, 35), (40, 41)], stars=20, back=['alt', 'zodiac', 'calendar_syriac', 'shadow', 'sine', 'hours'],
    assume=['الميل الكلي ٢٣°٥١\' كما يذكر الكتاب.', 'تصميم الظهر مقترح (غير موصوف).', 'السمك الأصلي ١١ مم.'])

add(id='A2.15', page=103, builder='astrolabe', slug='abdalkarim_al_misri',
    title_ar='أسطرلاب عبد الكريم المصري (٦٥٠هـ/١٢٥٢م)', title_en='Astrolabe of Abdalkarim al-Misri (650/1252)',
    model='Brass, engraved. Mater with bracket and suspension ring with a diameter of 280 mm. 3 discs for the latitudes 30°/44°; 33°/40°; 36°/66° 30\'. Rete with 25 inscribed star pointers. Double pointer with sights on the back. Calendars, quadrants.',
    D=280, year=1252, plates=[(30, 44), (33, 40), (36, 66.5)], stars=25, back=['alt', 'zodiac', 'calendar_syriac', 'sine', 'hours', 'shadow'], assume=[])

add(id='A2.17', page=104, builder='astrolabe', slug='hama_regiomontanus',
    title_ar='أسطرلاب حماة (٦٩٨هـ/١٢٩٩م) - أسطرلاب ريجيومونتانوس', title_en='Astrolabe from Hama 1299 (Regiomontanus)',
    model='Brass, engraved. Mater with bracket and suspension ring with a diameter of 161 mm. 4 discs (30°/33° and 36°/39° of Arabic origin; 45°/48° and 51° for European latitudes; 42° not completed). Rete of silver (spider with figures). On the back, the alidade with sights, and a pointer attached at right angles.',
    D=161, year=1299, plates=[(30, 33), (36, 39), (45, 48), (51, 42)], stars=20, back=['alt', 'sine', 'shadow'], alidade_pointer=True,
    assume=['العنكبوت الفضي ذو الصور منقول بالتتبع الآلي من صورة الكتاب (فصل لون الفضة عن النحاس) ثم أضيفت حلقة خارجية ومحور للمتانة؛ دقة التفاصيل محدودة بدقة الصورة.'])

add(id='A2.07', page=105, builder='astrolabe', slug='al_ashraf_yemen',
    title_ar='أسطرلاب الملك الأشرف عمر بن يوسف - اليمن (٦٩٠هـ/١٢٩١م)', title_en='Astrolabe of al-Malik al-Ashraf, Yemen 1291',
    model='Brass, engraved. Mater with bracket and suspension ring, outer diameter 155 mm. 4 discs for the latitudes 13°/15°; 13°37\'/14°30\'; 21°, and 7th climate /24° and 6th climate. Rete with 20 star pointers, diameter 130 mm. On the back alidade with sights, length 140 mm. Arabic legend on the back.',
    D=155, year=1291, plates=[(13, 15), (13 + 37 / 60, 14.5), (21, CLIM7), (24, CLIM6)], stars=20, rete_d=130, alidade_len=140,
    back=['alt', 'zodiac', 'decans', 'triplicities', 'shadow'], legend_back='عمل الملك الأشرف عمر بن يوسف',
    assume=['الإقليم السابع ٤٨°٣٢\' والسادس ٤٥°١\' بعروض بطلميوس.', 'نص الكتابة على الظهر مختصر.'])

add(id='A2.06', page=106, builder='astrolabe', slug='british_museum_13c',
    title_ar='أسطرلاب عربي (ق ٧هـ/١٣م) - المتحف البريطاني', title_en='Arabic astrolabe, 13th c. (British Museum)',
    model='Brass, engraved. Mater with bracket and suspension ring, diameter 150 mm. 3 discs for the latitudes 21°/24°; 27°/33°; 30°/31°. Rete with 29 star pointers, diameter 120 mm. Double pointer with sights, length 140 mm.',
    D=150, year=1250, plates=[(21, 24), (27, 33), (30, 31)], stars=29, rete_d=120, alidade_len=140,
    back=['alt', 'zodiac', 'calendar_syriac', 'shadow'], assume=['تصميم الظهر غير موصوف.'])

add(id='A2.33', page=107, builder='astrolabe', slug='muhammad_saffar_1477',
    title_ar='أسطرلاب شمس الدين محمد صفار (٨٨٤هـ/١٤٧٧م)', title_en='Astrolabe of Shamsaddin Muhammad Saffar (1477)',
    model='Brass, etched. Mater with bracket and suspension ring, outer diameter 120 mm. 2 discs for the latitudes 33°/36° and 72°.',
    D=120, year=1477, plates=[(33, 36), (72, None)], stars=16, back=['alt', 'sine', 'shadow'], assume=['عدد الكواكب ١٦ وتصميم الظهر مقترحان.'])

add(id='A2.16', page=108, builder='astrolabe', slug='muqim_al_yazdi_1647',
    title_ar='أسطرلاب محمد مقيم اليزدي للشاه عباس الثاني (١٠٥٧هـ/١٦٤٧م)', title_en='Astrolabe of Muhammad Muqim al-Yazdi (1647)',
    model='Brass, engraved. Mater with bracket and suspension ring, diameter 30 cm. In the mater the coordinates of 46 cities ... longitudes counted from a prime meridian 28°30\' west of Toledo. 4 discs for the latitudes 23°/43°; 29°/30°; 33°/37°; 36°/37°. Rete with 46 star pointers. Double pointer with sights. Sine quadrant, zodiacal quadrant and two shadow squares.',
    D=300, year=1647, plates=[(23, 43), (29, 30), (33, 37), (36, 37)], stars=46,
    mater_inside={'gazetteer': CITIES_IRAN, 'lon0': 28.5 + 4.03}, back=['alt', 'sine', 'hours', 'shadow'],
    assume=['المدن الـ٤٦ مختارة بين بغداد وبلخ بإحداثيات حديثة؛ الطول محسوب من خط الطول الأول الواقع ٢٨°٣٠\' غرب طليطلة كما يذكر الكتاب.',
            'أسماء الكواكب بالعربية (الأصل بالفارسية).', 'الربع البروجي رسمناه ربع ساعات زمانية.'])

add(id='A2.32', page=109, builder='astrolabe', slug='ottoman_1680',
    title_ar='أسطرلاب عثماني (١٠٩١هـ/١٦٨٠م)', title_en='An Ottoman astrolabe (1680)',
    model='Brass, etched. Diameter 183 mm. 4 discs. Alidade with sights.',
    D=183, year=1680, plates=[(21, 30), (34, 36), (41, 42), ('horizons',)], stars=24, back=['alt', 'sine', 'shadow'],
    assume=['العروض ٢١ و٣٠ و٣٤ و٣٦ و٤١ و٤٢ من الكتاب على ثلاث صفائح، والصفيحة الرابعة صفيحة آفاق.', 'الظهر: ربع جيب وربع ظل كما في الأصل.'])

add(id='A2.20', page=110, builder='astrolabe', slug='persian_1706',
    title_ar='أسطرلاب فارسي (١١١٨هـ/١٧٠٦م) - ملك المعهد', title_en='Persian astrolabe (1706)',
    model='Brass, engraved. Diameter 90 mm. 4 discs. Rete with 21 star names. Double pointer with sights. The back carries a calendar with zodiac signs and shadow squares.',
    D=90, year=1706, plates=[(21 + 10 / 60, None), (21 + 10 / 60, None), (22 + 40 / 60, None), (39.25, None)], stars=21,
    mater_inside={'gazetteer': CITIES_IRAN[:36], 'lat_only': True}, back=['alt', 'zodiac', 'calendar_syriac', 'shadow'],
    assume=['عروض المدن الـ٣٦ صحيحة حديثة (الأصل فيه أخطاء كما يذكر الكتاب).'])

add(id='A2.08', page=111, builder='astrolabe', slug='spanish_gothic',
    title_ar='أسطرلاب إسباني قوطي (ق ١٤م)', title_en='Spanish-Gothic astrolabe, 14th c.',
    model='Brass, engraved. Gothic numerals. Mater with bracket and suspension ring, outer diameter 120 mm. 2 discs for the latitudes 36°/40° and 44°/48°. The rete with arabesques and quatre foil ornament shows 17 star positions. Ruler with a radius of 60 mm. On the back, ecliptic circle and calendar circle, with a shadow square and a diagram for determining the weekday at the beginning of the year. Double pointer with sights.',
    D=120, year=1350, plates=[(36, 40), (44, 48)], stars=17, script='latin', num='latin', style='gothic', rule=60, limb_hours=True,
    back=['alt', 'zodiac', 'calendar', 'shadow', 'dominical'],
    assume=['الأرقام القوطية رُسمت بأرقام حديثة (يمكن استبدال الخط).', 'دائرة الحروف الأحدية لـ٢٨ سنة تبدأ من ١٣٥٠م.'])

add(id='A2.09', page=112, builder='astrolabe', slug='european_1500',
    title_ar='أسطرلاب أوروبي (نحو ١٥٠٠م)', title_en='European astrolabe, ca. 1500',
    model='Brass, engraved. Mater with bracket and suspension ring, diameter 100 mm with horizontal coordinates for the latitude of 48°. Without discs. Rete with 14 star positions and an hour scale. Ruler in the radius of 50 mm, back with ecliptic circle and calendar circle, shadow square, diagram of the unequal hours and double pointer with sights.',
    D=100, year=1500, plates=[], mater_inside={'proj': 48}, stars=14, script='latin', num='latin', style='gothic', rule=50, rete_hours=True,
    back=['alt', 'zodiac', 'calendar', 'shadow', 'hours'], assume=[])

add(id='A2.10', page=113, builder='astrolabe', slug='gualterus_arsenius',
    title_ar='أسطرلاب على طراز ورشة جوالتروس أرسينيوس (نحو ١٥٧٠م)', title_en='Astrolabe after Gualterus Arsenius, ca. 1570',
    model='Brass, engraved. Mater with bracket and suspension ring, outer diameter 156 mm. 3 discs for the latitudes 39°/42°, 45°/48° and 51°/54°. Rete with 37 star-positions. Double pointer with sights. Back with az-Zarqali-projection with 2.5° grid and 25 star positions. Over these a horizontal bar rotates with the twilight border, together with a cursor and brachiolus. 4 x 90° division on the rim. Latin lettering.',
    D=156, year=1570, plates=[(39, 42), (45, 48), (51, 54)], stars=37, script='latin', num='latin', style='renaissance',
    back=['alt', 'saphea'], saphea_grid=2.5, saphea_stars=25, back_bar=True, alidade=True,
    assume=['العنكبوت ذو الأشرطة المتشابكة وصورة الملاك مبسط بزخرف هندسي.'])

add(id='A2.04', page=114, builder='astrolabe', slug='erasmus_habermel',
    title_ar='أسطرلاب على طراز إراسموس هابرمل (نحو ١٦٠٠م) - أم باثني عشر ضلعاً', title_en='Astrolabe after Erasmus Habermel, ca. 1600',
    model='Brass, engraved. 12-cornered mater with bracket and suspension ring, diameter 210 mm. 3 discs for the latitudes 39°/42°, 45°/48° and 51°/54°. Rete with 30 star positions. Double pointer with sights, length 210 mm. On the back a horizontal bar with a cursor and brachiolus.',
    D=210, year=1600, shape='12gon', plates=[(39, 42), (45, 48), (51, 54)], stars=30, script='latin', num='latin', style='renaissance',
    alidade_len=210, back=['alt', 'saphea'], saphea_grid=5, saphea_stars=20, back_bar=True, assume=[])

add(id='A2.19', page=115, builder='astrolabe', slug='brunold_didactic',
    title_ar='أسطرلاب تعليمي (م. برونولد)', title_en='Didactic astrolabe (M. Brunold)',
    model='Brass, engraved. Mater with bracket and suspension ring, diameter 118 mm. Rete with 19 star pointers. 4 discs for the latitudes 18°/28°, 30°/36°, 37° and 39°. Double pointer with sights with a diameter of 110 mm on the back. Arabic and Latin inscriptions.',
    D=118, year=2000, plates=[(18, 28), (30, 36), (37, None), (39, None)], stars=19, alidade_len=110, back=['alt', 'zodiac', 'calendar', 'shadow'],
    assume=['الكتابات بالعربية (والأصل عربي ولاتيني).'])

# ------------------------------------------------------------------ universal discs
add(id='A2.03', page=116, builder='saphea', slug='saphea_ibn_hudhail',
    title_ar='الصفيحة الزرقالية لمحمد بن هذيل - مرسية (٦٥٠هـ/١٢٥٢م)', title_en='Universal disc of Ibn Hudhail, Murcia 1252',
    model='Brass, etched. Diameter 185 mm. Length of the alidade 185 mm. Ruler with division into degrees, length 165 mm. Thickness 3 mm. Arabic alphabet numerals.',
    D=185, year=1252, t=3, alidade=185, rule_len=165, both=True, grid=5, assume=['الظهر ظهر أسطرلاب عادي مع دائرة صغيرة للقمر كما يصف الكتاب.'])

add(id='A2.34', page=117, builder='saphea', slug='saphea_al_khamairi',
    title_ar='الصفيحة الشكازية لمحمد بن فتوح الخمائري - إشبيلية (٦١٣هـ/١٢١٦م)', title_en='Universal disc of al-Khamairi, Seville 1216',
    model='Brass, etched. Diameter 185 mm. Length of the alidade 185 mm. Ruler with divisions into degrees, length 165 mm. Arabic alphabet numerals.',
    D=185, year=1216, alidade=185, rule_len=165, both=True, grid=5, stars=33, assume=['٣٣ كوكباً على الوجه كما في الأصل.'])

add(id='A2.02', page=118, builder='saphea', slug='saphea_libros_del_saber',
    title_ar='الصفيحة الزرقالية حسب كتب المعرفة الفلكية لألفونسو العاشر', title_en='Universal disc after the Libros del saber',
    model='Brass, etched. Diameter: 185 mm. Thickness: 3 mm. Calendars and sine lines. Roman numerals.',
    D=185, year=1277, t=3, alidade=185, rule_len=165, both=True, grid=5, script='latin', num='roman',
    back=['alt', 'zodiac', 'calendar', 'sine', 'shadow'], assume=[])

add(id='A2.01', page=119, builder='astrolabe', slug='ibn_as_sarraj_universal',
    title_ar='الأسطرلاب الشامل لابن السراج (ت ٧٢٩هـ/١٣٢٩م)', title_en='Universal astrolabe of Ibn as-Sarraj',
    model='Brass, etched. Mater with bracket and suspension ring, diameter 150 mm. Rete (trigonometric 5 degree grid with 18 star pointers) with a diameter of 134 mm. 3 discs contain doubly folded almucantarates (6°/12°; 18°/24°; 24°/30°; 36°/42°; 48°/54°; 60°/66°). Pointer with a radius of 67 mm. The back carries a double pointer with sights.',
    D=150, year=1329, rete_d=134, grid_rete=True, stars=18, rule=67,
    plates=[('fold', 6, 12, 18, 24), ('fold', 24, 30, 36, 42), ('fold', 48, 54, 60, 66)], back=['alt', 'sine', 'shadow'],
    assume=['كل وجه من الصفائح مطوي لعرضين: النصف الأيسر للأول والأيمن للثاني.',
            'شبكة العنكبوت: النصف السفلي شبكة المسقط العام كل ٥° مفرغة، والعلوي فلك البروج والكواكب.'])

# ------------------------------------------------------------------ spherical & linear
add(id='A1.08', page=123, builder='spherical', slug='spherical_an_nairizi', variant='nayrizi',
    title_ar='الأسطرلاب الكري للنيريزي', title_en='Spherical astrolabe of an-Nairizi',
    model='Brass, etched, diameter: 17 cm.', D=170, lat=33 + 20 / 60, year=900, stars=16,
    assume=['عرض الخطوط على الكرة ٣٣°٢٠\' (بغداد).', 'العنكبوت للنصف الشمالي فقط: نصف فلك البروج وربع الارتفاع والكراسي الثلاثة.'])
add(id='A1.09', page=125, builder='spherical', slug='spherical_al_biruni', variant='biruni',
    title_ar='الأسطرلاب الكري للبيروني', title_en='Spherical astrolabe of al-Biruni',
    model='Brass, etched, diameter: 17 cm.', D=170, lat=33 + 35 / 60, year=1030, stars=16,
    assume=['العرض ٣٣°٣٥\' (غزنة).'])
add(id='A1.10', page=127, builder='spherical', slug='spherical_al_marrakushi', variant='marrakushi',
    title_ar='الأسطرلاب الكري للمراكشي', title_en='Spherical astrolabe of al-Marrakushi',
    model='Brass, etched, diameter: 8 cm.', D=80, lat=30, year=1280, stars=10,
    assume=['العرض ٣٠° (القاهرة)، وثقوب العروض على ربع نصف النهار.'])
add(id='A1.11', page=129, builder='spherical', slug='spherical_libros_del_saber', variant='alfonso',
    title_ar='الأسطرلاب الكري حسب كتب المعرفة الفلكية', title_en='Spherical astrolabe after the Libros del saber',
    model='Brass, etched, diameter: 17 cm.', D=170, lat=39 + 52 / 60, year=1277, stars=16, script='latin',
    assume=['العرض ٣٩°٥٢\' (طليطلة).'])
add(id='A1.12', page=131, builder='spherical', slug='spherical_musa_1480', variant='musa',
    title_ar='أسطرلاب كري عربي (٨٨٥هـ/١٤٨٠م) صنعة موسى', title_en='Spherical astrolabe made by Musa, 1480',
    model='Brass, etched, diameter: 17 cm.', D=170, lat=30, year=1480, stars=16,
    assume=['العرض ٣٠° (غير مذكور).'])
add(id='A1.13', page=133, builder='spherical', slug='spherical_1660_stand', variant='stand',
    title_ar='أسطرلاب كري (١٠٧٠هـ/١٦٦٠م) على حامل', title_en='Spherical astrolabe of 1660 on a stand',
    model='Brass, etched. Diameter: 8 cm. Can be set to different positions. Stand, height: 11.5 cm.', D=80, lat=30, year=1660, stars=10, stand=115,
    assume=['العرض ٣٠° (القاهرة).'])
add(id='A1.14', page=134, builder='linear', slug='linear_astrolabe_tusi',
    title_ar='الأسطرلاب الخطي (عصا الطوسي)', title_en='The linear astrolabe (staff of at-Tusi)',
    model='Wood, paper, strings with brass-weights. Length: 46 cm.', L=460, lat=36.3,
    assume=['العرض ٣٦°١٨\' (طوس).', 'التقسيمات على مخطط هنري ميشيل المنشور في الكتاب.'])

# ------------------------------------------------------------------ quadrants
add(id='A3.03', page=136, builder='sine_quadrant', slug='quadrant_al_mizzi',
    title_ar='ربع المزي (٧٣٤هـ/١٣٣٤م)', title_en='Quadrant of al-Mizzi (734/1334)',
    model='Brass, engraved. Radius 150 mm. Front with sights.', R=150, lat=33.5, front='astrolabic', back='sine',
    assume=['الوجه: ربع مقنطرات لعرض دمشق ٣٣°٣٠\' كما في الصورة، والظهر ربع جيب.'])
add(id='A3.04', page=137, builder='sine_quadrant', slug='sine_quadrant_damascus_1335',
    title_ar='ربع الجيب لعلي بن الشهاب - دمشق (٧٣٥هـ/١٣٣٥م)', title_en='Sine quadrant, Damascus 1335',
    model='Brass, etched. Radius: 135 mm.', R=135, lat=33.5, front='sine', back='astrolabic', assume=['الظهر ربع مقنطرات لعرض ٣٣°٣٠\'.'])
add(id='A3.09', page=138, builder='sine_quadrant', slug='sexagesimal_quadrant_maghrib',
    title_ar='ربع الجيب الستيني من المغرب', title_en='Sexagesimal sine quadrant from the Maghrib',
    model='Brass, engraved. Radius: 125 mm.', R=125, front='sine', assume=['منحنى العصر محسوب: ظل العصر = الشاخص + ظل الزوال.'])
add(id='A3.07', page=139, builder='shakkaziya', slug='shakkaziya_double_quadrant',
    title_ar='الربع الشكازي المزدوج للماريديني', title_en='Shakkaziya double quadrant of al-Maridini',
    model='Brass, engraved. Radius: 167 mm.', R=167, year=1400, stars=7, assume=[])
add(id='A3.01', page=140, builder='shakkaziya', slug='double_quadrant_latin',
    title_ar='الربع المزدوج (نسخة أوروبية ق ١٥م)', title_en='Double quadrant (European, 15th c.)',
    model='Brass, engraved. Radius 160 mm.', R=160, year=1450, stars=7, script='latin', num='latin', assume=[])
add(id='A3.02', page=141, builder='meteoroscope', slug='meteoroscope_apian',
    title_ar='الميتيوروسكوب لبيتر أبيان', title_en='Meteoroscope by Peter Apian',
    model='Brass, engraved. Radius 150 mm. A sine quadrant is located on the back, above it a movable ruler.', R=150, year=1540, script='latin', num='latin', assume=[])
add(id='A3.10', page=142, builder='dastur', slug='dastur_quadrant',
    title_ar='دائرة الدستور لعلي بن إبراهيم المطعم (٧٣٤هـ/١٣٣٤م)', title_en='Dastur quadrant (734/1334)',
    model='Brass, engraved. Radius 18 cm.', D=182, year=1334, lat=31.5, stars=12,
    assume=['الكتاب يذكر "نصف قطر ١٨ سم" ويذكر أن الأصل قطره ١٨٢ مم؛ اعتمدنا قطر ١٨٢ مم (ضاعف المقياس ×٢ إن أردت نصف القطر ١٨ سم).',
            'العرض ٣١°٣٠\' (بين ٣٠ و٣٣).'])
add(id='A3.11', page=143, builder='quadrant_disc', slug='quadrant_disc_maghrib',
    title_ar='قرص الأرباع المغربي', title_en='Quadrant disc from the Maghrib',
    model='Brass, engraved. Radius 25 cm. (original: diameter 250 mm, thickness 0.8 mm)', D=250, assume=['اعتمدنا قطر ٢٥٠ مم وسمك ٠٫٨ مم كما في وصف الأصل.'])
add(id='A3.05', page=144, builder='sine_quadrant', slug='european_quadrant_18c',
    title_ar='ربع أوروبي (ق ١٨م)', title_en='European quadrant, 18th c.',
    model='Brass, engraved. Radius 120 mm.', R=120, lat=48, front='horary', script='latin', num='latin',
    assume=['خطوط الساعات المستوية لعرض ٤٨° مع مربع الظل (التصميم مقترح وفق الأرباع الأوروبية).'])

# ------------------------------------------------------------------ other instruments
add(id='A4.25', page=145, builder='indian', slug='indian_circle',
    title_ar='الدائرة الهندية', title_en='Indian circle', model='Brass, engraved. Diameter: 250 mm. Height of the gnomon: 63 mm.', D=250, gnomon=63, assume=[])
add(id='A4.21', page=146, builder='meridian', slug='ibn_al_haitham_meridian',
    title_ar='آلة استخراج خط نصف النهار لابن الهيثم', title_en='Instrument for determining the meridian (Ibn al-Haitham)',
    model='Brass, gilded. Hard wood. Height: 1 m.', H=1000,
    assume=['الكتاب يعطي الارتفاع الكلي فقط؛ أبعاد نصف الدائرة واللوح والعضادة مقدّرة من الصورة.'])
add(id='A4.24', page=147, builder='triangle', slug='khazini_triangle',
    title_ar='الآلة ذات المثلث للخازني', title_en='The instrument with the triangle (al-Khazini)',
    model='Brass, etched. Hard wood. Plumb.', leg=200, assume=['طول ساق المثلث ٢٠٠ مم مقدر من الصورة.'])
add(id='A4.33', page=148, builder='alt_table', slug='altitude_instrument_1', variant=1, table=660,
    title_ar='آلة قياس الارتفاع الأولى (السموأل المغربي)', title_en='Instrument for measuring altitudes no. 1',
    model='Table of hard wood, length: 66 cm. Scale mounted on the side, engraved Arabic letters with numerical values.',
    assume=['طول الذراع = (٦٦٠ - ٤٠)/٢ = ٣١٠ مم.'])
add(id='A4.34', page=149, builder='alt_table', slug='altitude_instrument_2', variant=2, table=460,
    title_ar='آلة قياس الارتفاع الثانية', title_en='Instrument for measuring altitudes no. 2',
    model='Table of hard wood, length: 46 cm. Brass pointer that can be rotated for sighting and a lever for tightening.',
    assume=['طول الذراع ٣٨٠ مم.'])
add(id='A4.35', page=150, builder='alt_table', slug='altitude_instrument_3', variant=3, table=635,
    title_ar='آلة قياس الارتفاع الثالثة', title_en='Instrument for measuring altitudes no. 3',
    model='Table of hard wood, length: 63.5 cm. A scale is mounted on one side of the table with engraved Arabic letters with numerical values.',
    assume=['طول الذراع ٥٧٥ مم.'])

INSTRUMENTS = I
