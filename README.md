# رسومات تنفيذية للآلات الفلكية — من الصفحات ٧٩ إلى ١٥٠

> **جديد: النسخة الثانية** في [`instruments_v2/`](instruments_v2/README.md): خطوط دقيقة بلا تعرج، الوجه والظهر بنفس خط القص، الكراسي منقولة من صور الكتاب، و٥٣ آلة. هذه النسخة الأولى باقية كما هي.

المصدر: فؤاد سزكين، **Science and Technology in Islam, vol. II — Astronomy** (فرانكفورت ٢٠١٠)، الصفحات ٧٩–١٥٠.

يحتوي المستودع على **رسومات تنفيذية كاملة لكل آلة (٥٢ آلة)** في هذه الصفحات: الأسطرلابات المسطحة، والصفائح الزرقالية، والأسطرلاب الشامل، والأسطرلابات الكرية، والأسطرلاب الخطي، والأرباع، والآلات الرصدية الأخرى. لكل آلة رسم للوجه والظهر ولكل قطعة على حدة، جاهزة للحِرفي أو لآلة CNC.

## محتوى مجلد كل آلة `instruments/NN_رقم-الجرد_الاسم/`

| الملف | الاستعمال |
|---|---|
| `*_workshop.pdf` | **ملف الحِرفي**: الصفحة الأولى لوحة عامة بأسلوب الرسم اليدوي بالحبر على ورق، ثم **كل قطعة على صفحة مستقلة بمقياس ١:١** مع المادة والسمك والعدد وأقطار الثقوب والأبعاد. يُطبع بمقياس ١٠٠٪ ويُنقل على النحاس. |
| `*_overview.jpg` | اللوحة العامة كصورة (الوجه المجمّع، الظهر المجمّع، وكل القطع). |
| `cnc/*.dxf` | لكل قطعة: هندسة دقيقة بالمليمتر ١:١ (دوائر وأقواس حقيقية ARC/CIRCLE). |
| `cnc/*.svg` | نفس الهندسة بصيغة SVG بالمليمتر (Inkscape / الليزر / الحفر). |
| `README.md` | بيانات النموذج كما في الكتاب، جدول القطع، القيم المحسوبة، جدول الكواكب، وكل افتراض لم يذكره الكتاب. |
| `reference/` | صفحة الكتاب للمقارنة الشكلية والزخرفية. |

### طبقات ملفات CNC

| الطبقة | اللون | العملية |
|---|---|---|
| `CUT_OUTER` | أحمر | قص المحيط الخارجي |
| `CUT_INNER` | بنفسجي | قص الفتحات والتفريغ (العنكبوت، الثقوب، الكرسي) |
| `ENGRAVE` | أسود | حفر الخطوط الرئيسية والتدريج |
| `ENGRAVE_FINE` | رمادي | حفر الخطوط الثانوية (أخف أو أقل عمقاً) |
| `TEXT` | أزرق | حفر الكتابة والأرقام (محيطات حروف مغلقة — تصلح للحفر V أو التعبئة) |
| `BEND` | برتقالي | خط ثني (الهدفات، العروة) |
| `GUIDE` | أخضر | خط مساعد — لا يُنفذ |

## الدقة: كل الخطوط محسوبة رياضياً
لم يُنسخ أي خط من الصور، وكل الخطوط مستخرجة بالحساب:
- **الصفائح**: إسقاط مجسَّم (ستيريوغرافي) من القطب الجنوبي لكل عرض مذكور في الكتاب: الأفق، والمقنطرات، والسموت، وخط الشفق (−١٨°)، والساعات الزمانية، ومدارا الجدي والسرطان، ومعدل النهار. وكل منحنى دائرة حقيقية تُحسب بمركزها ونصف قطرها، وتُقص حوافها بدقة ١٠⁻⁷ درجة.
- **العنكبوت**: يُحسب فلك البروج وتقسيمه درجةً درجة من القطب. ومواضع الكواكب مأخوذة من فهرس حديث بعد تقديم الاعتدالين إلى **سنة صنع كل آلة**، وبالميل الكلي المستعمل فيها.
- **الظهر**: تُحسب دوائر التقويم من طول الشمس الحقيقي لكل يوم في سنة الصنع (تقويم يولياني)، فتأتي مطابقة لدائرة البروج. وتُحسب أيضاً مربعات الظل، وربع الجيب (٦٠ خطاً) مع منحنى العصر وقوس الميل الأعظم، وخطوط الساعات الزمانية.
- **الصفيحة الزرقالية والشكازية**: إسقاط من نقطة الاعتدال على مستوى المارة بالانقلابين، وتقسيم مسطرة الأفق = نق × ظا(θ/٢).
- **الأرباع**: يُحسب ربع المقنطرات بطيّ إسقاط الصفيحة، وكذلك ربع الجيب الستيني وخطوط الساعات المستوية الأوروبية.
- **الكرية**: خطوط الكرة محسوبة، ويُرفق ملف `sphere_engraving.csv` بإحداثيات x,y,z للحفر بمحور رابع، مع فرد حلقات العنكبوت مستقيمة بطول المحيط.
- **الأسطرلاب الخطي**: الميول والارتفاعات ومراكز المقنطرات ومقياس الأوتار، على مخطط هنري ميشيل المنشور في الكتاب.
- **آلات السموأل الثلاث**: تدريج المساطر محسوب: ٢ل جتا ع، ل جا ع، ل جتا ع، ومرقّم بحروف الجمّل.

الأبعاد الرئيسية (القطر، أو نصف القطر، أو الطول، أو السمك، وعروض الصفائح، وعدد الكواكب، وطول العضادة والمسطرة) مأخوذة **من فقرة "Our model" في الكتاب لكل آلة**. أما ما لم يذكره الكتاب فمكتوب صراحةً في قسم «افتراضات» في README كل آلة.

## فهرس الآلات

| # | صفحة الكتاب | الجرد | الآلة | English | ملفات CNC |
|---|---|---|---|---|---|
| 1 | 86 | `A2.25` | [أسطرلاب نسطولس (٣١٥هـ/٩٢٧م)](instruments/01_A2_25_nastulus_kuwait/README.md) | Astrolabe of Nastulus (315/927) | 12 |
| 2 | 87 | `A2.26` | [الأسطرلاب الثاني لنسطولس (الأم فقط)](instruments/02_A2_26_nastulus_cairo_mater/README.md) | The second astrolabe of Nastulus (mater only) | 7 |
| 3 | 88 | `A2.27` | [أسطرلاب حامد بن علي الواسطي](instruments/03_A2_27_hamid_al_wasiti/README.md) | The astrolabe of Hamid b. Ali al-Wasiti | 12 |
| 4 | 89 | `A2.14` | [أسطرلاب أحمد بن خلف (نحو ٣٤٠هـ/٩٥٠م)](instruments/04_A2_14_ahmad_b_khalaf/README.md) | Astrolabe of Ahmad b. Khalaf (ca. 340/950) | 18 |
| 5 | 90 | `A2.28` | [أسطرلاب الخجندي (٣٧٤هـ/٩٨٤م)](instruments/05_A2_28_al_khujandi/README.md) | The astrolabe of al-Khujandi (374/984) | 17 |
| 6 | 91 | `A2.18` | [الأسطرلاب الكتالوني (ق ١٠م) - أقدم أسطرلاب لاتيني](instruments/06_A2_18_carolingian_catalan/README.md) | Catalan ("Carolingian") astrolabe, 10th c. | 14 |
| 7 | 92 | `A2.29` | [أسطرلاب لوبيتوس البرشلوني (Sententiae astrolabii)](instruments/07_A2_29_lupitus_barcelona/README.md) | Astrolabe after Lupitus of Barcelona | 14 |
| 8 | 94 | `A2.11` | [الأسطرلاب المنسوب للبابا سلفستر الثاني (٣٨٠هـ/٩٩٠م)](instruments/08_A2_11_sylvester_ii/README.md) | Astrolabe attributed to Pope Sylvester II | 14 |
| 9 | 95 | `A2.12` | [أسطرلاب محمد بن الصفار - طليطلة (٤٢٠هـ/١٠٢٩م)](instruments/09_A2_12_ibn_as_saffar_toledo/README.md) | Astrolabe of Muhammad b. as-Saffar, Toledo 1029 | 26 |
| 10 | 97 | `A2.05` | [أسطرلاب إبراهيم بن سعيد السهلي - بلنسية (٤٧٨هـ/١٠٨٦م)](instruments/10_A2_05_ibrahim_b_said_valencia/README.md) | Astrolabe of Ibrahim b. Said as-Sahli, Valencia 1086 | 26 |
| 11 | 98 | `A2.30` | [أسطرلاب محمد بن الفتوح الخمائري - إشبيلية (٦١٣هـ/١٢١٦م) بصفيحة باريس](instruments/11_A2_30_al_khamairi_1216_paris/README.md) | Astrolabe of al-Khamairi, Seville 1216 (Paris plate) | 19 |
| 12 | 100 | `A2.31` | [أسطرلاب الخمائري (٦٢٦هـ/١٢٢٨م) بالتقويم الإسلامي والمسيحي](instruments/12_A2_31_al_khamairi_1228/README.md) | Astrolabe of al-Khamairi 1228 with calendars | 20 |
| 13 | 101 | `A2.24` | [أسطرلاب متحف البحرية بإسطنبول (٦١٩هـ/١٢٢٢م) - قطر ٥٦ سم](instruments/13_A2_24_marine_museum_istanbul/README.md) | Astrolabe of the Marine Museum, Istanbul (619/1222) | 14 |
| 14 | 103 | `A2.15` | [أسطرلاب عبد الكريم المصري (٦٥٠هـ/١٢٥٢م)](instruments/14_A2_15_abdalkarim_al_misri/README.md) | Astrolabe of Abdalkarim al-Misri (650/1252) | 16 |
| 15 | 104 | `A2.17` | [أسطرلاب حماة (٦٩٨هـ/١٢٩٩م) - أسطرلاب ريجيومونتانوس](instruments/15_A2_17_hama_regiomontanus/README.md) | Astrolabe from Hama 1299 (Regiomontanus) | 18 |
| 16 | 105 | `A2.07` | [أسطرلاب الملك الأشرف عمر بن يوسف - اليمن (٦٩٠هـ/١٢٩١م)](instruments/16_A2_07_al_ashraf_yemen/README.md) | Astrolabe of al-Malik al-Ashraf, Yemen 1291 | 18 |
| 17 | 106 | `A2.06` | [أسطرلاب عربي (ق ٧هـ/١٣م) - المتحف البريطاني](instruments/17_A2_06_british_museum_13c/README.md) | Arabic astrolabe, 13th c. (British Museum) | 16 |
| 18 | 107 | `A2.33` | [أسطرلاب شمس الدين محمد صفار (٨٨٤هـ/١٤٧٧م)](instruments/18_A2_33_muhammad_saffar_1477/README.md) | Astrolabe of Shamsaddin Muhammad Saffar (1477) | 13 |
| 19 | 108 | `A2.16` | [أسطرلاب محمد مقيم اليزدي للشاه عباس الثاني (١٠٥٧هـ/١٦٤٧م)](instruments/19_A2_16_muqim_al_yazdi_1647/README.md) | Astrolabe of Muhammad Muqim al-Yazdi (1647) | 18 |
| 20 | 109 | `A2.32` | [أسطرلاب عثماني (١٠٩١هـ/١٦٨٠م)](instruments/20_A2_32_ottoman_1680/README.md) | An Ottoman astrolabe (1680) | 17 |
| 21 | 110 | `A2.20` | [أسطرلاب فارسي (١١١٨هـ/١٧٠٦م) - ملك المعهد](instruments/21_A2_20_persian_1706/README.md) | Persian astrolabe (1706) | 14 |
| 22 | 111 | `A2.08` | [أسطرلاب إسباني قوطي (ق ١٤م)](instruments/22_A2_08_spanish_gothic/README.md) | Spanish-Gothic astrolabe, 14th c. | 15 |
| 23 | 112 | `A2.09` | [أسطرلاب أوروبي (نحو ١٥٠٠م)](instruments/23_A2_09_european_1500/README.md) | European astrolabe, ca. 1500 | 11 |
| 24 | 113 | `A2.10` | [أسطرلاب على طراز ورشة جوالتروس أرسينيوس (نحو ١٥٧٠م)](instruments/24_A2_10_gualterus_arsenius/README.md) | Astrolabe after Gualterus Arsenius, ca. 1570 | 19 |
| 25 | 114 | `A2.04` | [أسطرلاب على طراز إراسموس هابرمل (نحو ١٦٠٠م) - أم باثني عشر ضلعاً](instruments/25_A2_04_erasmus_habermel/README.md) | Astrolabe after Erasmus Habermel, ca. 1600 | 19 |
| 26 | 115 | `A2.19` | [أسطرلاب تعليمي (م. برونولد)](instruments/26_A2_19_brunold_didactic/README.md) | Didactic astrolabe (M. Brunold) | 16 |
| 27 | 116 | `A2.03` | [الصفيحة الزرقالية لمحمد بن هذيل - مرسية (٦٥٠هـ/١٢٥٢م)](instruments/27_A2_03_saphea_ibn_hudhail/README.md) | Universal disc of Ibn Hudhail, Murcia 1252 | 7 |
| 28 | 117 | `A2.34` | [الصفيحة الشكازية لمحمد بن فتوح الخمائري - إشبيلية (٦١٣هـ/١٢١٦م)](instruments/28_A2_34_saphea_al_khamairi/README.md) | Universal disc of al-Khamairi, Seville 1216 | 7 |
| 29 | 118 | `A2.02` | [الصفيحة الزرقالية حسب كتب المعرفة الفلكية لألفونسو العاشر](instruments/29_A2_02_saphea_libros_del_saber/README.md) | Universal disc after the Libros del saber | 7 |
| 30 | 119 | `A2.01` | [الأسطرلاب الشامل لابن السراج (ت ٧٢٩هـ/١٣٢٩م)](instruments/30_A2_01_ibn_as_sarraj_universal/README.md) | Universal astrolabe of Ibn as-Sarraj | 17 |
| 31 | 123 | `A1.08` | [الأسطرلاب الكري للنيريزي](instruments/31_A1_08_spherical_an_nairizi/README.md) | Spherical astrolabe of an-Nairizi | 10 |
| 32 | 125 | `A1.09` | [الأسطرلاب الكري للبيروني](instruments/32_A1_09_spherical_al_biruni/README.md) | Spherical astrolabe of al-Biruni | 11 |
| 33 | 127 | `A1.10` | [الأسطرلاب الكري للمراكشي](instruments/33_A1_10_spherical_al_marrakushi/README.md) | Spherical astrolabe of al-Marrakushi | 11 |
| 34 | 129 | `A1.11` | [الأسطرلاب الكري حسب كتب المعرفة الفلكية](instruments/34_A1_11_spherical_libros_del_saber/README.md) | Spherical astrolabe after the Libros del saber | 11 |
| 35 | 131 | `A1.12` | [أسطرلاب كري عربي (٨٨٥هـ/١٤٨٠م) صنعة موسى](instruments/35_A1_12_spherical_musa_1480/README.md) | Spherical astrolabe made by Musa, 1480 | 12 |
| 36 | 133 | `A1.13` | [أسطرلاب كري (١٠٧٠هـ/١٦٦٠م) على حامل](instruments/36_A1_13_spherical_1660_stand/README.md) | Spherical astrolabe of 1660 on a stand | 12 |
| 37 | 134 | `A1.14` | [الأسطرلاب الخطي (عصا الطوسي)](instruments/37_A1_14_linear_astrolabe_tusi/README.md) | The linear astrolabe (staff of at-Tusi) | 3 |
| 38 | 136 | `A3.03` | [ربع المزي (٧٣٤هـ/١٣٣٤م)](instruments/38_A3_03_quadrant_al_mizzi/README.md) | Quadrant of al-Mizzi (734/1334) | 4 |
| 39 | 137 | `A3.04` | [ربع الجيب لعلي بن الشهاب - دمشق (٧٣٥هـ/١٣٣٥م)](instruments/39_A3_04_sine_quadrant_damascus_1335/README.md) | Sine quadrant, Damascus 1335 | 4 |
| 40 | 138 | `A3.09` | [ربع الجيب الستيني من المغرب](instruments/40_A3_09_sexagesimal_quadrant_maghrib/README.md) | Sexagesimal sine quadrant from the Maghrib | 3 |
| 41 | 139 | `A3.07` | [الربع الشكازي المزدوج للماريديني](instruments/41_A3_07_shakkaziya_double_quadrant/README.md) | Shakkaziya double quadrant of al-Maridini | 5 |
| 42 | 140 | `A3.01` | [الربع المزدوج (نسخة أوروبية ق ١٥م)](instruments/42_A3_01_double_quadrant_latin/README.md) | Double quadrant (European, 15th c.) | 5 |
| 43 | 141 | `A3.02` | [الميتيوروسكوب لبيتر أبيان](instruments/43_A3_02_meteoroscope_apian/README.md) | Meteoroscope by Peter Apian | 5 |
| 44 | 142 | `A3.10` | [دائرة الدستور لعلي بن إبراهيم المطعم (٧٣٤هـ/١٣٣٤م)](instruments/44_A3_10_dastur_quadrant/README.md) | Dastur quadrant (734/1334) | 6 |
| 45 | 143 | `A3.11` | [قرص الأرباع المغربي](instruments/45_A3_11_quadrant_disc_maghrib/README.md) | Quadrant disc from the Maghrib | 6 |
| 46 | 144 | `A3.05` | [ربع أوروبي (ق ١٨م)](instruments/46_A3_05_european_quadrant_18c/README.md) | European quadrant, 18th c. | 3 |
| 47 | 145 | `A4.25` | [الدائرة الهندية](instruments/47_A4_25_indian_circle/README.md) | Indian circle | 2 |
| 48 | 146 | `A4.21` | [آلة استخراج خط نصف النهار لابن الهيثم](instruments/48_A4_21_ibn_al_haitham_meridian/README.md) | Instrument for determining the meridian (Ibn al-Haitham) | 7 |
| 49 | 147 | `A4.24` | [الآلة ذات المثلث للخازني](instruments/49_A4_24_khazini_triangle/README.md) | The instrument with the triangle (al-Khazini) | 4 |
| 50 | 148 | `A4.33` | [آلة قياس الارتفاع الأولى (السموأل المغربي)](instruments/50_A4_33_altitude_instrument_1/README.md) | Instrument for measuring altitudes no. 1 | 4 |
| 51 | 149 | `A4.34` | [آلة قياس الارتفاع الثانية](instruments/51_A4_34_altitude_instrument_2/README.md) | Instrument for measuring altitudes no. 2 | 5 |
| 52 | 150 | `A4.35` | [آلة قياس الارتفاع الثالثة](instruments/52_A4_35_altitude_instrument_3/README.md) | Instrument for measuring altitudes no. 3 | 5 |
## إعادة التوليد أو التعديل
المولّد البرمجي موجود في `tools/astro/` (بايثون):
```
pip install numpy shapely ezdxf fonttools uharfbuzz cairosvg pypdf pillow
python3 tools/astro/build.py --book /path/Volume2EN.pdf            # كل الآلات
python3 tools/astro/build.py --only A2.14,A3.03 --book /path/Volume2EN.pdf
```
- `tools/astro/catalog.py`: بيانات كل آلة (القطر، والعروض، وعدد الكواكب، وتصميم الظهر، والسنة...). عدّل القيم هنا ثم أعد التوليد.
- `tools/astro/geom.py`: الحساب الفلكي والإسقاط.
- `tools/astro/astrolabe.py` و`others.py`: القطع.
- الخط المستعمل في الحفر: Amiri (رخصة OFL) في `tools/fonts/`.

## ملاحظات
- الزخارف الحرة (عناكب الصور والملاك والأشرطة المتشابكة، والكتابات المزخرفة الطويلة) رُسمت بتصميم هندسي مبسط يحافظ على مواضع الكواكب الصحيحة. صفحة الكتاب المرفقة في `reference/` تفيد في إضافة الزخرف يدوياً.
- الأسطرلاب `A2.30` يذكر الكتاب قطره ٧٣ مم، وهذا صغير على الأرجح. وفي `A3.10` يذكر الكتاب «نصف قطر ١٨ سم» بينما قطر الأصل ١٨٢ مم، فاعتمدنا ١٨٢ مم. ولأن كل الملفات نسبية، يكفي تكبيرها بنسبة واحدة.
