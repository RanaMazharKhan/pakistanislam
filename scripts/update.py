#!/usr/bin/env python3
"""Daily update script v2 for the Islamic portal (premium edition).

Kaam:
  1. Har sheher ke liye Aladhan API (free) se data lata hai:
     - Hanafi timings: method 1 = University of Islamic Sciences, Karachi, school 1 = Hanafi Asr.
     - Jafria timings: method 0 = Shia Ithna-Ashari.
     - Kal ki Hijri date: taake Maghrib ke baad homepage par nayi Hijri date dikhai ja sake
       (Islamic din Maghrib se shuru hota hai — yehi woh gap hai jo aksar websites miss karti hain).
  2. docs/data/<slug>.json me save karta hai.
  3. templates/ se docs/index.html aur docs/<slug>.html banata hai.
  4. Koi sheher ya koi method fail ho jaye to purana data rehne deta hai,
     poora run fail nahi karta. Choti tehsil API par na mile to usay skip kar
     ke warning deta hai (qareebi district ka page phir bhi kaam karta hai).

Sirf Python standard library use hoti hai (koi pip install nahi).
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKT = timezone(timedelta(hours=5))

UR_MONTHS = ["جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون", "جولائی",
             "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"]
UR_WEEKDAYS = {"Monday": "پیر", "Tuesday": "منگل", "Wednesday": "بدھ",
               "Thursday": "جمعرات", "Friday": "جمعہ", "Saturday": "ہفتہ",
               "Sunday": "اتوار"}

# Kuch shehron ke liye Aladhan ka timingsByCity aik jesa dummy data deta hai
# (sab ke liye Fajr 05:01 / Maghrib 17:18, 2026-10-30 ko verify kiya) —
# un ke liye lat/long se timings li jati hain. Baqi sheher naam se theek hain.
CITY_COORDS = {
    "Gilgit": (35.9208, 74.3089),
    "Skardu": (35.2971, 75.6333),
    "Pishin": (30.5818, 66.9980),
    "Kharan": (28.5856, 65.4150),
    "Chitral": (35.8513, 71.7864),
    "Hunza": (36.3167, 74.6500),
    "Harnai": (29.8933, 67.9397),
    # Qambar Shahdadkot: calendarByCity errors on the name, same pattern
    # as the 7 above — lat/long (Qambar, Sindh) verified 2026-10-30.
    "Qambar Shahdadkot": (27.58767, 67.99885),
    "Jatoi": (29.5167, 70.85),
    "Khanpur": (28.6333, 70.2333),
    "Jahanian": (30.05, 71.8167),
    "Yazman": (29.1167, 71.7333),
    "Kharian": (32.8167, 73.85),
    "Hazro": (33.9, 72.4833),
    "Muridke": (31.8, 74.25),
    "Sambrial": (32.4833, 74.35),
    "Ahmedpur Sial": (31.6167, 72.2667),
    "Khwazakhela": (34.9333, 72.4667),
    "Pabbi": (34.0167, 71.9),
    "Jehangira": (33.9833, 72.2167),
    "Mir Ali": (32.9833, 70.2667),
    "Drosh": (35.5667, 71.7833),
    "Dassu": (35.5833, 73.6167),
    "Gambat": (27.35, 68.5167),
    "Ratodero": (27.8, 68.9333),
    "Kunri": (25.1833, 69.5667),
    "Digri": (25.1667, 69.1167),
    "Ormara": (25.2167, 64.6333),
    "Bela": (26.1833, 66.3167),
    "Dhadar": (29.1833, 67.65),
    "Nokundi": (28.8333, 62.75),
    "Sohbatpur": (28.5167, 68.4333),
    "Khaplu": (35.15, 76.3333),
    "Pallandri": (33.7167, 73.6833),
    "Athmuqam": (34.5833, 73.9167),
    "Hattian Bala": (34.1667, 73.7333),
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fetch_json(url, tries=3):
    last_err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "islamic-portal-daily-update"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(2 * (i + 1))
    raise last_err


def clean_time(t):
    # Aladhan "05:19 (PKT)" deta hai -> "05:19"
    return t.split(" ")[0] if t else ""


def clean_timings(timings):
    return {k: clean_time(v) for k, v in timings.items()}


def nice_date(dd_mm_yyyy):
    try:
        return datetime.strptime(dd_mm_yyyy, "%d-%m-%Y").strftime("%d %B %Y")
    except ValueError:
        return dd_mm_yyyy


def render(template, values):
    out = template
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", str(val))
    return out


def add_minutes(hhmm, mins):
    """'HH:MM' me minutes jod kar naya 'HH:MM' deta hai."""
    try:
        h, m = hhmm.split(":")
        total = (int(h) * 60 + int(m) + mins) % (24 * 60)
        return f"{total // 60:02d}:{total % 60:02d}"
    except Exception:
        return hhmm


def calendar_url(city, country, year, month, method, school):
    q = urllib.parse.urlencode({"city": city, "country": country,
                                "method": method, "school": school})
    return f"https://api.aladhan.com/v1/calendarByCity/{year}/{month}?" + q


def calendar_coords_url(lat, lon, year, month, method, school):
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon,
                                "method": method, "school": school})
    return f"https://api.aladhan.com/v1/calendar/{year}/{month}?" + q


def city_calendar_url(city_obj, country, year, month, method, school):
    """CITY_COORDS wale shehron ke liye calendar bhi coordinates se."""
    coords = CITY_COORDS.get(city_obj["name"])
    if coords:
        return calendar_coords_url(coords[0], coords[1], year, month, method, school)
    return calendar_url(city_obj["name"], country, year, month, method, school)


def timings_url(city, country, method, school=None, date=None):
    base = "https://api.aladhan.com/v1/timingsByCity"
    if date:
        base += "/" + date
    url = (base + "?city=" + urllib.parse.quote(city)
           + "&country=" + urllib.parse.quote(country)
           + "&method=" + str(method))
    if school is not None:
        url += "&school=" + str(school)
    return url


def coords_url(lat, lon, method, school=None, date=None):
    # Is endpoint ke liye date lazmi hai (DD-MM-YYYY); na mile to aaj ki PKT date.
    if not date:
        date = datetime.now(PKT).strftime("%d-%m-%Y")
    url = ("https://api.aladhan.com/v1/timings/" + date
           + "?latitude=" + str(lat) + "&longitude=" + str(lon)
           + "&method=" + str(method))
    if school is not None:
        url += "&school=" + str(school)
    return url


def city_url(city, country, method, school=None, date=None):
    # CITY_COORDS wale shehron ke liye lat/long, baqi ke liye sheher ke naam se.
    if city in CITY_COORDS:
        lat, lon = CITY_COORDS[city]
        return coords_url(lat, lon, method, school, date)
    return timings_url(city, country, method, school, date)


SITEMAP_BASE = "https://pakistanislam.tech/"
SITEMAP_STATIC = [
    "",
    "about.html",
    "articles/",
    "articles/islamic-date-kaise-maloom-hoti-hai.html",
    "articles/namaz-timings-kaise-nikali-jati-hain.html",
    "articles/ramadan-ki-tayyari-guide.html",
    "articles/shab-e-barat-aur-shab-e-miraj.html",
    "contact.html",
    "disclaimer.html",
    "events.html",
    "privacy-policy.html",
    "ramadan.html",
    "ramadan/",
    "surah/",
    "surah/falaq.html",
    "surah/ikhlas.html",
    "surah/mulk.html",
    "surah/naas.html",
]


def write_sitemap(done_slugs):
    # Rozana update ke saath sitemap bhi khud taaza ho jata hai.
    today = datetime.now(PKT).strftime("%Y-%m-%d")
    urls, seen = [], set()

    def add(path):
        u = SITEMAP_BASE + path
        if u not in seen:
            seen.add(u)
            urls.append(u)

    for p in SITEMAP_STATIC:
        add(p)
    for slug in done_slugs:
        add(slug + ".html")
    for slug in done_slugs:
        # Ramadan per-city page sirf tab shamil karen jab file asal me maujood ho
        if os.path.exists(os.path.join(ROOT, "docs", "ramadan", slug + ".html")):
            add("ramadan/" + slug + ".html")
    for slug in done_slugs:
        # Monthly timetable page bhi sirf tab, jab file maujood ho
        if os.path.exists(os.path.join(ROOT, "docs", "monthly", slug + ".html")):
            add("monthly/" + slug + ".html")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("<url><loc>" + u + "</loc><lastmod>" + today + "</lastmod></url>")
    lines.append("</urlset>")
    out = os.path.join(ROOT, "docs", "sitemap.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Sitemap update hua: " + str(len(urls)) + " URLs")


def write_monthly_pages(cities, config, site_name, updated_at, monthly_tpl):
    """Har sheher ka current-month timetable page docs/monthly/<slug>.html.
    Mahina badle baghair dobara generate nahi karta (marker file .month)."""
    now = datetime.now(PKT)
    tag = f"{now.year}-{now.month:02d}"
    mdir = os.path.join(ROOT, "docs", "monthly")
    os.makedirs(mdir, exist_ok=True)
    marker = os.path.join(mdir, ".month")
    if os.path.exists(marker):
        with open(marker, encoding="utf-8") as f:
            if f.read().strip() == tag:
                print("Monthly pages pehle se current hain (" + tag + ") — skip.")
                return
    method = config.get("method", 1)
    school = config.get("school_hanafi", 1)
    country = config.get("country", "Pakistan")
    month_name = UR_MONTHS[now.month - 1]
    ok = 0
    for city in cities:
        try:
            payload = fetch_json(city_calendar_url(city, country, now.year,
                                                   now.month, method, school))
            rows = []
            for day in payload["data"]:
                g, h = day["date"]["gregorian"], day["date"]["hijri"]
                tt = clean_timings(day["timings"])
                rows.append(
                    "<tr><td>" + str(g["day"]) + " " + UR_MONTHS[int(g["month"]["number"]) - 1]
                    + " (" + UR_WEEKDAYS.get(g["weekday"]["en"], "") + ")</td><td>"
                    + str(h["day"]) + " " + str(h["month"].get("ar", h["month"]["en"])) + "</td><td>"
                    + tt["Fajr"] + "</td><td>" + tt["Sunrise"] + "</td><td>"
                    + tt["Dhuhr"] + "</td><td>" + tt["Asr"] + "</td><td>"
                    + tt["Maghrib"] + "</td><td>" + tt["Isha"] + "</td></tr>")
            page = render(monthly_tpl, {
                "SITE_NAME": site_name, "CITY_UR": city.get("name_ur", city["name"]),
                "CITY_SLUG": city["slug"], "MONTH_NAME": month_name,
                "YEAR": str(now.year), "MONTH_ROWS": "\n".join(rows),
                "UPDATED_AT": updated_at})
            with open(os.path.join(mdir, city["slug"] + ".html"), "w",
                      encoding="utf-8") as f:
                f.write(page)
            ok += 1
        except Exception as e:
            print("Monthly skip:", city["name"], "-", e)
        time.sleep(0.35)
    print("Monthly pages tayyar: " + str(ok) + "/" + str(len(cities)))
    if ok >= len(cities) * 0.9:
        with open(marker, "w", encoding="utf-8") as f:
            f.write(tag)


def main():
    config = load_json(os.path.join(ROOT, "config.json"))
    cities = load_json(os.path.join(ROOT, "cities.json"))
    with open(os.path.join(ROOT, "templates", "index.html"), encoding="utf-8") as f:
        index_tpl = f.read()
    with open(os.path.join(ROOT, "templates", "city.html"), encoding="utf-8") as f:
        city_tpl = f.read()
    with open(os.path.join(ROOT, "templates", "monthly.html"), encoding="utf-8") as f:
        monthly_tpl = f.read()

    now_pkt = datetime.now(PKT)
    tomorrow_pkt = now_pkt + timedelta(days=1)
    tomorrow_str = tomorrow_pkt.strftime("%d-%m-%Y")
    updated_at = now_pkt.strftime("%d %B %Y, %I:%M %p")
    month_name = UR_MONTHS[now_pkt.month - 1]
    site_name = config.get("site_name", "Pakistan Islam Portal")
    country = config.get("country", "Pakistan")
    hijri_override = config.get("hijri_date_override", "").strip()

    data_dir = os.path.join(ROOT, "docs", "data")
    os.makedirs(data_dir, exist_ok=True)

    rows = []
    home_gregorian = ""
    home_hijri = ""
    home_hijri_after = ""
    home_maghrib = ""
    home_hijri_ur = ""
    home_hijri_after_ur = ""
    ok = 0
    done_slugs = []
    for idx, city in enumerate(cities):
        slug = city["slug"]
        name = city["name"]
        neighbours = cities[max(0, idx - 3):idx] + cities[idx + 1:idx + 4]
        nearby_links = "".join(
            '<a href="' + c["slug"] + '.html">' + c["name"] + "</a>"
            for c in neighbours)
        nearby_links_ur = "".join(
            '<a href="' + c["slug"] + '.html">' + c.get("name_ur", c["name"]) + "</a>"
            for c in neighbours)
        record = None
        try:
            payload = fetch_json(city_url(name, country, config.get("method", 1),
                                          config.get("school", 1)))
            d = payload["data"]
            hij = d["date"]["hijri"]
            record = {
                "city": name,
                "gregorian_date": d["date"]["gregorian"]["date"],
                "hijri_date": hij["day"] + " " + hij["month"]["en"] + " " + hij["year"],
                "hijri_date_ur": hij["day"] + " " + hij["month"].get("ar", hij["month"]["en"]) + " " + hij["year"] + "ھ",
                "timings": clean_timings(d["timings"]),
                "fetched_at": updated_at,
            }
            # Jafria timings (best-effort: fail ho to khaali rehne den)
            try:
                j_payload = fetch_json(city_url(name, country, 0))
                record["jafria"] = clean_timings(j_payload["data"]["timings"])
            except Exception as e:
                print("WARNING: " + name + " Jafria fail: " + str(e), file=sys.stderr)
                record["jafria"] = {}
            # Kal ki Hijri date (Maghrib rule ke liye, best-effort)
            try:
                t_payload = fetch_json(city_url(name, country, config.get("method", 1),
                                                config.get("school", 1),
                                                date=tomorrow_str))
                t_hij = t_payload["data"]["date"]["hijri"]
                record["hijri_date_after_maghrib"] = (
                    t_hij["day"] + " " + t_hij["month"]["en"] + " " + t_hij["year"])
                record["hijri_date_after_maghrib_ur"] = (
                    t_hij["day"] + " " + t_hij["month"].get("ar", t_hij["month"]["en"])
                    + " " + t_hij["year"] + "ھ")
            except Exception as e:
                print("WARNING: " + name + " kal ki date fail: " + str(e),
                      file=sys.stderr)
                record["hijri_date_after_maghrib"] = ""
            with open(os.path.join(data_dir, slug + ".json"), "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("WARNING: " + name + " fail ho gaya: " + str(e), file=sys.stderr)
            old = os.path.join(data_dir, slug + ".json")
            if not os.path.exists(old):
                continue
            record = load_json(old)
            record.setdefault("jafria", {})
            record.setdefault("hijri_date_after_maghrib", "")
            record.setdefault("hijri_date_ur", record["hijri_date"])
            record.setdefault("hijri_date_after_maghrib_ur", "")

        t = record["timings"]
        j = record.get("jafria", {})
        hijri_show = hijri_override if hijri_override else record["hijri_date"]
        hijri_after_show = hijri_override if hijri_override else record.get(
            "hijri_date_after_maghrib", "")
        hijri_ur_show = hijri_override if hijri_override else record.get(
            "hijri_date_ur", hijri_show)
        hijri_after_ur_show = hijri_override if hijri_override else record.get(
            "hijri_date_after_maghrib_ur", "")
        page = render(city_tpl, {
            "SITE_NAME": site_name,
            "CITY_UR": city.get("name_ur", name),
            "CITY_SLUG": slug,
            "GREGORIAN_DATE": nice_date(record["gregorian_date"]),
            "HIJRI_DATE": hijri_ur_show,
            "HIJRI_DATE_AFTER_MAGHRIB": hijri_after_ur_show,
            "MAGHRIB_TIME": t.get("Maghrib", ""),
            "FAJR": t.get("Fajr", ""),
            "SUNRISE": t.get("Sunrise", ""),
            "DHUHR": t.get("Dhuhr", ""),
            "ASR": t.get("Asr", ""),
            "MAGHRIB": t.get("Maghrib", ""),
            "ISHA": t.get("Isha", ""),
            "JAFRIA_FAJR": j.get("Fajr", "—"),
            "JAFRIA_MAGHRIB": j.get("Maghrib", "—"),
            "JAFRIA_ISHA": j.get("Isha", "—"),
            "ISHRAQ": add_minutes(t.get("Sunrise", ""), 20),
            "MONTH_NAME": month_name,
            "NEARBY_LINKS_UR": nearby_links_ur,
            "UPDATED_AT": updated_at,
        })
        with open(os.path.join(ROOT, "docs", slug + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        done_slugs.append(slug)

        rows.append('<tr data-city="' + city.get("name_ur", name) + " " + name.lower()
                    + '"><td>' + city.get("name_ur", name) + "</td><td>"
                    + t.get("Fajr", "") + "</td><td>" + t.get("Maghrib", "")
                    + "</td><td>" + j.get("Maghrib", "—") + '</td><td><a href="'
                    + slug + '.html">ٹائمنگ دیکھیں</a></td></tr>')
        if not home_gregorian:
            home_gregorian = nice_date(record["gregorian_date"])
            home_hijri = hijri_show
            home_hijri_after = hijri_after_show
            home_hijri_ur = hijri_ur_show
            home_hijri_after_ur = hijri_after_ur_show
            home_maghrib = t.get("Maghrib", "")
        ok += 1

    if ok == 0:
        print("ERROR: kisi sheher ka data nahi mila, homepage update nahi hui.",
              file=sys.stderr)
        return 1

    index = render(index_tpl, {
        "SITE_NAME": site_name,
        "GREGORIAN_DATE": home_gregorian,
        "HIJRI_DATE": home_hijri_ur if home_hijri_ur else home_hijri,
        "HIJRI_DATE_AFTER_MAGHRIB": home_hijri_after_ur,
        "MAGHRIB_TIME": home_maghrib,
        "CITY_TABLE_ROWS": "\n".join(rows),
        "UPDATED_AT": updated_at,
    })
    with open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8") as f:
        f.write(index)


    write_monthly_pages(cities, config, site_name, updated_at, monthly_tpl)
    write_sitemap(done_slugs)

    print("Done: " + str(ok) + "/" + str(len(cities)) + " shehron ki update hui.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
