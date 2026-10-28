# SEO Plan — Pakistan Islam Portal (pakistanislam.tech)

## Zaroori caveat (pehle parh len)
Is plan ke keywords **competition aur query-shape evidence** par muntakhib hain — kisi keyword ka exact monthly
search volume verify nahi hai. Final priority se pehle inhen **Google Keyword Planner (location = Pakistan)** me
daal kar check karen aur negligible volume wale keywords ko drop kar den. Koi volume, CPC ya earning figure is
plan me verified nahi hai.

## Target keyword groups aur page mapping

### 1. Namaz timing (har sheher ka page)
- `namaz timing [city] today`, `[city] prayer times today`, `[city] namaz timing`
- `Fajr time [city]`, `Fajr time today Karachi`, `aaj ki namaz timing`
- Fiqa variants: `Fiqa Hanafi prayer time [city]`, `Fiqa Jafria [city]`, `Shia namaz timing [city]`
- Page: `docs/<city>.html` (templates/city.html se generate) — title/description me "Namaz Timing Today",
  "Fajr Time", "Sehri aur Iftar", "Hanafi aur Jafria".
- Muqabla: hamariweb, darsaal, isubqo, namaz.io, islamicfinder (bohat gehra, chhoti localities tak).
- Edge: Roman Urdu + Hanafi/Jafria aik page par + 163 shehron ki depth.

### 2. Islamic date / chand ki tarikh (home page)
- `Islamic date today in Pakistan`, `Islamic date today Pakistan`, `Hijri date today`
- `chand ki tarikh`, `aaj chand ki kya tarikh hai`, `chand ki date today`, `aaj ki Islamic date`
- `Islamic date tomorrow in Pakistan`, `Islamic calendar 2027`
- Page: home (`docs/index.html`, templates/index.html se generate).
- Muqabla: hamariweb, islamicdatetoday.pk, islamiccalendar.com.pk.
- Edge: Ruet-e-Hilal + Maghrib-rule ki wazahat (28 Oct 2026 ko competitors ne aik hi din 16, 17 aur
  18 Jumada al-Awwal dikhaye — sirf number dena kafi nahi, wazahat differentiator hai).
- Future opportunity (alag page, abhi nahi): Urdu-script queries (`آج چاند کی تاریخ`) ke liye Urdu-script
  date page — is ke liye script ka faisla user se confirm kar ke hi likha jaye.

### 3. Sehri / iftar time (city pages + Ramadan pages)
- `sehri time today [city]`, `iftar time today [city]`, `sehri iftar time [city] today`
- `Roza timing today`, `sehr o iftar timing [city]`, `sehri time [city] Fiqa Jafria`
- Spelling variants: sehri / sehar / sahar / suhoor; iftar / iftari.
- Muqabla: hamariweb, darsaal, islamuna, isubqo, iftartimetoday.com.
- Demand "today + city" shape ki hai — rozana update zaroori hai, static table nahi.

### 4. Ramadan calendar / timetable 2027 (Ramadan pages)
- `Ramadan calendar 2027 Pakistan`, `Ramadan timetable [city] 2027`
- `Ramadan 2027 [city] sehri iftar timetable`, `first sehri / first iftar Ramadan 2027 [city]`
- Page: `docs/ramadan.html` + `scripts/ramadan.py` se per-city timetables (`docs/ramadan/`).
- Muqabla: hamariweb (chhote qasbon tak), wetoolskit, darsaal, islamuna.
- Edge: Roman Urdu presentation, Hanafi + Jafria aik saath, 2027 timetables jald publish karna,
  "expected, Ruet-e-Hilal confirms" framing ke saath.

### 5. Eid aur Islamic events dates (events page)
- `Eid ul Fitr date Pakistan 2027`, `Eid ul Adha date 2027`, `Shab e Barat 2027 date Pakistan`
- `Shab e Miraj / Meraj 2027 date`, `Shab e Qadr / Laylatul Qadr 2027`, `Ashura date 2027`
- `Eid Milad un Nabi date 2027`, `chand raat date`, `Islamic holidays 2027 Pakistan`
- Page: `docs/events.html`.
- Muqabla: pakera.pk, hamariweb, isubqo, islamicinfocenter.
- Warning: sources aik din ya zyada differ karte hain (Eid-ul-Fitr 9 vs 10 Mar 2027; Shab-e-Barat
  23 vs 24 Jan) — har event date par "mutawaqqa, Ruet-e-Hilal final" likhna lazmi hai.

### 6. Surah tarjuma (Surah hub + aik-aik Surah pages)
- `Surah Yaseen / Yasin Urdu tarjuma`, `Surah Yaseen with Urdu translation`
- `Surah Rahman / Mulk / Kahf / Waqiah Urdu translation`, `Panj Surah with Urdu tarjuma`
- Page: `docs/surah/` hub + har Surah ka page (aik-aik kar ke, Quranic text me ghalti se bachne ke liye).
- Muqabla: surah-yaseen.org, faizeislam.info, surayasin.com + apps/YouTube (recitation videos).
- Edge (sab se wazeh gap): full **Roman Urdu tarjuma text pages** web par kam hain — transliteration
  milta hai, Roman Urdu tarjuma text nahi. Yahi site ka Surah differentiator hai.
- Imaandari ka usool: jo Surah ka full tarjuma abhi site par nahi, us ke page par "jald aa raha hai"
  likha rahe; title/description me full tarjuma ka dawa na kiya jaye.

## On-page usool (har page par)
- Title 60-70 characters ke qareeb, target query shuru me; description me query + sheher/date + method.
- Keyword stuffing nahi — aik page, aik main query + us ki natural variants.
- Har page par: canonical, Open Graph/Twitter cards, FAQ schema (jahan FAQ ho), internal links
  (related pages + nearby cities).
- Favicon: `/favicon.ico`, `/favicon.svg`, `/apple-touch-icon.png` (har page ke head me).

## Agle steps
1. Keyword Planner (Pakistan filter) se volumes verify karen, negligible wale drop karen.
2. `scripts/ramadan.py` chala kar per-city Ramadan 2027 timetables publish karen.
3. Surah Yaseen, Rahman, Kahf, Waqiah ka full Roman Urdu tarjuma aik-aik kar ke likhen.
4. Search Console me property verify kar ke sitemap submit karen (README me tareeqa maujood hai).
5. Rozana Daily Update action ko chalne den (namaz timings + Islamic date fresh rahen).
