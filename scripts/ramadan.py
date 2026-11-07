#!/usr/bin/env python3
"""Ramadan timetable generator (ek dafa chalane wala script).

Ramadan 1448 (Feb-Mar 2027 mutawaqqa) ke liye har sheher ka poora mahine ka
timetable banata hai: roza number, Gregorian date, sehri (Fajr) aur iftar (Maghrib).

Chalane ka tareeqa (Nov-Dec 2026 me, Ramadan se pehle):
  python3 scripts/ramadan.py
Phir docs/ramadan/ wali files ko push kar den. Ye script rozana wale
update.py se alag hai — is ko roz chalane ki zaroorat nahi.

Script Feb aur Mar 2027 dono mahinon ka calendar le kar un dinon ko chunta hai
jin ki Hijri month 9 (Ramadan) aur Hijri year 1448 ho, is liye tareekhen
khud bakhud durust nikalti hain. Ruet-e-Hilal ke elaan ke baad agar farq ho
to config.json me hijri_date_override se date theek karen aur timetable
dobara generate karen.
"""

import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update import PKT, CITY_COORDS, clean_time, fetch_json, load_json  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHARED_CSS = """
.lang-toggle{display:inline-flex;align-items:center;gap:7px;background:linear-gradient(135deg,#0a4d3a,#0f6f4f);color:#fff !important;border-radius:100px;padding:6px 16px;font-weight:800;font-size:.9rem;line-height:1.9;text-decoration:none;white-space:nowrap;box-shadow:0 6px 16px rgba(10,77,58,.30);position:relative;overflow:hidden;transition:transform .35s cubic-bezier(.34,1.56,.64,1),box-shadow .35s ease}.lang-toggle:hover{transform:translateY(-2px) scale(1.04);box-shadow:0 12px 24px rgba(10,77,58,.38)}.lang-toggle:active{transform:scale(.96)}.lang-toggle::after{content:"";position:absolute;top:0;left:-90%;width:45%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.45),transparent);transform:skewX(-20deg);transition:left .65s ease}.lang-toggle:hover::after{left:140%}.lang-toggle .arr{display:inline-block;transition:transform .35s ease}.lang-toggle:hover .arr{transform:translateX(4px)}
*{box-sizing:border-box}
body{font-family:'Noto Nastaliq Urdu',serif;margin:0;background:#f6f3ea;color:#22302a;line-height:2.1}
.wrap{max-width:880px;margin:0 auto;padding:18px 16px 34px}
nav{display:flex;justify-content:space-between;align-items:center;gap:10px;background:#fff;border:1px solid #e7e1cf;border-radius:100px;padding:8px 18px;box-shadow:0 10px 26px rgba(10,77,58,.10);flex-wrap:wrap}
nav .brand{color:#0a4d3a;text-decoration:none;font-weight:700}
nav .links a{color:#0a4d3a;text-decoration:none;margin:0 7px;font-size:.92rem}
.hero{background:linear-gradient(135deg,#0a4d3a,#0d6a4f);color:#fff;border-radius:26px;padding:26px 24px;margin-top:18px;box-shadow:0 22px 44px rgba(10,77,58,.22)}
.hero h1{margin:0;font-size:1.65rem;line-height:2}
.hero p{margin:2px 0 0;color:#dcefe6}
.card{background:#fff;border:1px solid #e7e1cf;border-radius:26px;padding:22px;margin-top:18px;box-shadow:0 16px 34px rgba(10,77,58,.10)}
table{width:100%;border-collapse:collapse;margin-top:8px}
th{background:#0a4d3a;color:#fff;padding:10px 8px;font-weight:600}
td{border-bottom:1px solid #eee7d2;padding:8px;text-align:center}
tr:nth-child(even) td{background:#fbf9f1}
tr.fri td{background:#fdf3d3;font-weight:600}
.btns{margin-top:16px;display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-block;background:#0a4d3a;color:#fff;text-decoration:none;border-radius:100px;padding:6px 20px;box-shadow:0 10px 22px rgba(10,77,58,.18)}
.btn.gold{background:#b98a1e}
.note{background:#fdf8e7;border:1px solid #e9dcb2;border-radius:18px;padding:12px 18px;margin-top:18px;font-size:.94rem}
small{color:#5b6b63}
ul.cities{list-style:none;padding:0;margin:10px 0 0;columns:3;column-gap:14px}
ul.cities li{break-inside:avoid;margin:0 0 8px}
ul.cities a{display:block;background:#fbf9f1;border:1px solid #e7e1cf;border-radius:14px;padding:4px 12px;color:#0a4d3a;text-decoration:none}
@media(max-width:640px){ul.cities{columns:2}.hero h1{font-size:1.35rem}}
"""

NAV = """<nav><a class="brand" href="../index.html">☪ پاکستان اسلام پورٹل</a><span class="links"><a href="../index.html">مرکزی صفحہ</a><a href="../ramadan.html">رمضان المبارک 2027</a><a href="../surah/index.html">قرآن کریم</a><a href="../events.html">اسلامی تقریبات</a><a href="../articles/index.html">اسلامی مضامین</a></span></nav>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="alternate" hreflang="en" href="https://pakistanislam.tech/english/ramadan/{{SLUG}}.html">
<link rel="alternate" hreflang="ur" href="https://pakistanislam.tech/ramadan/{{SLUG}}.html">
<title>{{CITY}} رمضان 2027 ٹائم ٹیبل – Ramadan Calendar 2027 {{CITY_EN}}: Sehri & Iftar Timing | {{SITE_NAME}}</title>
<meta name="description" content="Ramadan calendar 2027 for {{CITY_EN}}: daily Sehri (Suhoor) and Iftar timings for all 30 fasts. {{CITY}} کا رمضان 2027 (1448 ہجری) مکمل ٹائم ٹیبل: سحری اور افطار کے اوقات۔ طریقہ: یونیورسٹی آف اسلامک سائنسز، کراچی (حنفی)۔">
<style>""" + SHARED_CSS + """</style>
</head>
<body>
<div class="wrap">
""" + NAV + """
<div class="hero">
<h1>🌙 {{CITY}} — رمضان 2027 ٹائم ٹیبل</h1>
<p>سحری فجر کے وقت ختم ہوتی ہے اور افطار مغرب کے وقت ہوتا ہے۔ سنہرے رنگ والی سطر جمعہ کے دن کی ہے۔</p>
</div>
<div class="card">
<table>
<tr><th>روزہ</th><th>تاریخ</th><th>سحری</th><th>افطار</th></tr>
{{ROWS}}
</table>
<div class="btns">
<a class="btn" href="../{{SLUG}}.html">{{CITY}} کی آج کی نماز ٹائمنگ</a>
<a class="btn gold" href="../monthly/{{SLUG}}.html">{{CITY}} کا ماہانہ ٹائم ٹیبل</a>
<a class="btn" href="index.html">تمام شہروں کے رمضان ٹائم ٹیبل</a>
<a class="btn lang-toggle" href="../english/ramadan/{{SLUG}}.html" lang="en" dir="ltr">🌐 English <span class="arr">→</span></a>
</div>
</div>
<div class="note">طریقہ: یونیورسٹی آف اسلامک سائنسز، کراچی (18 ڈگری)، حنفی۔ ٹائم ٹیبل کیلکولیٹڈ ہے — رویتِ ہلال کے اعلان کے مطابق 1 دن کا فرق ممکن ہے، اپنی مقامی مسجد سے تصدیق کر لیں۔</div>
<p style="text-align:center"><small>☪ پاکستان اسلام پورٹل — روزانہ اپ ڈیٹ ہونے والی نماز ٹائمنگ، اسلامی تاریخ اور رمضان کیلنڈر۔</small></p>
</div>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;600;700&display=swap" rel="stylesheet">
<title>رمضان 2027 ٹائم ٹیبل پاکستان – Ramadan Calendar 2027 Pakistan: Sehri & Iftar Timings | {{SITE_NAME}}</title>
<meta name="description" content="Ramadan calendar 2027 Pakistan: Sehri and Iftar timetable for every city. پاکستان کے تمام شہروں کے رمضان 2027 سحری و افطار ٹائم ٹیبل — اپنا شہر منتخب کریں۔">
<style>""" + SHARED_CSS + """</style>
</head>
<body>
<div class="wrap">
""" + NAV + """
<div class="hero">
<h1>🌙 رمضان 2027 ٹائم ٹیبل — پاکستان</h1>
<p>اپنا شہر منتخب کریں — ہر شہر کا مکمل سحری و افطار ٹائم ٹیبل (متوقع تاریخیں؛ حتمی اعلان رویتِ ہلال کمیٹی کرے گی)۔</p>
</div>
<div class="card">
<p style="margin-top:0"><a href="../ramadan.html">رمضان 2027 کا جائزہ — تاریخیں، چاند رات، لیلۃ القدر ←</a> &nbsp;·&nbsp; <a class="lang-toggle" href="../english/ramadan/" lang="en" dir="ltr">🌐 English <span class="arr">→</span></a></p>
<ul class="cities">
{{LINKS}}
</ul>
</div>
</div>
</body>
</html>
"""


EN_CSS = """
.lang-toggle{display:inline-flex;align-items:center;gap:7px;background:linear-gradient(135deg,#0a4d3a,#0f6f4f);color:#fff !important;border-radius:100px;padding:6px 16px;font-weight:800;font-size:.9rem;line-height:1.9;text-decoration:none;white-space:nowrap;box-shadow:0 6px 16px rgba(10,77,58,.30);position:relative;overflow:hidden;transition:transform .35s cubic-bezier(.34,1.56,.64,1),box-shadow .35s ease}.lang-toggle:hover{transform:translateY(-2px) scale(1.04);box-shadow:0 12px 24px rgba(10,77,58,.38)}.lang-toggle:active{transform:scale(.96)}.lang-toggle::after{content:"";position:absolute;top:0;left:-90%;width:45%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.45),transparent);transform:skewX(-20deg);transition:left .65s ease}.lang-toggle:hover::after{left:140%}.lang-toggle .arr{display:inline-block;transition:transform .35s ease}.lang-toggle:hover .arr{transform:translateX(4px)}
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;margin:0;background:#f6f3ea;color:#22302a;line-height:1.7}
.wrap{max-width:880px;margin:0 auto;padding:18px 16px 34px}
nav{display:flex;justify-content:space-between;align-items:center;gap:10px;background:#fff;border:1px solid #e7e1cf;border-radius:100px;padding:8px 18px;box-shadow:0 10px 26px rgba(10,77,58,.10);flex-wrap:wrap}
nav .brand{color:#0a4d3a;text-decoration:none;font-weight:700}
nav .links a{color:#0a4d3a;text-decoration:none;margin:0 7px;font-size:.92rem}
nav .toggle{border:1px solid #0a4d3a;border-radius:100px;padding:4px 14px;font-weight:800}
.hero{background:linear-gradient(135deg,#0a4d3a,#0d6a4f);color:#fff;border-radius:26px;padding:26px 24px;margin-top:18px;box-shadow:0 22px 44px rgba(10,77,58,.22)}
.hero h1{margin:0;font-size:1.65rem;line-height:1.3}
.hero p{margin:6px 0 0;color:#dcefe6}
.card{background:#fff;border:1px solid #e7e1cf;border-radius:26px;padding:22px;margin-top:18px;box-shadow:0 16px 34px rgba(10,77,58,.10)}
table{width:100%;border-collapse:collapse;margin-top:8px}
th{background:#0a4d3a;color:#fff;padding:10px 8px;font-weight:600}
td{border-bottom:1px solid #eee7d2;padding:8px;text-align:center}
tr:nth-child(even) td{background:#fbf9f1}
tr.fri td{background:#fdf3d3;font-weight:600}
.btns{margin-top:16px;display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-block;background:#0a4d3a;color:#fff;text-decoration:none;border-radius:100px;padding:8px 20px;box-shadow:0 10px 22px rgba(10,77,58,.18)}
.btn.gold{background:#b98a1e}
.note{background:#fdf8e7;border:1px solid #e9dcb2;border-radius:18px;padding:12px 18px;margin-top:18px;font-size:.94rem}
small{color:#5b6b63}
ul.cities{list-style:none;padding:0;margin:10px 0 0;columns:3;column-gap:14px}
ul.cities li{break-inside:avoid;margin:0 0 8px}
ul.cities a{display:block;background:#fbf9f1;border:1px solid #e7e1cf;border-radius:14px;padding:6px 12px;color:#0a4d3a;text-decoration:none}
@media(max-width:640px){ul.cities{columns:2}.hero h1{font-size:1.35rem}}
"""

EN_NAV = """<nav><a class="brand" href="/english/">☪ Pakistan Islam Portal</a><span class="links"><a href="/english/">Home</a><a href="/english/ramadan.html">Ramadan</a><a href="/english/surah/">Quran</a><a href="/english/hadith/">Hadith</a><a href="/english/calendar.html">Calendar</a><a href="/english/events.html">Events</a><a href="/english/articles/">Articles</a></span><a class="toggle lang-toggle" href="{{URDU_HREF}}" lang="ur" dir="ltr">🌐 اردو <span class="arr">→</span></a></nav>"""

EN_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" hreflang="en" href="https://pakistanislam.tech/english/ramadan/{{SLUG}}.html">
<link rel="alternate" hreflang="ur" href="https://pakistanislam.tech/ramadan/{{SLUG}}.html">
<title>Ramadan 2027 Timetable {{CITY_EN}} – Sehri &amp; Iftar Timings | Ramadan Calendar 2027 {{CITY_EN}}</title>
<meta name="description" content="Ramadan calendar 2027 for {{CITY_EN}}: daily Sehri (Suhoor) end and Iftar timings for all 30 fasts of Ramadan 1448. Method: University of Islamic Sciences, Karachi (Hanafi).">
<style>""" + EN_CSS + """</style>
</head>
<body>
<div class="wrap">
""" + EN_NAV + """
<div class="hero">
<h1>🌙 {{CITY_EN}} — Ramadan 2027 Timetable</h1>
<p>Sehri ends at Fajr and Iftar is at Maghrib. Rows highlighted in gold are Fridays.</p>
</div>
<div class="card">
<table>
<tr><th>Fast</th><th>Date</th><th>Sehri</th><th>Iftar</th></tr>
{{ROWS}}
</table>
<div class="btns">
<a class="btn" href="/english/{{SLUG}}.html">{{CITY_EN}} prayer times today</a>
<a class="btn gold" href="/english/monthly/{{SLUG}}.html">{{CITY_EN}} monthly timetable</a>
<a class="btn" href="/english/ramadan/">Ramadan timetables for all cities</a>
</div>
</div>
<div class="note">Method: University of Islamic Sciences, Karachi (18 degrees), Hanafi. This timetable is calculated — dates may shift by one day with the Ruet-e-Hilal moon-sighting announcement, so please confirm with your local masjid.</div>
<p style="text-align:center"><small>☪ Pakistan Islam Portal — daily prayer timings, Islamic dates and the Ramadan calendar.</small></p>
</div>
</body>
</html>
"""

EN_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" hreflang="en" href="https://pakistanislam.tech/english/ramadan/">
<link rel="alternate" hreflang="ur" href="https://pakistanislam.tech/ramadan/">
<title>Ramadan 2027 Timetable Pakistan – Sehri &amp; Iftar Timings for Every City | Ramadan Calendar 2027</title>
<meta name="description" content="Ramadan calendar 2027 Pakistan: Sehri and Iftar timetable for every city — choose your city for the full 30-day Ramadan 1448 timetable.">
<style>""" + EN_CSS + """</style>
</head>
<body>
<div class="wrap">
""" + EN_NAV + """
<div class="hero">
<h1>🌙 Ramadan 2027 Timetable — Pakistan</h1>
<p>Choose your city — the full Sehri and Iftar timetable for every city (expected dates; the final announcement is made by the Ruet-e-Hilal Committee).</p>
</div>
<div class="card">
<p style="margin-top:0"><a href="/english/ramadan.html">Ramadan 2027 overview — dates, Chand Raat, Laylatul Qadr →</a></p>
<ul class="cities">
{{LINKS}}
</ul>
</div>
</div>
</body>
</html>
"""


def main():
    config = load_json(os.path.join(ROOT, "config.json"))
    cities = load_json(os.path.join(ROOT, "cities.json"))
    site_name = config.get("site_name", "Pakistan Islam Portal")
    out_dir = os.path.join(ROOT, "docs", "ramadan")
    os.makedirs(out_dir, exist_ok=True)
    en_out_dir = os.path.join(ROOT, "docs", "english", "ramadan")
    os.makedirs(en_out_dir, exist_ok=True)

    links = []
    links_en = []
    for city in cities:
        days = []
        for month in (2, 3):
            # CITY_COORDS wale shehron ke liye calendarByCity dummy data
            # deta hai (daily timings me yehi bug fix hua tha) — un ke liye
            # lat/long wala calendar endpoint use karen.
            if city["name"] in CITY_COORDS:
                lat, lon = CITY_COORDS[city["name"]]
                url = ("https://api.aladhan.com/v1/calendar/2027/" + str(month)
                       + "?latitude=" + str(lat) + "&longitude=" + str(lon)
                       + "&method=" + str(config.get("method", 1))
                       + "&school=" + str(config.get("school", 1)))
            else:
                url = ("https://api.aladhan.com/v1/calendarByCity?city="
                       + urllib.parse.quote(city["name"])
                       + "&country=" + urllib.parse.quote(config.get("country", "Pakistan"))
                       + "&method=" + str(config.get("method", 1))
                       + "&school=" + str(config.get("school", 1))
                       + "&month=" + str(month) + "&year=2027")
            try:
                payload = fetch_json(url)
            except Exception as e:
                print("WARNING: " + city["name"] + " month " + str(month)
                      + " fail: " + str(e), file=sys.stderr)
                continue
            for d in payload["data"]:
                hij = d["date"]["hijri"]
                if hij["month"]["number"] == 9 and hij["year"] == "1448":
                    days.append(d)
        if not days:
            print("WARNING: " + city["name"] + " ke liye Ramadan ke din nahi mile.",
                  file=sys.stderr)
            continue
        rows = []
        rows_en = []
        for i, d in enumerate(days, 1):
            t = d["timings"]
            g = d["date"]["gregorian"]
            fri = ' class="fri"' if g["weekday"]["en"] == "Friday" else ""
            rows.append("<tr" + fri + "><td>" + str(i) + "</td><td>"
                        + g["date"] + "</td><td>"
                        + clean_time(t.get("Fajr", "")) + "</td><td>"
                        + clean_time(t.get("Maghrib", "")) + "</td></tr>")
            date_en = (g["weekday"]["en"][:3] + ", " + str(int(g["day"])) + " "
                       + g["month"]["en"][:3] + " " + str(g["year"]))
            rows_en.append("<tr" + fri + "><td>" + str(i) + "</td><td>"
                           + date_en + "</td><td>"
                           + clean_time(t.get("Fajr", "")) + "</td><td>"
                           + clean_time(t.get("Maghrib", "")) + "</td></tr>")
        page = (PAGE_TEMPLATE.replace("{{CITY}}", city.get("name_ur", city["name"]))
                .replace("{{CITY_EN}}", city["name"])
                .replace("{{SITE_NAME}}", site_name)
                .replace("{{SLUG}}", city["slug"])
                .replace("{{ROWS}}", "\n".join(rows)))
        with open(os.path.join(out_dir, city["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        links.append('<li><a href="' + city["slug"] + '.html">'
                     + city.get("name_ur", city["name"]) + " رمضان ٹائم ٹیبل</a></li>")
        page_en = (EN_PAGE_TEMPLATE.replace("{{URDU_HREF}}", "/ramadan/" + city["slug"] + ".html")
                   .replace("{{CITY_EN}}", city["name"])
                   .replace("{{SLUG}}", city["slug"])
                   .replace("{{ROWS}}", "\n".join(rows_en)))
        with open(os.path.join(en_out_dir, city["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page_en)
        links_en.append('<li><a href="' + city["slug"] + '.html">'
                        + city["name"] + " Ramadan timetable</a></li>")
        print(city["name"] + ": " + str(len(days)) + " rozay mile.")

    index = (INDEX_TEMPLATE.replace("{{SITE_NAME}}", site_name)
             .replace("{{LINKS}}", "\n".join(links)))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    index_en = (EN_INDEX_TEMPLATE.replace("{{URDU_HREF}}", "/ramadan/")
                .replace("{{LINKS}}", "\n".join(links_en)))
    with open(os.path.join(en_out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_en)
    print("Ramadan timetables tayyar: " + str(len(links)) + " sheher (UR + EN).")


if __name__ == "__main__":
    main()
