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

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;600;700&display=swap" rel="stylesheet">
<title>{{CITY}} رمضان 2027 ٹائم ٹیبل | {{SITE_NAME}}</title>
<meta name="description" content="{{CITY}} کا رمضان 2027 (1448 ہجری) مکمل ٹائم ٹیبل: سحری اور افطار کے اوقات۔ طریقہ: یونیورسٹی آف اسلامک سائنسز، کراچی (حنفی)۔">
<style>
body{font-family:'Noto Nastaliq Urdu',serif;max-width:800px;margin:0 auto;padding:16px;line-height:2.1;color:#222}
table{width:100%;border-collapse:collapse;margin-top:12px}
th,td{border:1px solid #ddd;padding:8px;text-align:left}
th{background:#f0f0f0}
a{color:#0b5cad}small{color:#555}
</style>
</head>
<body>
<p><a href="../index.html">→ واپس ہوم</a></p>
<h1>{{CITY}} — رمضان 2027 ٹائم ٹیبل</h1>
<p>سحری فجر کے وقت ختم ہوتی ہے، افطار مغرب کے وقت ہوتا ہے۔</p>
<table>
<tr><th>روزہ</th><th>تاریخ</th><th>سحری</th><th>افطار</th></tr>
{{ROWS}}
</table>
<p><small>طریقہ: یونیورسٹی آف اسلامک سائنسز، کراچی (18 ڈگری)، حنفی۔ ٹائم ٹیبل کیلکولیٹڈ ہے — رویتِ ہلال کے اعلان کے مطابق 1 دن کا فرق ممکن ہے، اپنی مقامی مسجد سے تصدیق کر لیں۔</small></p>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>رمضان 2027 ٹائم ٹیبل پاکستان | {{SITE_NAME}}</title>
<style>
body{font-family:'Noto Nastaliq Urdu',serif;max-width:800px;margin:0 auto;padding:16px;line-height:2.1;color:#222}
a{color:#0b5cad}
</style>
</head>
<body>
<p><a href="../index.html">&larr; Wapas Home</a></p>
<h1>رمضان 2027 ٹائم ٹیبل — پاکستان</h1>
<p>اپنا شہر منتخب کریں — ہر شہر کا پورا 30 دن کا سحری/افطار ٹائم ٹیبل:</p>
<p><a href="../ramadan.html">رمضان 2027 جائزہ (تاریخیں، چاند رات، لیلۃ القدر) ←</a></p>
<ul>
{{LINKS}}
</ul>
</body>
</html>
"""


def main():
    config = load_json(os.path.join(ROOT, "config.json"))
    cities = load_json(os.path.join(ROOT, "cities.json"))
    site_name = config.get("site_name", "Pakistan Islam Portal")
    out_dir = os.path.join(ROOT, "docs", "ramadan")
    os.makedirs(out_dir, exist_ok=True)

    links = []
    for city in cities:
        days = []
        for month in (2, 3):
            # CITY_COORDS wale 7 shehron ke liye calendarByCity dummy data
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
        for i, d in enumerate(days, 1):
            t = d["timings"]
            rows.append("<tr><td>" + str(i) + "</td><td>"
                        + d["date"]["gregorian"]["date"] + "</td><td>"
                        + clean_time(t.get("Fajr", "")) + "</td><td>"
                        + clean_time(t.get("Maghrib", "")) + "</td></tr>")
        page = (PAGE_TEMPLATE.replace("{{CITY}}", city.get("name_ur", city["name"]))
                .replace("{{SITE_NAME}}", site_name)
                .replace("{{ROWS}}", "\n".join(rows)))
        with open(os.path.join(out_dir, city["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        links.append('<li><a href="' + city["slug"] + '.html">'
                     + city.get("name_ur", city["name"]) + " رمضان ٹائم ٹیبل</a></li>")
        print(city["name"] + ": " + str(len(days)) + " rozay mile.")

    index = (INDEX_TEMPLATE.replace("{{SITE_NAME}}", site_name)
             .replace("{{LINKS}}", "\n".join(links)))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print("Ramadan timetables tayyar: " + str(len(links)) + " sheher.")


if __name__ == "__main__":
    main()
