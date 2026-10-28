# Pakistan Islam Portal — Premium Edition (v4: Asli 3D + Urdu Script Articles + Live Demo)

Roman Urdu me mukammal Islamic portal: Islamic date, namaz timings, Ramadan timetable, Surah tarjuma aur Islamic events — **premium 3D design** ke saath. **Koi server nahi, koi bill nahi** — GitHub Actions rozana data update karta hai, GitHub Pages site chalata hai.

## v4 me kya naya hai (pehle wale issues ka fix)
- **Asli 3D effect (bug fix):** pehle `float3d` animation `transform` ko animate karti thi jo rings/cubes ki 3D tilt (`rotateX`) ko override kar ke khatam kar deti thi — shapes chapte nazar aate the. Ab animation sirf `translate` property par chalti hai aur tilt mehfooz rehti hai. Plus: **6-face ghoomta hua 3D cube**, gehre rang (ring border 0.30, gold ring 0.60, cube faces 0.38), bara chand, aur nested parallax — mouse hilane par har shape apni depth se hilta hai, tilt khatam nahi hoti.
- **Home page par zyada maloomat:** Ramadan countdown (days calculator), Aane Wale Islamic Events cards, "Namaz Timings Kaise Banti Hain?" explainer, Hanafi vs Jafria farq, Maghrib Rule box, aur articles previews — home page ab lamba aur maloomat se bhara hua hai.
- **Articles ab bilkul Urdu script (Nastaliq) me:** 4 mukammal articles + articles index page — poora text Urdu script me, RTL layout, Nastaliq font. Baqi site (timings, Surah, events) Roman Urdu me hi hai, jese pehle tay tha.
- **Live demo pages (koi dash, koi toota link nahi):** sample home page aur 12 mashhoor shehron ke pages ab **live Aladhan data** se bharte hain (internet par kholte hi asli timings), aur tamam 361 internal links check kiye gaye — **koi toota link nahi**. Pehli GitHub Actions update ke baad in demo pages ki jagah rozana update hone wale template pages aa jayenge.
- **Live announcement ticker (home page):** nav bar ke neeche sabz patti chalti hai — us par announcements aur important information aati hai (Ramadan 2027 ka elaan, aaj ki Islamic date, live Pakistan time, Ramadan countdown, masjid se confirm karne ki note, naye articles ki khabar). Mouse le jane par patti ruk jati hai. Template me bhi maujood hai, is liye pehli update ke baad asli home page par bhi chalegi.
- **Static pages ka 3D fix:** Ramadan, Events, Surah aur Ramadan-index pages ki animation bhi `translate`-based kar di gayi hai taake un ki 3D tilt bhi mehfooz rahe.

## Is version me kya naya hai (doosri websites ke gaps)

| Gap (doosri websites me) | Is portal me hal |
|---|---|
| Sirf baray sheher | **163 sheher** — district headquarters + choti cities/tehsils (Skardu se Turbat, Mithi se Chitral tak) |
| Sirf ek method | **Hanafi + Jafria** timings har sheher ke page par |
| Islamic date aadhi raat ko badalti hai | **Maghrib rule**: Maghrib ke baad Hijri date khud badal jati hai (kal ki date bhi API se li jati hai) |
| Ramadan timetable sirf Ramadan me | **Ramadan 2027 pehle se tayyar** — overview page + har sheher ka 30 din ka timetable |
| Sirf timings, koi content nahi | **Surah tarjuma + Islamic events + articles** ek hi hub me |
| English content | **Sab kuch Roman Urdu me** — jese log search karte hain |
| SEO kamzor | **FAQ schema (JSON-LD)** home page par — featured snippet ka chance |
| Method chhupa hua | **Karachi method (18°/18°), Hanafi Asr** har page par saaf likha hua |

## Files kya kya hain

| File | Kaam |
|---|---|
| `docs/index.html` | Live demo home page — Aladhan se live timings + zyada maloomat (pehli update ke baad 160+ shehron wali table aa jayegi) |
| `docs/<sheher>.html` | 12 mashhoor shehron ke live demo pages; baqi 151 pages pehli update ke baad script banayega |
| `scripts/make_samples.py` | Live demo city pages banane wala generator (pehli update ke baad zaroorat nahi) |
| `docs/ramadan.html` | Ramadan 2027 overview: dates, sehri/iftar tareeqa, pehle roze ki andazan timings |
| `docs/ramadan/<sheher>.html` | Har sheher ka poora 30 din ka Ramadan timetable (ramadan.py banata hai) |
| `docs/events.html` | 2027 ke Islamic events (Shab-e-Miraj se Eid Milad tak) |
| `docs/surah/*.html` | Surah hub + Ikhlas, Falaq, Naas aur Mulk ka mukammal Roman Urdu tarjuma (Yaseen, Rahman, Kahf, Waqiah baad me ek ek kar ke) |
| `docs/articles/*.html` | 4 mukammal articles (bilkul Urdu script / Nastaliq me) + articles index page |
| `docs/about.html`, `docs/contact.html`, `docs/privacy-policy.html`, `docs/disclaimer.html` | AdSense ke liye zaroori pages — About, Contact (FormSubmit se email par connected — pehli submission par confirmation click karna hai), Privacy Policy, Disclaimer |
| `docs/404.html`, `docs/robots.txt`, `docs/sitemap.xml` | Custom 404 page, robots aur sitemap (sitemap ka domain `pakistanislam.tech` hai — domain badle to sitemap aur robots me bhi badal den) |
| `docs/data/*.json` | Har sheher ka raw data (script banata hai) |
| `scripts/update.py` | Rozana update: Hanafi + Jafria + kal ki Hijri date |
| `scripts/ramadan.py` | Ramadan timetable generator (ek dafa chalana hai) |
| `.github/workflows/daily-update.yml` | Roz raat 12 baje PKT khud chalne wala workflow |
| `cities.json` | **163 shehron** ki list |
| `config.json` | Settings: method, school, Hijri override, site name |
| `templates/*.html` | Premium pages ka design (script in se pages banata hai) |

## Publish karne ka tareeqa (step by step)

### Step 1 — GitHub par repo banayen
1. [github.com](https://github.com) par login karen → **New repository**.
2. Repository name: `pakistanislam`, **Public** → **Create repository**.

### Step 2 — Files upload karen
Repo page par **Add file → Upload files** → is project ki tamam files aur folders (`.github` samet) drag kar ke drop karen → **Commit changes**.

Git wala tareeqa:
```bash
git init
git add .
git commit -m "Islamic portal premium launch"
git branch -M main
git remote add origin https://github.com/APKA-USERNAME/pakistanislam.git
git push -u origin main
```

### Step 3 — GitHub Pages on karen
**Settings → Pages** → Source: `Deploy from a branch` → Branch: `main`, Folder: `/docs` → **Save**.
Site: `https://APKA-USERNAME.github.io/pakistanislam/`

### Step 4 — Actions ko permission den (zaroori!)
**Settings → Actions → General** → **Workflow permissions** me `Read and write permissions` → **Save**.

### Step 5 — Pehli update check karen
**Actions** tab → **Daily Update** workflow — push par khud chalega, 2–3 minute me green tick. (163 sheher × 3 API calls hain, is liye pehli run thori lambi ho sakti hai.) Phir site par asli timings, Islamic date aur poori shehron ki table hogi.

### Step 6 — Ramadan timetable banayen
Apne computer par ya Actions se:
```bash
python3 scripts/ramadan.py
```
`docs/ramadan/` ban jayega → push kar den. Ye abhi bhi chalaya ja sakta hai (Feb–Mar 2027 ka calendar calculation se milta hai). Ruet-e-Hilal ke elaan ke baad timetable dobara check karen.

### Step 7 — Custom domain + HTTPS
**Settings → Pages → Custom domain** me domain likhen (misal `pakistanislam.tech`) → DNS me 4 A records (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) + CNAME `www` → `APKA-USERNAME.github.io`.
HTTPS certificate banne me 15 minute se 24 ghante lag sakte hain — foran HTTPS chahiye to **Cloudflare free** par domain add kar ke SSL mode **Flexible** rakhen (baad me **Full (Strict)** par kar den). `github.io` subdomain par HTTPS foran automatic hota hai.

## Rozana kaam kaise hoga
- **Timings aur date:** kuch nahi karna — workflow roz khud update karta hai.
- **Naya article:** `docs/articles/` me nayi `.html` file banayen, home page ki list me link add karen, push karen.
- **Naya sheher:** `cities.json` me naam aur slug add karen, push karen — agle run me us ka page ban jayega.
- **Ruet-e-Hilal ka farq:** `config.json` me `hijri_date_override` bhar den, misal `"1 Ramadan 1448"`, push karen. Hatane ke liye dobara khaali kar den.
- **Chota sheher API par na mile to:** script usay skip kar ke warning dega, baqi site chalti rahegi. Us sheher ke visitors ko qareebi district ka page dikhayen (link home page ki table se mil jayega).

## Ramadan 2027 — Verified dates (mutawaqqa)
- Chand Raat: 7 February 2027 ki shaam • Pehla Roza: 8 February 2027 (Pakistan me 9 Feb mumkin)
- Laylatul Qadr (27wi shab): ~6 March 2027 • Eid-ul-Fitr: ~10 March 2027
- Eid-ul-Adha: 16–17 May 2027 • Ashura: 15–16 June 2027 • Eid Milad-un-Nabi: 14–15 August 2027
- Sab dates mutawaqqa hain — final sirf Ruet-e-Hilal ke elaan se.

## Google Search Console me register karne ka tareeqa
1. [search.google.com/search-console](https://search.google.com/search-console) par apne Google account se login karen → **Add property**.
2. **URL prefix** property chunen (misal `https://pakistanislam.tech/`) → verification ke liye **HTML tag** wala option chunen → jo `content="..."` code mile woh `templates/index.html`, `templates/city.html` aur `docs/index.html` me `APKA-GOOGLE-VERIFICATION-CODE` ki jagah likhen → push karen → Search Console me **Verify** dabayen.
3. Asaan tareeqa (Domain property): Search Console se **TXT record** le kar apne domain ke DNS (Cloudflare) me add karen — is me code har page me dalne ki zaroorat nahi hoti.
4. Verify hone ke baad Search Console me **Sitemaps** par ja kar `https://pakistanislam.tech/sitemap.xml` submit karen.
5. Domain agar `pakistanislam.tech` se kuch aur hua to `sitemap.xml`, `robots.txt` aur tamam pages ke canonical/OG links me domain find-replace kar den.

## Zaroori baaten
- Timings **University of Islamic Sciences, Karachi** method (18°/18°) aur **Hanafi Asr** par mabni hain; Jafria method 0 (Shia Ithna-Ashari) se li jati hain.
- Data source **Aladhan API** (free) hai — API down ho to script purana data rehne deta hai, site khaali nahi hoti.
- Har page par ye note hai ke timings calculated hain aur local masjid se confirm kar len.
