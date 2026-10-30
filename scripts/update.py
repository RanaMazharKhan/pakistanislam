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


def main():
    config = load_json(os.path.join(ROOT, "config.json"))
    cities = load_json(os.path.join(ROOT, "cities.json"))
    with open(os.path.join(ROOT, "templates", "index.html"), encoding="utf-8") as f:
        index_tpl = f.read()
    with open(os.path.join(ROOT, "templates", "city.html"), encoding="utf-8") as f:
        city_tpl = f.read()

    now_pkt = datetime.now(PKT)
    tomorrow_pkt = now_pkt + timedelta(days=1)
    tomorrow_str = tomorrow_pkt.strftime("%d-%m-%Y")
    updated_at = now_pkt.strftime("%d %B %Y, %I:%M %p")
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
    ok = 0
    for idx, city in enumerate(cities):
        slug = city["slug"]
        name = city["name"]
        neighbours = cities[max(0, idx - 3):idx] + cities[idx + 1:idx + 4]
        nearby_links = "".join(
            '<a href="' + c["slug"] + '.html">' + c["name"] + "</a>"
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

        t = record["timings"]
        j = record.get("jafria", {})
        hijri_show = hijri_override if hijri_override else record["hijri_date"]
        hijri_after_show = hijri_override if hijri_override else record.get(
            "hijri_date_after_maghrib", "")
        page = render(city_tpl, {
            "SITE_NAME": site_name,
            "CITY": name,
            "CITY_SLUG": slug,
            "GREGORIAN_DATE": nice_date(record["gregorian_date"]),
            "HIJRI_DATE": hijri_show,
            "HIJRI_DATE_AFTER_MAGHRIB": hijri_after_show,
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
            "NEARBY_LINKS": nearby_links,
            "UPDATED_AT": updated_at,
        })
        with open(os.path.join(ROOT, "docs", slug + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

        rows.append('<tr data-city="' + name.lower() + '"><td>' + name + "</td><td>"
                    + t.get("Fajr", "") + "</td><td>" + t.get("Maghrib", "")
                    + "</td><td>" + j.get("Maghrib", "—") + '</td><td><a href="'
                    + slug + '.html">Timing dekhen</a></td></tr>')
        if not home_gregorian:
            home_gregorian = nice_date(record["gregorian_date"])
            home_hijri = hijri_show
            home_hijri_after = hijri_after_show
            home_maghrib = t.get("Maghrib", "")
        ok += 1

    if ok == 0:
        print("ERROR: kisi sheher ka data nahi mila, homepage update nahi hui.",
              file=sys.stderr)
        return 1

    index = render(index_tpl, {
        "SITE_NAME": site_name,
        "GREGORIAN_DATE": home_gregorian,
        "HIJRI_DATE": home_hijri,
        "HIJRI_DATE_AFTER_MAGHRIB": home_hijri_after,
        "MAGHRIB_TIME": home_maghrib,
        "CITY_TABLE_ROWS": "\n".join(rows),
        "UPDATED_AT": updated_at,
    })
    with open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8") as f:
        f.write(index)

    print("Done: " + str(ok) + "/" + str(len(cities)) + " shehron ki update hui.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
