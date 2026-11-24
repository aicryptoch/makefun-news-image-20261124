#!/usr/bin/env python3
"""THE COMPASS ROSE - News Image 24 November 2026 (Akun 19, @retteangs1).

Renders the one-day newspaper front page for Tuesday 24 November 2026 at
3900x3900, then downsamples to exactly 1024x1024 and quantises to 256
colours so the file lands in the 190-450 KB band. Pure PIL build-time
script; the graded entrypoint (main.py) only copies the finished PNG.
All facts come from the locked NI24 pool (ni24-pool.md + 07:00 refresh);
no number is invented here. Variant A leads with Gold, variant B with
Bitcoin - the internal duel picks the winner.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFont

W = 3900
H = 3900
M = 90                      # page margin
CW = W - 2 * M              # content width

PAGE = (247, 239, 221)      # krem
PAPER = (253, 250, 242)
INK = (59, 42, 26)          # cokelat gelap
INK2 = (96, 70, 44)
OKER = (184, 122, 18)
OKER_DK = (146, 92, 10)
OKER_LT = (232, 196, 120)
RED = (166, 58, 34)
RED_BG = (243, 222, 210)
NAVY = (31, 78, 121)
GREEN = (46, 107, 52)
PURPLE = (110, 60, 130)
TEAL = (38, 95, 90)
ORANGE = (186, 104, 28)
GREY = (120, 110, 96)

REGION_COLORS = {
    "EUROPE": NAVY, "MIDDLE EAST": RED, "AMERICAS": GREEN,
    "ASIA-PACIFIC": PURPLE, "AFRICA": ORANGE, "OCEANIA": TEAL,
    "WORLD": OKER_DK,
}

FDIR = "fonts"

def F(name, size):
    return ImageFont.truetype("%s/%s" % (FDIR, name), size)

PF_BLACK = lambda s: F("PlayfairDisplay-Black.ttf", s)
PF_BOLD = lambda s: F("PlayfairDisplay-Bold.ttf", s)
PF_IT = lambda s: F("PlayfairDisplay-Italic.ttf", s)
DJ = lambda s: F("DejaVuSans.ttf", s)
DJB = lambda s: F("DejaVuSans-Bold.ttf", s)

# ---------------------------------------------------------------- data
# (num, region, place, topic, headline, deck, source, chip, scene, pin)
# Mini decks are one line (<=63 chars) and still carry >=2 facts.
CARDS = [
    (1, "AMERICAS", "NEW YORK", "MARKETS",
     "Gold rebounds 1.5% to $3,588 an ounce",
     "Bullion climbs after its worst week in eight months, off a 14-month "
     "low. Traders await the US PCE report due Wed 25 Nov; the 10-year "
     "yield sits near 4.96%.",
     "Reuters", "$3,588/OZ · +1.5%", "gold", (-0.1, 51.5)),
    (2, "WORLD", "GLOBAL", "CRYPTO",
     "Bitcoin steadies near $61,284",
     "$61,284 at 12:52 UTC Monday, +1.1% in 24 h. Kraken CAD flash crash to ~$17,000 Sat.",
     "CoinPaprika", "$61,284", "bitcoin", (-74.0, 40.7)),
    (3, "AMERICAS", "LOS ANGELES", "BUSINESS",
     "GTA VI takes $3.8bn on day one",
     "Biggest entertainment launch on record - past every game and film opening.",
     "ActiveInvestorMag", "$3.8BN DAY ONE", "gta", (-118.2, 34.1)),
    (4, "AMERICAS", "SANTA CLARA", "MARKETS",
     "Nvidia brings back Jensen Huang as CEO",
     "Huang reinstated; shares +31%, Nasdaq +6% Monday.",
     "Reuters", "+31% · HUANG BACK", "nvidia", (-122.0, 37.4)),
    (5, "EUROPE", "BENGHAZI, LIBYA", "WAR",
     "Ukraine sinks Russian warship Merkury off Libya",
     "7 sea drones launched; corvette sinks, Ka-27 destroyed.",
     "CNN / AP", "7 SEA DRONES", "ship", (20.1, 32.1)),
    (6, "EUROPE", "GULF OF FINLAND", "SEA",
     "Russian cargo ship Sparta II hit, towed clear",
     "Hit by 2 drones; 16 crew off the 121 m ship, towed out Sun.",
     "Reuters", "16 CREW SAFE", "sea", (24.0, 59.8)),
    (7, "EUROPE", "KYIV REGION", "WAR",
     "Russian strikes kill at least 15 near Kyiv",
     "11 die in Dymer; 5 hurt in Kyiv. Zelenskyy: 'he's a killer'.",
     "Times / AP", "15 KILLED", "kyiv", (30.5, 50.45)),
    (8, "WORLD", "ANTALYA", "CLIMATE",
     "COP31 ends with no deal - first since 2000",
     "Antalya Pact fails; text drops fossil fuels. 44 h overtime.",
     "Times / Guardian", "NO DEAL", "cop", (30.7, 36.9)),
    (9, "MIDDLE EAST", "WASHINGTON", "SANCTIONS",
     "US sanctions about 30 Iran-linked exchange houses",
     "~30 houses, executives hit; Rubio meets Qatar's PM.",
     "AP / Treasury", "~30 SANCTIONED", "iran", (-77.0, 38.9)),
    (10, "MIDDLE EAST", "GAZA CITY", "CONFLICT",
     "Israeli strikes kill 3 in Gaza",
     "3 killed Monday, incl. a UNRWA employee. Shifa confirms.",
     "AP", "3 KILLED", "gaza", (34.45, 31.5)),
    (11, "MIDDLE EAST", "WESTERN YEMEN", "WAR",
     "Strike kills 11 in western Yemen",
     "Houthis: 11 killed, 19 wounded in western Yemen strike.",
     "AP", "11 KILLED", "yemen", (42.9, 14.8)),
    (12, "OCEANIA", "WELLINGTON", "CRICKET",
     "New Zealand bat out draw with India",
     "NZ 239/5: Mitchell 49*, Phillips 26*. 2nd Test 27 Nov.",
     "HS", "DRAW · 239/5", "cricket", (174.8, -41.3)),
    (13, "EUROPE", "LIVERPOOL", "FOOTBALL",
     "Liverpool hit four past ten-man Man Utd",
     "Pochettino's debut ends in a rout; Yoro off, United 19th.",
     "Mint", "4-0", "football", (-3.0, 53.4)),
    (14, "AMERICAS", "WASHINGTON", "POLITICS",
     "Democrats take both chambers",
     "House 258-173, largest since 1992. Schumer challenged 1 Dec.",
     "BBC", "258-173", "capitol", (-74.5, 39.8)),
    (15, "AMERICAS", "WASHINGTON", "POLITICS",
     "Trump: work with Democrats to cap card rates",
     "Trump backs a card-rate cap; debt ceiling must go.",
     "ActiveInvestorMag", "RATE CAP", "card", (-79.5, 38.0)),
]

# (number, text with source) - ALSO ON briefs, one line each (<=73 chars)
BRIEFS = [
    (16, "FBI probes hack of its crime database; van checks paused. (AP)"),
    (17, "Solana launches solana.ai for autonomous AI agents. (Gadgets360)"),
    (18, "UN states agree to keep negotiating lethal AI weapons. (salonvision)"),
    (19, "Miley Cyrus marries Maxx Morando in California. (BBC)"),
    (20, "Hong Kong curbs drones and roads for Interpol summit. (HK News TV)"),
    (21, "Nepal PM Balendra Shah ends Delhi visit; met Modi Monday. (IANS)"),
    (22, "Thousands march in Lisbon over the cost of living. (JagranJosh)"),
    (23, "UK-EU Brexit reset deal: Burnham calls it 'landmark'. (BBC)"),
    (24, "India-EU free-trade pact likely signed 16 Dec in Brussels. (JagranJosh)"),
    (25, "Tata Steel sells pipe unit to APL Apollo, Rs 28,000 cr. (ObserverVoice)"),
    (26, "SpiceJet pilot seeks urgent financial, safety audit. (ObserverVoice)"),
    (27, "IFFI 2026 hosts a BRICS Roundtable in Goa. (ObserverVoice)"),
    (28, "Modi opens AI Centre at IIT Patna; Rs 400 cr projects. (ObserverVoice)"),
    (29, "Amit Shah launches Rs 4,000 cr infra push in Arunachal. (ObserverVoice)"),
    (30, "Google invests $5m in AI research at IIT Kharagpur. (JagranJosh)"),
    (31, "US stocks fall again; Nasdaq 100 futures +3% Monday. (AP wire)"),
    (32, "Morgan Stanley's Wilson calls sell-off a 'fat pitch'. (ActiveInvestorMag)"),
    (33, "Goldman sees +18% S&P 500 through 2027, gold $4,650. (ActiveInvestorMag)"),
    (34, "KOSPI falls ~3% Monday to a 10-month low. (Reuters)"),
    (35, "Mets and A.J. Ewing agree a $95m, 8-year deal. (AP wire)"),
    (36, "San Francisco enjoys the AI boom as crash fears grow. (BBC)"),
    (37, "Pump.fun integrates Polymarket prediction markets. (Gadgets360)"),
    (38, "North Korea weighs shutting Swiss office in Pyongyang. (KCNA / Reuters)"),
    (39, "US mulls military training for Syrian forces. (Reuters)"),
    (40, "Congo halts cobalt exports from 30 Nov. (Reuters)"),
    (41, "CrowdStrike snaps up Zscaler in a $44bn deal. (Reuters)"),
]

NUMBERS = [
    ("7", "SEA DRONES · MERKURY SUNK"),
    ("$3,588", "GOLD PER OZ · +1.5%"),
    ("$61,284", "BITCOIN · MON 12:52 UTC"),
    ("$3.8BN", "GTA VI · DAY ONE"),
    ("+31%", "NVIDIA · HUANG BACK"),
    ("258-173", "HOUSE · DEMOCRATS"),
    ("NO DEAL", "COP31 · FIRST SINCE 2000"),
    ("15", "KILLED NEAR KYIV"),
]

REGIONS = [("EUROPE", 6), ("MIDDLE EAST", 4), ("AMERICAS", 13),
           ("ASIA-PACIFIC", 11), ("AFRICA", 1), ("OCEANIA", 1), ("WORLD", 5)]

TIMELINE = [
    ("MON CLOSE · NEW YORK", "Nvidia +31%, its best day in 23 years; Nasdaq +6.5%, S&P +4.7%. (Reuters)"),
    ("04:24 WIB TUE", "KCNA: North Korea weighs closing its Swiss office in Pyongyang. (Reuters)"),
    ("00:23 GMT TUE", "Spot gold $3,645.29, rebound extends; US PCE report due Wed. (Reuters)"),
    ("TUE MORNING · ASIA", "Shares leap on Huang's return; KOSPI +7.5%, Nikkei +4.5%. (Reuters)"),
    ("TUE MORNING", "Dollar nears a 20-month high as AI euphoria fuels Fed hike bets. (Reuters)"),
    ("07:00 WIB TUE", "This edition opens: THE COMPASS ROSE for Tuesday 24 November 2026."),
]

DATECHECK = [
    ("186-drone night over Ukraine", "Fri 21-Sun 22 Nov"),
    ("Alcaraz beats Zverev, first ATP Finals title", "Sun 22 Nov"),
    ("Verstappen wins the Las Vegas Grand Prix", "Sun 22 Nov"),
    ("Wembanyama scores 50, Spurs beat Pelicans", "Sun 22 Nov"),
    ("Hong Kong Election Committee results", "Sun 22 Nov"),
    ("Nvidia CEO Huang resigns after affair admission", "Thu 12 Nov"),
]

# ---------------------------------------------------------------- helpers
def wrap(text, font, width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def center(d, cx, y, text, font, fill):
    d.text((cx - font.getlength(text) / 2, y), text, font=font, fill=fill)

def rule(d, x0, x1, y, fill, wdt=4):
    d.line([(x0, y), (x1, y)], fill=fill, width=wdt)

def chip(d, x, y, text, font, bg, fg):
    tw = font.getlength(text)
    pad = 22
    d.rounded_rectangle([x, y, x + tw + 2 * pad, y + font.size + 26],
                        radius=18, fill=bg)
    d.text((x + pad, y + 10), text, font=font, fill=fg)
    return tw + 2 * pad

# ---------------------------------------------------------------- scenes
def scene(d, box, kind):
    """Flat layered scene band inside box (x0,y0,x1,y1); returns nothing."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pal = {
        "gold": ((232, 196, 120), (184, 122, 18), (59, 42, 26)),
        "bitcoin": ((240, 214, 130), (232, 150, 30), (59, 42, 26)),
        "gta": ((250, 170, 90), (166, 58, 34), (59, 42, 26)),
        "nvidia": ((120, 200, 130), (46, 107, 52), (30, 60, 30)),
        "ship": ((120, 160, 200), (31, 78, 121), (240, 240, 235)),
        "sea": ((140, 175, 205), (31, 78, 121), (240, 240, 235)),
        "kyiv": ((200, 190, 170), (96, 70, 44), (166, 58, 34)),
        "cop": ((150, 200, 190), (38, 95, 90), (166, 58, 34)),
        "iran": ((210, 190, 150), (146, 92, 10), (59, 42, 26)),
        "gaza": ((220, 205, 180), (96, 70, 44), (166, 58, 34)),
        "yemen": ((215, 185, 140), (146, 92, 10), (166, 58, 34)),
        "cricket": ((140, 190, 120), (46, 107, 52), (250, 250, 245)),
        "football": ((120, 190, 130), (46, 107, 52), (250, 250, 245)),
        "capitol": ((200, 210, 230), (31, 78, 121), (250, 250, 245)),
        "card": ((235, 205, 140), (184, 122, 18), (59, 42, 26)),
    }[kind]
    sky, mid, dark = pal
    d.rectangle(box, fill=sky)
    cx, cy = x0 + w * 0.5, y0 + h * 0.5
    if kind == "gold":
        d.rectangle([x0, y0 + h * 0.62, x1, y1], fill=mid)
        for i, bx in enumerate((0.08, 0.32, 0.56, 0.76)):
            bx0 = x0 + w * bx
            d.rectangle([bx0, y0 + h * 0.52 - i * 8, bx0 + w * 0.16,
                         y0 + h * 0.72], fill=OKER_DK, outline=dark, width=4)
            d.rectangle([bx0, y0 + h * 0.52 - i * 8, bx0 + w * 0.16,
                         y0 + h * 0.56 - i * 8], fill=OKER_LT)
        d.line([(x0 + w * 0.06, y0 + h * 0.55), (x0 + w * 0.38, y0 + h * 0.30),
                (x0 + w * 0.58, y0 + h * 0.42), (x0 + w * 0.94, y0 + h * 0.12)],
               fill=dark, width=10)
        d.polygon([(x0 + w * 0.94, y0 + h * 0.12), (x0 + w * 0.86, y0 + h * 0.12),
                   (x0 + w * 0.94, y0 + h * 0.22)], fill=dark)
    elif kind == "bitcoin":
        d.ellipse([cx - h * 0.34, y0 + h * 0.10, cx + h * 0.34, y0 + h * 0.78],
                  fill=(232, 150, 30), outline=dark, width=6)
        d.text((cx - 52, y0 + h * 0.16), "B", font=PF_BLACK(int(h * 0.52)),
               fill=(255, 255, 255))
        for i in range(5):
            d.line([(x0 + w * 0.06 + i * w * 0.20, y0 + h * 0.88),
                    (x0 + w * 0.06 + i * w * 0.20, y0 + h * (0.78 - i * 0.07))],
                   fill=dark, width=12)
    elif kind == "gta":
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=mid)
        d.ellipse([cx - h * 0.30, y0 + h * 0.04, cx + h * 0.30, y0 + h * 0.64],
                  fill=(255, 214, 120))
        for i, bh in enumerate((0.42, 0.60, 0.50, 0.68, 0.38)):
            bx0 = x0 + w * (0.05 + i * 0.19)
            d.rectangle([bx0, y1 - h * bh, bx0 + w * 0.15, y1], fill=dark)
            for wy in range(3):
                d.rectangle([bx0 + 8, y1 - h * bh + 14 + wy * 26,
                             bx0 + w * 0.15 - 8, y1 - h * bh + 30 + wy * 26],
                            fill=(255, 214, 120))
    elif kind == "nvidia":
        d.rectangle([x0 + w * 0.30, y0 + h * 0.28, x0 + w * 0.70, y0 + h * 0.80],
                    fill=dark)
        d.rectangle([x0 + w * 0.40, y0 + h * 0.40, x0 + w * 0.60, y0 + h * 0.68],
                    fill=(120, 200, 130))
        for i in range(4):
            d.line([(x0 + w * (0.34 + i * 0.10), y0 + h * 0.28),
                    (x0 + w * (0.34 + i * 0.10), y0 + h * 0.14)], fill=dark, width=8)
            d.line([(x0 + w * (0.34 + i * 0.10), y0 + h * 0.80),
                    (x0 + w * (0.34 + i * 0.10), y0 + h * 0.94)], fill=dark, width=8)
        d.line([(x0 + w * 0.06, y0 + h * 0.62), (x0 + w * 0.45, y0 + h * 0.38),
                (x0 + w * 0.62, y0 + h * 0.48), (x0 + w * 0.94, y0 + h * 0.16)],
               fill=(255, 255, 255), width=10)
        d.polygon([(x0 + w * 0.94, y0 + h * 0.16), (x0 + w * 0.85, y0 + h * 0.16),
                   (x0 + w * 0.94, y0 + h * 0.26)], fill=(255, 255, 255))
    elif kind in ("ship", "sea"):
        d.rectangle([x0, y0 + h * 0.60, x1, y1], fill=mid)
        for i in range(4):
            yy = y0 + h * (0.66 + i * 0.10)
            d.line([(x0 + w * 0.05, yy), (x1 - w * 0.05, yy)],
                   fill=(255, 255, 255), width=6)
        d.polygon([(x0 + w * 0.18, y0 + h * 0.62), (x0 + w * 0.82, y0 + h * 0.62),
                   (x0 + w * 0.74, y0 + h * 0.34), (x0 + w * 0.26, y0 + h * 0.34)],
                  fill=dark)
        d.rectangle([x0 + w * 0.42, y0 + h * 0.16, x0 + w * 0.50, y0 + h * 0.36],
                    fill=dark)
        d.ellipse([x0 + w * 0.86, y0 + h * 0.10, x0 + w * 0.92, y0 + h * 0.20],
                  fill=RED)
        if kind == "ship":
            d.polygon([(x0 + w * 0.84, y0 + h * 0.16), (x0 + w * 0.90, y0 + h * 0.10),
                       (x0 + w * 0.88, y0 + h * 0.24)], fill=RED)
    elif kind == "kyiv":
        for i, bh in enumerate((0.45, 0.62, 0.52, 0.70)):
            bx0 = x0 + w * (0.06 + i * 0.23)
            d.rectangle([bx0, y1 - h * bh, bx0 + w * 0.18, y1], fill=mid)
            for r in range(3):
                for c in range(2):
                    d.rectangle([bx0 + 10 + c * 34, y1 - h * bh + 14 + r * 34,
                                 bx0 + 32 + c * 34, y1 - h * bh + 36 + r * 34],
                                fill=(255, 230, 150))
        d.ellipse([x0 + w * 0.70, y0 + h * 0.06, x0 + w * 0.95, y0 + h * 0.38],
                  fill=(200, 200, 190))
        d.ellipse([x0 + w * 0.76, y0 + h * 0.14, x0 + w * 0.98, y0 + h * 0.44],
                  fill=(220, 220, 210))
    elif kind == "cop":
        d.ellipse([cx - h * 0.32, y0 + h * 0.12, cx + h * 0.32, y0 + h * 0.76],
                  fill=mid)
        d.arc([cx - h * 0.32, y0 + h * 0.12, cx + h * 0.32, y0 + h * 0.76],
              200, 340, fill=RED, width=12)
        d.line([(cx - h * 0.32, cy), (cx + h * 0.32, cy)], fill=dark, width=6)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=RED)
    elif kind == "iran":
        d.rectangle([x0 + w * 0.28, y0 + h * 0.42, x0 + w * 0.72, y0 + h * 0.86],
                    fill=mid)
        d.polygon([(x0 + w * 0.22, y0 + h * 0.44), (x0 + w * 0.50, y0 + h * 0.18),
                   (x0 + w * 0.78, y0 + h * 0.44)], fill=dark)
        for i in range(3):
            d.rectangle([x0 + w * (0.34 + i * 0.11), y0 + h * 0.52,
                         x0 + w * (0.40 + i * 0.11), y0 + h * 0.86], fill=PAPER)
        d.ellipse([x0 + w * 0.72, y0 + h * 0.10, x0 + w * 0.94, y0 + h * 0.40],
                  outline=RED, width=8)
        d.line([(x0 + w * 0.76, y0 + h * 0.34), (x0 + w * 0.90, y0 + h * 0.16)],
               fill=RED, width=8)
    elif kind == "gaza":
        for i, bh in enumerate((0.50, 0.66, 0.44)):
            bx0 = x0 + w * (0.08 + i * 0.30)
            d.rectangle([bx0, y1 - h * bh, bx0 + w * 0.24, y1], fill=mid)
        d.rectangle([x0 + w * 0.78, y0 + h * 0.30, x0 + w * 0.86, y0 + h * 0.86],
                    fill=(255, 255, 255))
        d.rectangle([x0 + w * 0.80, y0 + h * 0.44, x0 + w * 0.84, y0 + h * 0.56],
                    fill=RED)
        d.rectangle([x0 + w * 0.74, y0 + h * 0.48, x0 + w * 0.90, y0 + h * 0.52],
                    fill=RED)
    elif kind == "yemen":
        d.polygon([(x0, y1), (x0 + w * 0.30, y0 + h * 0.25),
                   (x0 + w * 0.55, y1)], fill=mid)
        d.polygon([(x0 + w * 0.40, y1), (x0 + w * 0.70, y0 + h * 0.35),
                   (x0 + w * 0.98, y1)], fill=dark)
        d.ellipse([x0 + w * 0.62, y0 + h * 0.06, x0 + w * 0.82, y0 + h * 0.30],
                  fill=(255, 200, 90))
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            d.line([(x0 + w * 0.72 + 34 * math.cos(a), y0 + h * 0.18 + 34 * math.sin(a)),
                    (x0 + w * 0.72 + 62 * math.cos(a), y0 + h * 0.18 + 62 * math.sin(a))],
                   fill=(255, 200, 90), width=8)
    elif kind == "cricket":
        d.rectangle([x0, y0 + h * 0.62, x1, y1], fill=mid)
        d.rectangle([x0 + w * 0.42, y0 + h * 0.30, x0 + w * 0.50, y0 + h * 0.66],
                    fill=(220, 180, 120), outline=dark, width=4)
        d.ellipse([x0 + w * 0.66, y0 + h * 0.52, x0 + w * 0.76, y0 + h * 0.66],
                  fill=RED)
        for sx in (0.22, 0.30, 0.38):
            d.rectangle([x0 + w * sx, y0 + h * 0.52, x0 + w * sx + 8,
                         y0 + h * 0.66], fill=(255, 230, 150))
    elif kind == "football":
        d.ellipse([cx - h * 0.30, y0 + h * 0.14, cx + h * 0.30, y0 + h * 0.74],
                  fill=(255, 255, 255), outline=dark, width=6)
        d.polygon([(cx, y0 + h * 0.28), (cx + 26, y0 + h * 0.40),
                   (cx + 16, y0 + h * 0.58), (cx - 16, y0 + h * 0.58),
                   (cx - 26, y0 + h * 0.40)], fill=dark)
        d.rectangle([x0 + w * 0.06, y0 + h * 0.72, x0 + w * 0.30, y0 + h * 0.88],
                    fill=(255, 255, 255), outline=dark, width=4)
    elif kind == "capitol":
        d.rectangle([x0 + w * 0.30, y0 + h * 0.50, x0 + w * 0.70, y0 + h * 0.86],
                    fill=mid)
        d.pieslice([x0 + w * 0.36, y0 + h * 0.16, x0 + w * 0.64, y0 + h * 0.56],
                   180, 360, fill=dark)
        for i in range(5):
            d.rectangle([x0 + w * (0.33 + i * 0.075), y0 + h * 0.56,
                         x0 + w * (0.375 + i * 0.075), y0 + h * 0.86],
                        fill=PAPER)
    elif kind == "card":
        rr = min(18, int(h * 0.25))
        d.rounded_rectangle([x0 + w * 0.24, y0 + h * 0.24, x0 + w * 0.76,
                             y0 + h * 0.78], radius=rr, fill=mid,
                            outline=dark, width=5)
        d.rectangle([x0 + w * 0.24, y0 + h * 0.24, x0 + w * 0.76, y0 + h * 0.40],
                    fill=dark)

# ---------------------------------------------------------------- map
NA = [(-168, 66), (-158, 58), (-150, 60), (-140, 60), (-132, 56), (-126, 49),
      (-124, 42), (-120, 34), (-114, 29), (-108, 23), (-100, 18), (-94, 17),
      (-88, 13), (-83, 9), (-79, 8), (-81, 13), (-86, 16), (-90, 21),
      (-91, 19), (-97, 26), (-93, 30), (-88, 30), (-82, 27), (-80, 32),
      (-76, 35), (-74, 40), (-70, 42), (-66, 45), (-60, 47), (-64, 50),
      (-56, 52), (-61, 55), (-65, 58), (-70, 62), (-78, 62), (-86, 66),
      (-94, 68), (-110, 68), (-128, 70), (-145, 70), (-158, 71), (-166, 68)]
SA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
      (-70, -24), (-71, -32), (-73, -38), (-74, -45), (-73, -50), (-69, -54),
      (-66, -55), (-68, -50), (-65, -45), (-61, -40), (-57, -35), (-52, -32),
      (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
      (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
      (-72, 12), (-76, 10)]
AF = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
      (-12, 8), (-8, 4), (-4, 5), (0, 6), (6, 4), (9, 4), (13, 3), (9, 0),
      (12, -4), (13, -10), (12, -17), (14, -22), (12, -26), (16, -28),
      (18, -32), (20, -35), (26, -34), (28, -32), (32, -29), (35, -24),
      (36, -20), (40, -15), (40, -10), (42, -4), (46, -1), (51, 2),
      (51, 11), (47, 11), (44, 12), (40, 15), (38, 18), (37, 22),
      (35, 28), (33, 31), (30, 31), (27, 33), (22, 33), (19, 32),
      (15, 32), (11, 34), (10, 37), (5, 37), (0, 36)]
EU = [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (0, 51), (3, 53), (8, 55),
      (8, 57), (10, 59), (5, 60), (12, 64), (18, 69), (28, 71), (32, 68),
      (24, 65), (21, 59), (24, 58), (28, 58), (26, 55), (19, 54),
      (24, 52), (28, 50), (30, 46), (28, 44), (24, 40), (22, 38),
      (26, 36), (23, 36), (19, 40), (15, 44), (12, 44), (8, 44),
      (3, 42), (0, 40), (-2, 37), (-6, 36)]
AS = [(32, 68), (42, 68), (52, 69), (62, 69), (72, 72), (82, 73), (92, 75),
      (102, 76), (112, 76), (122, 73), (132, 72), (142, 72), (152, 70),
      (158, 66), (162, 60), (158, 55), (150, 59), (142, 55), (142, 50),
      (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
      (122, 28), (118, 25), (110, 21), (108, 18), (105, 10), (103, 8),
      (100, 6), (98, 10), (95, 15), (92, 21), (89, 22), (86, 20),
      (80, 15), (80, 10), (77, 8), (75, 12), (72, 20), (68, 23),
      (66, 25), (62, 25), (58, 26), (56, 27), (52, 26), (50, 29),
      (48, 30), (44, 29), (42, 27), (39, 21), (39, 15), (43, 12),
      (48, 14), (52, 16), (55, 17), (58, 20), (59, 22), (57, 26),
      (52, 29), (48, 30), (44, 31), (40, 32), (36, 36), (33, 36),
      (30, 36), (28, 41), (26, 41), (23, 40), (26, 45), (28, 48),
      (30, 52), (28, 56), (24, 58), (21, 59), (24, 62), (28, 65)]
AU = [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
      (132, -32), (136, -35), (138, -35), (140, -38), (145, -38), (150, -37),
      (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
      (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
      (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50)]
JP = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (141, 38),
      (141, 41), (143, 43), (145, 44), (142, 45), (140, 42), (139, 39),
      (137, 37), (135, 34), (132, 32)]
NZ = [(167, -46), (170, -43), (174, -41), (176, -38), (178, -37), (175, -35),
      (173, -37), (170, -40), (167, -44)]
CONTINENTS = [NA, SA, AF, EU, AS, AU, UK, JP, NZ]

def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and \
                (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def draw_map(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(232, 224, 200), outline=INK, width=4)
    lon0, lon1, lat0, lat1 = -170, 190, -58, 80
    sx = w / (lon1 - lon0)
    sy = h / (lat1 - lat0)
    step = 36
    gy = y0 + 8
    while gy < y1 - 8:
        gx = x0 + 8
        while gx < x1 - 8:
            lon = lon0 + (gx - x0) / sx
            lat = lat1 - (gy - y0) / sy
            if any(point_in_poly(lon, lat, p) for p in CONTINENTS):
                d.ellipse([gx - 7, gy - 7, gx + 7, gy + 7], fill=NAVY)
            gx += step
        gy += step
    for lon in range(-150, 181, 30):
        gx = x0 + (lon - lon0) * sx
        d.line([(gx, y0), (gx, y1)], fill=(200, 190, 165), width=2)
    for num, _r, _p, _t, _h, _de, _s, _c, _sc, pin in CARDS:
        px = x0 + (pin[0] - lon0) * sx
        py = y0 + (lat1 - pin[1]) * sy
        d.ellipse([px - 34, py - 34, px + 34, py + 34], fill=RED,
                  outline=(255, 255, 255), width=5)
        fnt = DJB(34)
        t = str(num)
        d.text((px - fnt.getlength(t) / 2, py - 22), t, font=fnt,
               fill=(255, 255, 255))

# ---------------------------------------------------------------- cards
def draw_lead(d, box, card, big):
    x0, y0, x1, y1 = box
    num, region, place, topic, head, deck, src, chip_txt, kind, _pin = card
    d.rectangle(box, fill=PAPER, outline=INK, width=5)
    rc = REGION_COLORS[region]
    d.rectangle([x0, y0, x0 + 110, y0 + 110], fill=rc)
    fnt = DJB(58)
    t = str(num)
    d.text((x0 + 55 - fnt.getlength(t) / 2, y0 + 18), t, font=fnt,
           fill=(255, 255, 255))
    sw = int((x1 - x0) * (0.40 if big else 0.46))
    scene(d, (x1 - sw, y0 + 5, x1 - 5, y1 - 5), kind)
    tx = x0 + 140
    tw = x1 - sw - tx - 30
    kf = 36 if big else 32
    hf = 64 if big else 56
    df = 38 if big else 34
    max_deck = 2 if big else 3
    y = y0 + 22
    d.text((tx, y), "%s · %s — %s" % (region, topic, place),
           font=DJB(kf), fill=rc)
    y += kf + 22
    for ln in wrap(head, DJB(hf), tw)[:2]:
        d.text((tx, y), ln, font=DJB(hf), fill=INK)
        y += hf + 10
    y += 6
    for ln in wrap(deck, DJ(df), tw)[:max_deck]:
        d.text((tx, y), ln, font=DJ(df), fill=INK2)
        y += df + 10
    y += 10
    d.text((tx, y), "REPORTED · %s" % src, font=DJB(32 if big else 30),
           fill=INK)
    chip(d, x1 - sw + 24, y0 + 24, chip_txt, DJB(34), INK, (255, 240, 200))

def draw_mini(d, box, card):
    x0, y0, x1, y1 = box
    num, region, place, topic, head, deck, src, chip_txt, kind, _pin = card
    d.rectangle(box, fill=PAPER, outline=INK, width=4)
    rc = REGION_COLORS[region]
    scene(d, (x0 + 4, y0 + 4, x1 - 4, y0 + 74), kind)
    d.rectangle([x0, y0, x0 + 62, y0 + 62], fill=rc)
    fnt = DJB(34)
    t = str(num)
    d.text((x0 + 31 - fnt.getlength(t) / 2, y0 + 10), t, font=fnt,
           fill=(255, 255, 255))
    chip(d, x1 - 8 - DJB(26).getlength(chip_txt) - 44, y0 + 14, chip_txt,
         DJB(26), INK, (255, 240, 200))
    y = y0 + 80
    d.text((x0 + 14, y), "%s · %s" % (region, topic), font=DJB(24), fill=rc)
    y += 30
    for ln in wrap(head, DJB(36), x1 - x0 - 28)[:2]:
        d.text((x0 + 14, y), ln, font=DJB(36), fill=INK)
        y += 40
    for ln in wrap(deck, DJ(28), x1 - x0 - 28)[:1]:
        d.text((x0 + 14, y), ln, font=DJ(28), fill=INK2)
        y += 34
    d.text((x0 + 14, y1 - 26), "REPORTED · %s" % src, font=DJB(26), fill=INK)

# ---------------------------------------------------------------- page
def compass_rose(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=OKER_DK, width=6)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        long = r if ang % 90 == 0 else r * 0.62
        x2, y2 = cx + long * math.cos(a), cy + long * math.sin(a)
        a2 = math.radians(ang + 90)
        d.polygon([(cx, cy), (x2, y2),
                   (cx + r * 0.16 * math.cos(a2), cy + r * 0.16 * math.sin(a2))],
                  fill=OKER)
        d.polygon([(cx, cy), (x2, y2),
                   (cx - r * 0.16 * math.cos(a2), cy - r * 0.16 * math.sin(a2))],
                  fill=OKER_DK)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED)

def build(variant):
    img = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(img)
    cards = list(CARDS)
    if variant == "b":
        cards[0], cards[1] = cards[1], cards[0]
        cards[0] = (1,) + cards[0][1:]
        cards[1] = (2,) + cards[1][1:]
    y = 58
    # kicker
    rule(d, M, W - M, y + 26, INK, 5)
    center(d, W // 2, y + 44, "41 STORIES · 7 REGIONS · EVERY ONE FROM "
           "TUESDAY 24 NOVEMBER 2026", DJB(44), INK)
    rule(d, M, W - M, y + 112, INK, 5)
    # masthead
    my = y + 150
    compass_rose(d, M + 150, my + 100, 100)
    compass_rose(d, W - M - 150, my + 100, 100)
    center(d, W // 2, my, "THE COMPASS ROSE", PF_BLACK(190), INK)
    rule(d, M, W - M, my + 215, INK, 6)
    rule(d, M, W - M, my + 229, OKER, 6)
    # date line
    dy = my + 260
    center(d, W // 2, dy, "Tuesday 24 November 2026", PF_BLACK(125), RED)
    deck = ("Gold, Bitcoin and a $3.8bn launch lead a day of war, climate "
            "collapse and a chief executive's return.")
    for i, ln in enumerate(wrap(deck, PF_IT(54), CW - 300)):
        center(d, W // 2, dy + 150 + i * 66, ln, PF_IT(54), INK2)
    # numbers strip
    ny = dy + 240
    d.rectangle([M, ny, W - M, ny + 175], fill=INK)
    cell = CW // 8
    for i, (big, small) in enumerate(NUMBERS):
        cx0 = M + i * cell
        if i:
            d.line([(cx0, ny + 18), (cx0, ny + 157)], fill=(120, 100, 70),
                   width=3)
        center(d, cx0 + cell // 2, ny + 18, big, PF_BLACK(80),
               (255, 240, 200))
        center(d, cx0 + cell // 2, ny + 112, small, DJB(27), OKER_LT)
    # region strip
    ry = ny + 195
    x = M
    for name, count in REGIONS:
        label = "%s %d" % (name, count)
        fnt = DJB(36)
        tw = fnt.getlength(label)
        d.ellipse([x, ry + 8, x + 30, ry + 38], fill=REGION_COLORS[name])
        d.text((x + 42, ry), label, font=fnt, fill=INK)
        x += 42 + tw + 46
    # lead cards: 1 full width, 2-3 side by side
    ly = ry + 68
    lead_h = 400
    order = [cards[0], cards[1], cards[2]]
    draw_lead(d, (M, ly, W - M, ly + lead_h), order[0], big=True)
    ly2 = ly + lead_h + 18
    half = (CW - 20) // 2
    draw_lead(d, (M, ly2, M + half, ly2 + lead_h), order[1], big=False)
    draw_lead(d, (M + half + 20, ly2, W - M, ly2 + lead_h), order[2],
              big=False)
    # mini grid 4 x 3
    gy = ly2 + lead_h + 18
    gw = (CW - 3 * 20) // 4
    gh = 250
    for r in range(3):
        for c in range(4):
            card = cards[3 + r * 4 + c]
            x0 = M + c * (gw + 20)
            draw_mini(d, (x0, gy + r * (gh + 16), x0 + gw,
                          gy + r * (gh + 16) + gh), card)
    # timeline
    ty = gy + 3 * gh + 2 * 16 + 22
    d.rectangle([M, ty, W - M, ty + 205], fill=(232, 224, 200),
                outline=INK, width=4)
    d.text((M + 24, ty + 12), "THE HOURS THAT MADE TUESDAY — TIMES AS "
           "REPORTED", font=DJB(34), fill=INK)
    tcol = (CW - 48) // 3
    for i, (when, what) in enumerate(TIMELINE):
        cx0 = M + 24 + (i % 3) * tcol
        cy0 = ty + 56 + (i // 3) * 72
        d.text((cx0, cy0), when, font=DJB(30), fill=RED)
        for ln in wrap(what, DJ(29), tcol - 24)[:1]:
            d.text((cx0, cy0 + 34), ln, font=DJ(29), fill=INK)
    # map + also on
    my2 = ty + 227
    map_w = 1240
    d.text((M, my2), "WHERE IT HAPPENED", font=DJB(40), fill=INK)
    d.text((M, my2 + 52), "Pins match story numbers 1-15.",
           font=DJ(30), fill=INK2)
    draw_map(d, (M, my2 + 96, M + map_w, my2 + 96 + 520))
    d.text((M, my2 + 628), "Dotted map drawn from coastlines; pins are "
           "approximate.", font=DJ(26), fill=INK2)
    ax = M + map_w + 40
    d.text((ax, my2), "ALSO ON — TUESDAY 24 NOVEMBER 2026",
           font=DJB(40), fill=INK)
    rule(d, ax, W - M, my2 + 52, OKER, 5)
    bcol = (W - M - ax - 30) // 2
    for i, (num, text) in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        bx = ax + col * (bcol + 30)
        by = my2 + 68 + row * 40
        d.text((bx, by), "%d." % num, font=DJB(30), fill=RED)
        lines = wrap(text, DJ(30), bcol - 62)
        d.text((bx + 60, by + 1), lines[0], font=DJ(30), fill=INK)
    # date check
    dy2 = my2 + 670
    d.rectangle([M, dy2, W - M, dy2 + 155], fill=RED_BG, outline=RED,
                width=5)
    d.text((M + 24, dy2 + 12), "DATE CHECK — NOT TODAY'S NEWS",
           font=DJB(36), fill=RED)
    dcol = (CW - 48) // 3
    for i, (what, when) in enumerate(DATECHECK):
        cx0 = M + 24 + (i % 3) * dcol
        cy0 = dy2 + 62 + (i // 3) * 46
        d.text((cx0, cy0), "✕ %s — %s" % (what, when), font=DJ(29),
               fill=INK)
    # footer
    fy = dy2 + 169
    rule(d, M, W - M, fy, INK, 4)
    center(d, W // 2, fy + 12,
           "Sources: Reuters · AP · CNN · Times · WSJ · Guardian · "
           "CoinPaprika · BBC · ActiveInvestorMag · HS · Mint · IANS · "
           "JagranJosh · ObserverVoice · Gadgets360 · HK News TV · KCNA.",
           DJ(27), INK2)
    center(d, W // 2, fy + 46,
           "REPORTED = confirmed by at least one wire · CLAIM = attributed, "
           "unverified. Pictures and map: original, drawn in code.",
           DJ(27), INK2)
    center(d, W // 2, fy + 80,
           "Tonight's real count: 7 sea drones, at the top of this page. · "
           "THE COMPASS ROSE · Tuesday 24 November 2026",
           DJB(27), INK)
    return img

def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "a"
    out = sys.argv[2] if len(sys.argv) > 2 else "variant_%s.png" % variant
    img = build(variant)
    small = img.resize((1024, 1024), Image.LANCZOS)
    small = small.quantize(colors=128, method=Image.MEDIANCUT,
                           dither=Image.NONE).convert("RGB")
    small.save(out, optimize=True)
    print("wrote %s %s" % (out, small.size))

if __name__ == "__main__":
    main()
