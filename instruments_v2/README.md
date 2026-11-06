# النسخة الثانية — رسومات تنفيذية دقيقة (الصفحات ٧٩–١٥٠)

هذه **نسخة جديدة** مستقلة. النسخة الأولى باقية كما هي في `instruments/` و`tools/astro/`.

## ما الجديد في النسخة الثانية
1. **خطوط دقيقة تماماً بلا تعرج**: كل الدوائر والأقواس في ملفات PDF والصور مرسومة دوائرَ وأقواساً حقيقية، وأُلغي أسلوب الرسم اليدوي. وفي ملفات CNC صار محيط القص نفسه أقواساً ودوائر حقيقية (ARC/CIRCLE) بعد أن كان مضلعات.
2. **الوجه والظهر متطابقان في القص**: كل قطعة لها وجهان (الأم، كل صفيحة، جسم الربع، الصفيحة الزرقالية…) يستعمل وجهاها **نفس خط القص حرفياً**. ولكل قطعة منها ملف إضافي `<القطعة>__CUT_ONLY.dxf` فيه خط القص وحده.
   - طريقة العمل في الورشة: قصّ مرة واحدة بملف `__CUT_ONLY`، ثم احفر الوجه الأول، ثم اقلب القطعة حول محورها الرأسي (والربع حول قطره) واحفر الوجه الثاني. الثقوب والمحيط ينطبقان تماماً.
3. **الزخارف من صور الكتاب**:
   - **الكرسي (العروة المزخرفة) لكل الآلات ذات الكرسي (٣٣ آلة)** منقول بالتتبع الآلي من صورة الآلة في الكتاب: تصحيح المنظور بمطابقة إطار الأم بقطع ناقص وتحويله إلى دائرة، ثم فصل المعدن عن الخلفية، ثم قص الحلقة والعروة، ثم التناظر حول المحور. بعدها يُكبَّر إلى قطر النموذج بالضبط مع فتحاته المفرغة.
   - **عنكبوت حماة الفضي ذو الصور (A2.17)** منقول بالتتبع من الصورة بفصل لون الفضة عن النحاس.
   - **صفحتا مطابقة** في آخر ملف PDF لكل آلة لها صورة: صورة الكتاب مصححة ومكبرة إلى مقاس النموذج، وفوقها خط القص الأحمر. ومعهما ملفان `cnc/photo_overlay_front.svg` و`photo_overlay_back.svg` لتتبع أي تفصيل إضافي في Inkscape على المقاس الحقيقي.
4. **أُضيفت آلة كانت ناقصة**: أسطرلاب أحمد بن محمد النقاش، سرقسطة ١٠٧٩م (A2.13، صفحة ٩٦). صار المجموع **٥٣ آلة**.

## حدود يجب معرفتها
- العناكب الذهبية فوق صفائح ذهبية لا يمكن فصلها آلياً من الصور بدقة الكتاب (نحو ٥٠٠ بكسل للآلة)، لذلك بقيت العناكب حسابية: مواضع الكواكب دقيقة لسنة الصنع، والزخرف هندسي. أما زخرف الأصل فظاهر في صفحة المطابقة وفي ملف `photo_overlay_front.svg` لمن أراد تتبعه يدوياً على المقاس الحقيقي.
- دقة الكرسي المنقول محدودة بدقة صورة الكتاب: نحو ٠٫٣–٠٫٥ مم في آلة قطرها ١٥٠ مم. الشكل العام والفتحات مطابقة، والنقش الدقيق على سطح الكرسي غير منقول.

## إعادة التوليد
```
pip install numpy shapely ezdxf fonttools uharfbuzz cairosvg pypdf pillow opencv-python-headless
python3 tools/astro_v2/trace_all.py /path/Volume2EN.pdf     # تتبع الصور (مرة واحدة)
python3 tools/astro_v2/build.py --book /path/Volume2EN.pdf  # يكتب في instruments_v2/
```
- نتائج التتبع محفوظة في `tools/astro_v2/traced/*.json`، فيمكن إعادة التوليد بدون الكتاب. أما صفحات المطابقة فتحتاج الكتاب.
- لكل آلة ارتفاع قص الكرسي والصورة المستعملة في `tools/astro_v2/photos.py`.

## فهرس الآلات (النسخة الثانية)

| # | صفحة الكتاب | الجرد | الآلة | English | ملفات CNC |
|---|---|---|---|---|---|
| 1 | 86 | `A2.25` | [أسطرلاب نسطولس (٣١٥هـ/٩٢٧م)](01_A2_25_nastulus_kuwait/README.md) | Astrolabe of Nastulus (315/927) | 12 |
| 2 | 87 | `A2.26` | [الأسطرلاب الثاني لنسطولس (الأم فقط)](02_A2_26_nastulus_cairo_mater/README.md) | The second astrolabe of Nastulus (mater only) | 7 |
| 3 | 88 | `A2.27` | [أسطرلاب حامد بن علي الواسطي](03_A2_27_hamid_al_wasiti/README.md) | The astrolabe of Hamid b. Ali al-Wasiti | 12 |
| 4 | 89 | `A2.14` | [أسطرلاب أحمد بن خلف (نحو ٣٤٠هـ/٩٥٠م)](04_A2_14_ahmad_b_khalaf/README.md) | Astrolabe of Ahmad b. Khalaf (ca. 340/950) | 18 |
| 5 | 90 | `A2.28` | [أسطرلاب الخجندي (٣٧٤هـ/٩٨٤م)](05_A2_28_al_khujandi/README.md) | The astrolabe of al-Khujandi (374/984) | 17 |
| 6 | 91 | `A2.18` | [الأسطرلاب الكتالوني (ق ١٠م) - أقدم أسطرلاب لاتيني](06_A2_18_carolingian_catalan/README.md) | Catalan ("Carolingian") astrolabe, 10th c. | 14 |
| 7 | 92 | `A2.29` | [أسطرلاب لوبيتوس البرشلوني (Sententiae astrolabii)](07_A2_29_lupitus_barcelona/README.md) | Astrolabe after Lupitus of Barcelona | 14 |
| 8 | 94 | `A2.11` | [الأسطرلاب المنسوب للبابا سلفستر الثاني (٣٨٠هـ/٩٩٠م)](08_A2_11_sylvester_ii/README.md) | Astrolabe attributed to Pope Sylvester II | 14 |
| 9 | 95 | `A2.12` | [أسطرلاب محمد بن الصفار - طليطلة (٤٢٠هـ/١٠٢٩م)](09_A2_12_ibn_as_saffar_toledo/README.md) | Astrolabe of Muhammad b. as-Saffar, Toledo 1029 | 26 |
| 10 | 96 | `A2.13` | [أسطرلاب أحمد بن محمد النقاش - سرقسطة (٤٧٢هـ/١٠٧٩م)](10_A2_13_an_naqqash_zaragoza/README.md) | Astrolabe of Ahmad b. Muhammad an-Naqqash, Zaragoza 1079 | 20 |
| 11 | 97 | `A2.05` | [أسطرلاب إبراهيم بن سعيد السهلي - بلنسية (٤٧٨هـ/١٠٨٦م)](11_A2_05_ibrahim_b_said_valencia/README.md) | Astrolabe of Ibrahim b. Said as-Sahli, Valencia 1086 | 26 |
| 12 | 98 | `A2.30` | [أسطرلاب محمد بن الفتوح الخمائري - إشبيلية (٦١٣هـ/١٢١٦م) بصفيحة باريس](12_A2_30_al_khamairi_1216_paris/README.md) | Astrolabe of al-Khamairi, Seville 1216 (Paris plate) | 19 |
| 13 | 100 | `A2.31` | [أسطرلاب الخمائري (٦٢٦هـ/١٢٢٨م) بالتقويم الإسلامي والمسيحي](13_A2_31_al_khamairi_1228/README.md) | Astrolabe of al-Khamairi 1228 with calendars | 20 |
| 14 | 101 | `A2.24` | [أسطرلاب متحف البحرية بإسطنبول (٦١٩هـ/١٢٢٢م) - قطر ٥٦ سم](14_A2_24_marine_museum_istanbul/README.md) | Astrolabe of the Marine Museum, Istanbul (619/1222) | 14 |
| 15 | 103 | `A2.15` | [أسطرلاب عبد الكريم المصري (٦٥٠هـ/١٢٥٢م)](15_A2_15_abdalkarim_al_misri/README.md) | Astrolabe of Abdalkarim al-Misri (650/1252) | 16 |
| 16 | 104 | `A2.17` | [أسطرلاب حماة (٦٩٨هـ/١٢٩٩م) - أسطرلاب ريجيومونتانوس](16_A2_17_hama_regiomontanus/README.md) | Astrolabe from Hama 1299 (Regiomontanus) | 18 |
| 17 | 105 | `A2.07` | [أسطرلاب الملك الأشرف عمر بن يوسف - اليمن (٦٩٠هـ/١٢٩١م)](17_A2_07_al_ashraf_yemen/README.md) | Astrolabe of al-Malik al-Ashraf, Yemen 1291 | 18 |
| 18 | 106 | `A2.06` | [أسطرلاب عربي (ق ٧هـ/١٣م) - المتحف البريطاني](18_A2_06_british_museum_13c/README.md) | Arabic astrolabe, 13th c. (British Museum) | 16 |
| 19 | 107 | `A2.33` | [أسطرلاب شمس الدين محمد صفار (٨٨٤هـ/١٤٧٧م)](19_A2_33_muhammad_saffar_1477/README.md) | Astrolabe of Shamsaddin Muhammad Saffar (1477) | 13 |
| 20 | 108 | `A2.16` | [أسطرلاب محمد مقيم اليزدي للشاه عباس الثاني (١٠٥٧هـ/١٦٤٧م)](20_A2_16_muqim_al_yazdi_1647/README.md) | Astrolabe of Muhammad Muqim al-Yazdi (1647) | 18 |
| 21 | 109 | `A2.32` | [أسطرلاب عثماني (١٠٩١هـ/١٦٨٠م)](21_A2_32_ottoman_1680/README.md) | An Ottoman astrolabe (1680) | 17 |
| 22 | 110 | `A2.20` | [أسطرلاب فارسي (١١١٨هـ/١٧٠٦م) - ملك المعهد](22_A2_20_persian_1706/README.md) | Persian astrolabe (1706) | 14 |
| 23 | 111 | `A2.08` | [أسطرلاب إسباني قوطي (ق ١٤م)](23_A2_08_spanish_gothic/README.md) | Spanish-Gothic astrolabe, 14th c. | 15 |
| 24 | 112 | `A2.09` | [أسطرلاب أوروبي (نحو ١٥٠٠م)](24_A2_09_european_1500/README.md) | European astrolabe, ca. 1500 | 11 |
| 25 | 113 | `A2.10` | [أسطرلاب على طراز ورشة جوالتروس أرسينيوس (نحو ١٥٧٠م)](25_A2_10_gualterus_arsenius/README.md) | Astrolabe after Gualterus Arsenius, ca. 1570 | 19 |
| 26 | 114 | `A2.04` | [أسطرلاب على طراز إراسموس هابرمل (نحو ١٦٠٠م) - أم باثني عشر ضلعاً](26_A2_04_erasmus_habermel/README.md) | Astrolabe after Erasmus Habermel, ca. 1600 | 19 |
| 27 | 115 | `A2.19` | [أسطرلاب تعليمي (م. برونولد)](27_A2_19_brunold_didactic/README.md) | Didactic astrolabe (M. Brunold) | 16 |
| 28 | 116 | `A2.03` | [الصفيحة الزرقالية لمحمد بن هذيل - مرسية (٦٥٠هـ/١٢٥٢م)](28_A2_03_saphea_ibn_hudhail/README.md) | Universal disc of Ibn Hudhail, Murcia 1252 | 7 |
| 29 | 117 | `A2.34` | [الصفيحة الشكازية لمحمد بن فتوح الخمائري - إشبيلية (٦١٣هـ/١٢١٦م)](29_A2_34_saphea_al_khamairi/README.md) | Universal disc of al-Khamairi, Seville 1216 | 7 |
| 30 | 118 | `A2.02` | [الصفيحة الزرقالية حسب كتب المعرفة الفلكية لألفونسو العاشر](30_A2_02_saphea_libros_del_saber/README.md) | Universal disc after the Libros del saber | 7 |
| 31 | 119 | `A2.01` | [الأسطرلاب الشامل لابن السراج (ت ٧٢٩هـ/١٣٢٩م)](31_A2_01_ibn_as_sarraj_universal/README.md) | Universal astrolabe of Ibn as-Sarraj | 17 |
| 32 | 123 | `A1.08` | [الأسطرلاب الكري للنيريزي](32_A1_08_spherical_an_nairizi/README.md) | Spherical astrolabe of an-Nairizi | 10 |
| 33 | 125 | `A1.09` | [الأسطرلاب الكري للبيروني](33_A1_09_spherical_al_biruni/README.md) | Spherical astrolabe of al-Biruni | 11 |
| 34 | 127 | `A1.10` | [الأسطرلاب الكري للمراكشي](34_A1_10_spherical_al_marrakushi/README.md) | Spherical astrolabe of al-Marrakushi | 11 |
| 35 | 129 | `A1.11` | [الأسطرلاب الكري حسب كتب المعرفة الفلكية](35_A1_11_spherical_libros_del_saber/README.md) | Spherical astrolabe after the Libros del saber | 11 |
| 36 | 131 | `A1.12` | [أسطرلاب كري عربي (٨٨٥هـ/١٤٨٠م) صنعة موسى](36_A1_12_spherical_musa_1480/README.md) | Spherical astrolabe made by Musa, 1480 | 12 |
| 37 | 133 | `A1.13` | [أسطرلاب كري (١٠٧٠هـ/١٦٦٠م) على حامل](37_A1_13_spherical_1660_stand/README.md) | Spherical astrolabe of 1660 on a stand | 12 |
| 38 | 134 | `A1.14` | [الأسطرلاب الخطي (عصا الطوسي)](38_A1_14_linear_astrolabe_tusi/README.md) | The linear astrolabe (staff of at-Tusi) | 3 |
| 39 | 136 | `A3.03` | [ربع المزي (٧٣٤هـ/١٣٣٤م)](39_A3_03_quadrant_al_mizzi/README.md) | Quadrant of al-Mizzi (734/1334) | 4 |
| 40 | 137 | `A3.04` | [ربع الجيب لعلي بن الشهاب - دمشق (٧٣٥هـ/١٣٣٥م)](40_A3_04_sine_quadrant_damascus_1335/README.md) | Sine quadrant, Damascus 1335 | 4 |
| 41 | 138 | `A3.09` | [ربع الجيب الستيني من المغرب](41_A3_09_sexagesimal_quadrant_maghrib/README.md) | Sexagesimal sine quadrant from the Maghrib | 3 |
| 42 | 139 | `A3.07` | [الربع الشكازي المزدوج للماريديني](42_A3_07_shakkaziya_double_quadrant/README.md) | Shakkaziya double quadrant of al-Maridini | 5 |
| 43 | 140 | `A3.01` | [الربع المزدوج (نسخة أوروبية ق ١٥م)](43_A3_01_double_quadrant_latin/README.md) | Double quadrant (European, 15th c.) | 5 |
| 44 | 141 | `A3.02` | [الميتيوروسكوب لبيتر أبيان](44_A3_02_meteoroscope_apian/README.md) | Meteoroscope by Peter Apian | 5 |
| 45 | 142 | `A3.10` | [دائرة الدستور لعلي بن إبراهيم المطعم (٧٣٤هـ/١٣٣٤م)](45_A3_10_dastur_quadrant/README.md) | Dastur quadrant (734/1334) | 6 |
| 46 | 143 | `A3.11` | [قرص الأرباع المغربي](46_A3_11_quadrant_disc_maghrib/README.md) | Quadrant disc from the Maghrib | 6 |
| 47 | 144 | `A3.05` | [ربع أوروبي (ق ١٨م)](47_A3_05_european_quadrant_18c/README.md) | European quadrant, 18th c. | 3 |
| 48 | 145 | `A4.25` | [الدائرة الهندية](48_A4_25_indian_circle/README.md) | Indian circle | 2 |
| 49 | 146 | `A4.21` | [آلة استخراج خط نصف النهار لابن الهيثم](49_A4_21_ibn_al_haitham_meridian/README.md) | Instrument for determining the meridian (Ibn al-Haitham) | 7 |
| 50 | 147 | `A4.24` | [الآلة ذات المثلث للخازني](50_A4_24_khazini_triangle/README.md) | The instrument with the triangle (al-Khazini) | 4 |
| 51 | 148 | `A4.33` | [آلة قياس الارتفاع الأولى (السموأل المغربي)](51_A4_33_altitude_instrument_1/README.md) | Instrument for measuring altitudes no. 1 | 4 |
| 52 | 149 | `A4.34` | [آلة قياس الارتفاع الثانية](52_A4_34_altitude_instrument_2/README.md) | Instrument for measuring altitudes no. 2 | 5 |
| 53 | 150 | `A4.35` | [آلة قياس الارتفاع الثالثة](53_A4_35_altitude_instrument_3/README.md) | Instrument for measuring altitudes no. 3 | 5 |
