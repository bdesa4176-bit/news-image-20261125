# draw_news.py — renders the 25 Nov 2026 world-news summary as a 1024x1024 PNG.
# Deterministic: same input -> same bytes. Run: python3 draw_news.py
# (build-time tool; the entry itself is entry.png + main.ts, which copies it.)
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (16, 36, 62)
INK = (20, 20, 20)
GREY = (90, 90, 90)
LIGHT = (191, 208, 228)
RED = (178, 34, 34)

# (region, accent colour, [(headline, summary, utc, caveat), ...])
REGIONS = [
    ("NORTH AMERICA", (31, 78, 121), [
        ("US proposes tariffs on 14 trade partners", "Washington proposes new tariffs on 14 partners to fight excess factory capacity; China hit hardest.", "15:00", False),
        ("Abrego Garcia leaves US for Spain", "Salvadoran migrant Kilmar Abrego Garcia voluntarily leaves for Spain after a two-year deportation fight.", "02:00", False),
        ("Army blows up toxic lead azide in Iowa", "Army detonates 9,500 lbs of degraded lead azide in Iowa; EPA finds no lead in the air after the blast.", "15:00", False),
        ("Trump hosts NATO chief Rutte for dinner", "White House says Trump will host NATO chief Mark Rutte for dinner at Mar-a-Lago on Wednesday evening.", "18:00", False),
        ("US price gauge rises 3.8% in October", "Fed's favoured PCE index rose 3.8% in October, in line with forecasts, as tariff talk rattled markets.", "13:30", False),
        ("Huawei guilty of trade-secret theft", "New York jury finds Huawei guilty of bank fraud and stealing trade secrets; acquits it of racketeering.", "21:00", True),
    ]),
    ("LATIN AMERICA", (46, 125, 50), [
        ("Cartagena hostages freed after supermarket siege", "All remaining hostages freed early Wed; ~30 taken Tue, 10 released, 1 captor killed in dawn raid.", "06:30", True),
        ("US proposes new tariffs on Brazil aircraft, sugar", "Washington proposes 10% duty on finished aircraft and higher sugar duties; Brazil calls it unacceptable.", "19:00", False),
        ("Venezuela reveals $237bn debt, eyes restructuring", "Caracas discloses $237.5bn public debt, far above estimates; bonds rally as restructuring hopes rise.", "15:00", True),
        ("Argentina in technical recession, Caputo plays down", "Q3 shrank 1.8%, second straight fall; Caputo calls recession label 'arbitrary', rules out policy change.", "17:15", False),
        ("Chile teachers strike clashes with police in Santiago", "Thousands marched in nationwide strike over education cuts; clashes and water cannon in Santiago.", "18:00", True),
        ("Mexico FDI hits record $43.1bn, new funds plunge", "Jan-Sep FDI hit $43.09bn, up 5.3%, but 81% was reinvested profit; new investment fell 42.1%.", "10:08", True),
    ]),
    ("EUROPE", (106, 27, 154), [
        ("Ukraine hits 5 jets at Savasleyka base", "Ukraine says it damaged three MiG-31s and two Su-34s at Savasleyka and hit two Samara oil refineries.", "06:00", False),
        ("Leaked data: 490,334 Russian war dead", "Leaked Russian statistics show at least 490,334 soldiers died in Ukraine, BBC and Mediazona report.", "09:00", False),
        ("Russian strikes kill 2 in Odesa, hit Kyiv", "Overnight strikes kill two in Odesa and injure three, incl. a child; a Kyiv apartment block catches fire.", "03:00", False),
        ("Poland plans border no-fly zone", "Poland plans a no-fly zone along its Ukraine border to ease shooting down Russian missiles and drones.", "14:00", False),
        ("Merz: Russia 'escalating' threats to Europe", "Chancellor Merz accuses Russia of escalating threats as he defends higher defence spending and Ukraine aid.", "11:00", False),
        ("Pope Leo laments COP31 climate failure", "Pope Leo XIV voices concern over COP31's failure to reach a deal, warning of more extreme weather.", "12:00", False),
        ("Europe court backs migrant pushbacks", "Rights court rules states may turn back migrants weaponised by Belarus, except the vulnerable.", "09:00", True),
    ]),
    ("MIDDLE EAST", (184, 92, 0), [
        ("Two tankers hit mines in Strait of Hormuz", "IRGC says two oil tankers struck naval mines and caught fire while on an unauthorised route.", "08:00", False),
        ("Houthis hit Saudi Arabia's Ras Tanura refinery", "Houthis say they attacked the Ras Tanura refinery; Saudi air defences downed four drones over the site.", "10:00", False),
        ("Israel kills Hamas colonel Abuelouf in Gaza", "Israeli strike kills Hamas internal security colonel Mohammad Abuelouf, his wife and two children.", "05:00", False),
        ("US weighs targeting Iran's top leaders", "Trump team debates strikes on senior Iranian leaders, incl. Mojtaba Khamenei, to end the war, NBC says.", "00:36", True),
        ("IS attack kills 2 Syrian security staff", "Islamic State attack kills two Syrian internal security personnel and wounds five in Hasaka.", "12:00", False),
        ("UN aid chief lands in Yemen, urges access", "Tom Fletcher arrives in Yemen warning the war blocks food and medicine for families, incl. in Taiz City.", "10:00", False),
        ("UN fears new Israeli attacks in Gaza", "UN rights office warns Israeli attacks and policies point to a widening risk of further atrocity crimes.", "11:00", False),
    ]),
    ("AFRICA", (141, 110, 0), [
        ("Ebola workers evacuated amid DR Congo fighting", "UN peacekeepers evacuated 10 health workers trapped 3 days in Akwe as army-CRP clashes hit Ebola response.", "18:24", True),
        ("Somalia famine risk eases in Baidoa, millions hungry", "IPC: Baidoa no longer at famine risk, but 5.3m Somalis still face severe food insecurity.", "09:00", False),
        ("UN warns of escalation risk in Nigeria Niger State", "UN rights chief warns of further escalation after intercommunal killings in Niger State; dozens killed.", "15:19", False),
        ("RSF drone strikes kill 19 civilians in Sudan", "RSF drones hit Damazin homes in Blue Nile, killing 19 civilians, including six women; 20 wounded.", "10:30", True),
        ("21 killed in Egypt fuel vehicle blaze", "A petroleum vehicle overturned and caught fire on a ring road in Egypt, killing 21 people and injuring 15.", "18:30", False),
        ("Kenya cult leader convicted of new child charges", "Paul Mackenzie convicted of child cruelty and assault over Shakahola starvation deaths; sentencing to follow.", "14:00", False),
        ("Senegal parliament defies president over budget", "Assembly voted 128-9 against Faye implementing the rejected 2026 budget by decree, deepening IMF standoff.", "21:00", False),
    ]),
    ("SOUTH ASIA", (0, 105, 92), [
        ("Bangladesh garment workers clash over new minimum wage", "Board sets pay at 17,000 taka (+36%); workers in Gazipur block highways, police fire tear gas.", "02:30", False),
        ("India approves $1.2bn plan for construction equipment", "Eight-year scheme offers sales-linked incentives to cut reliance on Chinese imports, esp. tunnel borers.", "11:00", False),
        ("US to cap India tariff at 17% if trade deal is struck", "USTR Jamieson Greer says tariff rises to 25% without a deal; India denies excess capacity.", "14:00", False),
        ("India: Hasina return separate from extradition", "India says Hasina's plan to return to Bangladesh is separate from its extradition request.", "12:00", False),
        ("WFP seeks $28m as Nepal flood survivors face winter", "Three months after August floods, WFP says $28m more needed for food security over the next year.", "09:00", True),
        ("Landmine casualties hit five-year high of 6,929 in 2025", "Myanmar leads with 1,891, Syria 1,602; 84% of victims were civilians, half children.", "08:30", True),
    ]),
    ("EAST ASIA & ASIA-PACIFIC", (173, 20, 87), [
        ("Solomon Islands signs Australia security treaty", "Canberra becomes Honiara's defence partner of choice; $740m aid, no foreign bases pledge.", "02:00", False),
        ("China launches Shenzhou-24 with Pakistani astronaut", "First foreign astronaut aboard Tiangong: Muhammad Zeeshan Ali flies with Tang Hongbo and Wu Yi.", "00:18", False),
        ("Yongbyon expansion may boost uranium output", "US institute ISIS says new Yongbyon hall could house centrifuges for weapons-grade uranium.", "00:32", False),
        ("Australia passes Digital Duty of Care law", "Parliament passes online safety law; Big Tech faces fines up to 5% of global revenue.", "09:15", False),
        ("Asian stocks tumble on tariff and AI fears", "KOSPI falls ~6%, Nikkei ~3% as US tariff probe and AI sell-off hit chip-heavy markets.", "06:00", False),
        ("North Korea expels Swiss diplomat in sanctions row", "Pyongyang orders Sylvain Astier out in 48 hours and shuts Swiss office over camp sanctions.", "17:00", False),
    ]),
]

# (hour, short label) for the timeline strip at the bottom
TIMELINE = [
    (0, "Shenzhou-24 launches"),
    (2, "Bangladesh wage clashes"),
    (6, "Ukraine hits 5 jets at Savasleyka"),
    (8, "Hormuz tankers hit mines"),
    (9, "Leaked data: 490,334 Russian war dead"),
    (11, "Merz: Russia 'escalating' threats"),
    (12, "IS attack kills 2 in Syria"),
    (14, "Poland plans border no-fly zone"),
    (15, "US proposes tariffs on 14 partners"),
    (18, "Army blows up lead azide in Iowa"),
]


def sort_key(s):
    # † items (true date 23-24 Nov, led 25 Nov morning coverage) first, then by UTC hour
    utc = s[2]
    if utc == "24 Nov":
        return -60
    try:
        h, m = utc.split(":")
        return int(h) * 60 + int(m)
    except ValueError:
        return 0


def trunc(draw, text, font, width):
    if draw.textlength(text, font=font) <= width:
        return text
    while text and draw.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text + "…"


def main():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONTB, 38)
    f_sub = ImageFont.truetype(FONT, 17)
    f_reg = ImageFont.truetype(FONTB, 12)
    f_head = ImageFont.truetype(FONTB, 12)
    f_sum = ImageFont.truetype(FONT, 10)
    f_time = ImageFont.truetype(FONTB, 9)
    f_foot = ImageFont.truetype(FONT, 10)

    # ---- header ----
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.rectangle([0, 96, W, 100], fill=RED)
    d.text((24, 12), "THE WORLD IN ONE DAY", font=f_title, fill="white")
    d.text((24, 62), "Wednesday, 25 November 2026  ·  45 stories from 7 regions  ·  Times UTC",
           font=f_sub, fill=LIGHT)

    # ---- body: two columns, regions in geographic order ----
    margin, gutter = 24, 20
    col_w = (W - 2 * margin - gutter) // 2
    col_x = [margin, margin + col_w + gutter]
    body_top = 108
    # A = NA, LatAm, Europe (19 stories); B = ME, Africa, SA, EA (26 stories)
    cols = [[0, 1, 2], [3, 4, 5, 6]]
    for ci, members in enumerate(cols):
        x = col_x[ci]
        y = body_top
        for ri in members:
            name, colour, stories = REGIONS[ri]
            stories = sorted(stories, key=sort_key)
            d.rectangle([x, y, x + col_w, y + 20], fill=colour)
            d.text((x + 8, y + 4), "%s  ·  %d" % (name, len(stories)), font=f_reg, fill="white")
            y += 20 + 3
            for (headline, summary, utc, caveat) in stories:
                hl = trunc(d, headline + ("  †" if caveat else ""), f_head, col_w - 46)
                sm = trunc(d, summary, f_sum, col_w - 46)
                d.text((x, y + 1), utc, font=f_time, fill=GREY)
                d.text((x + 44, y), hl, font=f_head, fill=INK)
                d.text((x + 44, y + 15), sm, font=f_sum, fill=GREY)
                y += 30
            y += 6

    # ---- footer ----
    d.text((margin, 1004), "Sources: Reuters · AP · BBC · Al Jazeera · UN News · WSJ · CNN  —  † = event from 23–24 Nov that led 25 Nov coverage.",
           font=f_foot, fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
