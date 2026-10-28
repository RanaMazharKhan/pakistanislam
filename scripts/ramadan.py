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
from update import PKT, clean_time, fetch_json, load_json  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ur">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ramadan 2027 Timetable {{CITY}} | {{SITE_NAME}}</title>
<meta name="description" content="{{CITY}} ka Ramadan 2027 (1448 Hijri) ka poora timetable: sehri aur iftar timings. Method: University of Islamic Sciences, Karachi (Hanafi).">
<style>
body{font-family:system-ui,sans-serif;max-width:800px;margin:0 auto;padding:16px;line-height:1.6;color:#222}
table{width:100%;border-collapse:collapse;margin-top:12px}
th,td{border:1px solid #ddd;padding:8px;text-align:left}
th{background:#f0f0f0}
a{color:#0b5cad}small{color:#555}
</style>
</head>
<body>
<p><a href="../index.html">&larr; Wapas Home</a></p>
<h1>{{CITY}} — Ramadan 2027 Timetable</h1>
<p>Sehri Fajr ke time par khatam hoti hai, iftar Maghrib ke time par hota hai.</p>
<table>
<tr><th>Roza</th><th>Date</th><th>Sehri</th><th>Iftar</th></tr>
{{ROWS}}
</table>
<p><small>Method: University of Islamic Sciences, Karachi (18&deg;/18&deg;), Hanafi. Timetable calculated hai — Ruet-e-Hilal ke elaan ke mutabiq 1 din ka farq mumkin hai, apni local masjid se confirm kar len.</small></p>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ur">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ramadan 2027 Timetable Pakistan | {{SITE_NAME}}</title>
<style>
body{font-family:system-ui,sans-serif;max-width:800px;margin:0 auto;padding:16px;line-height:1.6;color:#222}
a{color:#0b5cad}
</style>
</head>
<body>
<p><a href="../index.html">&larr; Wapas Home</a></p>
<h1>Ramadan 2027 Timetable — Pakistan</h1>
<p>Apna sheher chunen — har sheher ka poora 30 din ka sehri/iftar timetable:</p>
<p><a href="../ramadan.html">← Ramadan 2027 overview (dates, chand raat, Laylatul Qadr)</a></p>
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
        page = (PAGE_TEMPLATE.replace("{{CITY}}", city["name"])
                .replace("{{SITE_NAME}}", site_name)
                .replace("{{ROWS}}", "\n".join(rows)))
        with open(os.path.join(out_dir, city["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        links.append('<li><a href="' + city["slug"] + '.html">' + city["name"]
                     + " Ramadan Timetable</a></li>")
        print(city["name"] + ": " + str(len(days)) + " rozay mile.")

    index = (INDEX_TEMPLATE.replace("{{SITE_NAME}}", site_name)
             .replace("{{LINKS}}", "\n".join(links)))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print("Ramadan timetables tayyar: " + str(len(links)) + " sheher.")


if __name__ == "__main__":
    main()
