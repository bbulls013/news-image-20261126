#!/usr/bin/env python3
"""The World Today - Thursday 26 November 2026. Procedural newspaper front page.
Stdlib only. Deterministic. Writes /output/entry.png (fallback ./output/entry.png)."""
import os, struct, zlib

W, H = 1024, 1024
px = bytearray(W * H * 3)

def C(r, g, b): return (r, g, b)
PAPER = C(247, 242, 230); INK = C(26, 26, 26); RED = C(176, 42, 32)
NAVY = C(31, 58, 95); GOLD = C(184, 134, 42); GREY = C(110, 105, 95)
LIGHT = C(238, 231, 214); TEAL = C(28, 110, 100); WHITE = C(255, 255, 255)

def setp(x, y, col):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i+1], px[i+2] = col

def rect(x, y, w, h, col):
    for yy in range(max(0, y), min(H, y + h)):
        base = yy * W * 3
        for xx in range(max(0, x), min(W, x + w)):
            i = base + xx * 3
            px[i], px[i+1], px[i+2] = col

def frame(x, y, w, h, col, t=2):
    rect(x, y, w, t, col); rect(x, y + h - t, w, t, col)
    rect(x, y, t, h, col); rect(x + w - t, y, t, h, col)

def hline(x, y, w, col, t=1): rect(x, y, w, t, col)
def vline(x, y, h, col, t=1): rect(x, y, t, h, col)

def disc(cx, cy, r, col):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                setp(xx, yy, col)

def ring(cx, cy, r, col, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r * r:
                setp(xx, yy, col)

# ---- 5x7 bitmap font (rows top->bottom, '#' = ink) ----
F = {
'A':["01110","10001","10001","11111","10001","10001","10001"],
'B':["11110","10001","10001","11110","10001","10001","11110"],
'C':["01110","10001","10000","10000","10000","10001","01110"],
'D':["11100","10010","10001","10001","10001","10010","11100"],
'E':["11111","10000","10000","11110","10000","10000","11111"],
'F':["11111","10000","10000","11110","10000","10000","10000"],
'G':["01110","10001","10000","10111","10001","10001","01111"],
'H':["10001","10001","10001","11111","10001","10001","10001"],
'I':["01110","00100","00100","00100","00100","00100","01110"],
'J':["00111","00010","00010","00010","00010","10010","01100"],
'K':["10001","10010","10100","11000","10100","10010","10001"],
'L':["10000","10000","10000","10000","10000","10000","11111"],
'M':["10001","11011","10101","10101","10001","10001","10001"],
'N':["10001","11001","10101","10011","10001","10001","10001"],
'O':["01110","10001","10001","10001","10001","10001","01110"],
'P':["11110","10001","10001","11110","10000","10000","10000"],
'Q':["01110","10001","10001","10001","10101","10010","01101"],
'R':["11110","10001","10001","11110","10100","10010","10001"],
'S':["01111","10000","10000","01110","00001","00001","11110"],
'T':["11111","00100","00100","00100","00100","00100","00100"],
'U':["10001","10001","10001","10001","10001","10001","01110"],
'V':["10001","10001","10001","10001","10001","01010","00100"],
'W':["10001","10001","10001","10101","10101","10101","01010"],
'X':["10001","01010","00100","00100","00100","01010","10001"],
'Y':["10001","01010","00100","00100","00100","00100","00100"],
'Z':["11111","00001","00010","00100","01000","10000","11111"],
'0':["01110","10001","10011","10101","11001","10001","01110"],
'1':["00100","01100","00100","00100","00100","00100","01110"],
'2':["01110","10001","00001","00010","00100","01000","11111"],
'3':["11111","00010","00100","00010","00001","10001","01110"],
'4':["00010","00110","01010","10010","11111","00010","00010"],
'5':["11111","10000","11110","00001","00001","10001","01110"],
'6':["00110","01000","10000","11110","10001","10001","01110"],
'7':["11111","00001","00010","00100","01000","01000","01000"],
'8':["01110","10001","10001","01110","10001","10001","01110"],
'9':["01110","10001","10001","01111","00001","00010","01100"],
' ':["00000"]*7, '.':["00000","00000","00000","00000","00000","01100","01100"],
',':["00000","00000","00000","00000","01100","00100","01000"],
':':["00000","01100","01100","00000","01100","01100","00000"],
';':["00000","01100","01100","00000","01100","00100","01000"],
'-':["00000","00000","00000","01110","00000","00000","00000"],
'!':["00100","00100","00100","00100","00100","00000","00100"],
'?':["01110","10001","00001","00110","00100","00000","00100"],
"'":["00100","00100","01000","00000","00000","00000","00000"],
'/':["00001","00010","00010","00100","01000","01000","10000"],
'&':["01100","10010","10100","01000","10101","10010","01101"],
'%':["11001","11010","00010","00100","01000","01011","10011"],
'(' :["00010","00100","01000","01000","01000","00100","00010"],
')' :["01000","00100","00010","00010","00010","00100","01000"],
'+':["00000","00100","00100","01110","00100","00100","00000"],
'=':["00000","00000","11111","00000","11111","00000","00000"],
'"':["01010","01010","01010","00000","00000","00000","00000"],
'*':["00000","10101","01110","11111","01110","10101","00000"],
'$':["00100","01111","10100","01110","00101","11110","00100"],
'#':["01010","01010","11111","01010","11111","01010","01010"],
}
def tw(s, sc): return len(s) * 6 * sc - sc
def text(x, y, s, sc, col, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        g = F.get(ch, F[' '])
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row[rx] == '1':
                    rect(cx + rx * sc, y + ry * sc, sc, sc, col)
                    if bold: rect(cx + rx * sc + sc, y + ry * sc, sc, sc, col)
        cx += 6 * sc
    return cx - x
def wrap(s, maxch):
    words, lines, cur = s.upper().split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= maxch: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ---------------- content: 48 items, 8 sections ----------------
SECTIONS = [
 ("AMERICAS", RED, [
   ("US PROPOSES NEW TARIFFS ON 14 PARTNERS", "Washington targets factory overcapacity; futures slide, dollar edges up."),
   ("COLOMBIA: POLICE FREE 20 HOSTAGES", "Supermarket siege ends after 17 hours; UN praises peace-accord progress."),
   ("ECUADOR REVIEWS US OPERATIONS", "Interior minister says talks with Pentagon focused on next steps."),
   ("BRAZIL: VIRAL INFECTIONS DOWN 68%", "Wolbachia mosquitoes credited with sharp fall in mosquito-borne illness."),
   ("GULF PLANE SEARCH CONTINUES", "Coast Guard searches for six aboard small plane down in Gulf of Mexico."),
   ("FORT HOOD SURVIVORS LOSE APPEAL", "Court rejects final bid to witness execution in long-running case."),
 ]),
 ("EUROPE", NAVY, [
   ("UKRAINE STRIKES RUSSIAN AIR BASE", "Kyiv says five missile-launch planes damaged in overnight attack."),
   ("34 STATES URGE RUSSIA TO STOP GAS USE", "Watchdog confirms tear-gas traces found in Ukrainian trench."),
   ("EU ADDS 15 RUSSIAN ENTITIES TO LIST", "New export curbs target defence-linked firms and dual-use tech."),
   ("MURMANSK GOVERNOR HELD IN GRAFT CASE", "Arctic port chief placed in pre-trial detention, court says."),
   ("UK-UKRAINE DRONE DEAL SIGNED", "London to jointly build long-range strike drones with Kyiv."),
   ("EU SET TO JOIN UKRAINE TALKS", "Kyiv awaits date for four-way meeting with US, Europe, Russia."),
 ]),
 ("ASIA-PACIFIC", TEAL, [
   ("PAKISTAN ASTRONAUT JOINS SHENZHOU-24", "First foreign crew member selected for China's Tiangong station."),
   ("INDIA MARKS CONSTITUTION DAY", "Samvidhan Divas observed nationwide; 26/11 victims remembered."),
   ("IITS TO ADD 6,000 TECH SEATS", "New places in robotics, AI and space technology from 2027."),
   ("BANGLADESH RAISES GARMENT WAGE 36%", "Entry-level minimum pay lifted after worker campaign."),
   ("NORTH KOREA ORDERS SWISS OFFICE SHUT", "Pyongyang tells Bern to close newly opened diplomatic post."),
   ("SOLOMON ISLANDS-AUSTRALIA TREATY", "Historic security pact signed in Pacific diplomatic push."),
 ]),
 ("MIDDLE EAST + AFRICA", GOLD, [
   ("HOUTHIS CLAIM RAS TANURA ATTACK", "Yemen group says Saudi refinery hit; fires reported."),
   ("TANKERS HIT MINES IN HORMUZ", "Two oil tankers damaged in strait; shipping on alert."),
   ("GAZA STRIKE STRAINS CEASEFIRE", "Israel kills Hamas security official; truce under pressure."),
   ("CAIRO HIGHWAY FIRE KILLS AT LEAST 30", "Fuel tanker crash ignites blaze on ring road, officials say."),
   ("LEBANON PLANS SECOND AIRPORT", "Northern hub to open next month as politics shift."),
   ("INDIA CONDEMNS RIYADH TOWER ATTACK", "New Delhi protests after two Indians injured in strike."),
 ]),
 ("BUSINESS", NAVY, [
   ("FLIPKART CEO TO STEP DOWN", "Kalyan Krishnamurthy set to leave Walmart-owned group in December."),
   ("INDIAN BANKS WRITE OFF BAD LOANS", "Lenders clear large stressed-debt book for financial year."),
   ("NVIDIA FACES SENATE QUESTIONS", "Antitrust scrutiny grows as AI chip exports draw fire."),
   ("US STOCKS PARE LOSSES", "Nasdaq and S+P bounce off lows as AI shares recover."),
   ("TATA SONS DELAYS BOARD MEETING", "Conglomerate board session pushed to 30 November."),
   ("EMIRATES TOPS AIRLINE RANKINGS", "Carrier leads global list as reliability stays in focus."),
 ]),
 ("SCIENCE + TECH", TEAL, [
   ("BEPI COLOMBO REACHES MERCURY", "Probe enters orbit after eight-year journey to innermost planet."),
   ("ASTEROID TEST IMAGES DUE", "Close-up views of deliberately struck asteroid to be revealed."),
   ("INDIA: HUMAN CONTROL OF AI ARMS", "New Delhi calls for humans to stay in charge of military AI."),
   ("INDIA SPACE ECONOMY TO GROW", "Minister projects growth from 9 to 45 billion dollars."),
   ("CHINA AI CHIP ACCESS EXPLAINED", "How advanced Nvidia chips reached China despite export rules."),
   ("BBC + MET OFFICE WEATHER PACT", "Broadcaster launches partnership for weather coverage."),
 ]),
 ("SPORT", RED, [
   ("GUKESH VS SINDAROV IN GENEVA", "World chess title match continues; game 2 ends in draw."),
   ("SOORYAVANSHI 204 OFF 53 BALLS", "Teen smashes fastest List A double century against UAE."),
   ("IPL 2027 AUCTION: 1,220 REGISTER", "Record pool of cricketers sign up for mega auction."),
   ("CHAMPIONS LEAGUE NIGHT", "Bellingham wondergoal for Real Madrid; Arsenal, City held."),
   ("ASIA CUP RISING STARS SEMI", "Sri Lanka A face India A in Doha knockout clash."),
   ("WORDLE 1986 SETS THE DAY", "Thursday puzzle trends as millions start morning routine."),
 ]),
 ("CULTURE", GOLD, [
   ("ANDY TAYLOR DIES AT 65", "Duran Duran guitarist remembered by fans worldwide."),
   ("RAMAYANA PASSES 1,000 CRORE", "Epic film joins Bollywood billion-rupee club on day 20."),
   ("SUPER 30 FOUNDER HONOURED IN JAPAN", "Anand Kumar receives award for education work."),
   ("COCONUTS PAY SCHOOL FEES", "Island scheme lets families pay tuition in coconuts."),
   ("SHOLAY-ERA STARS REMEMBERED", "Tributes pour in as classic cinema marks milestones."),
   ("NEW MUSIC FRIDAY PREVIEW", "Weekend releases lined up as charts shift again."),
 ]),
]

# ---------------- draw page ----------------
rect(0, 0, W, H, PAPER)
frame(8, 8, W - 16, H - 16, INK, 3)
frame(14, 14, W - 28, H - 28, INK, 1)

# masthead
text(28, 24, "VOL. 1  NO. 1", 1, GREY)
text(830, 24, "PRICE: ONE DAY", 1, GREY)
text(28, 40, "THE WORLD", 5, INK)
text(28, 80, "TODAY", 5, RED)
hline(28, 122, 620, INK, 3)
text(28, 132, "THURSDAY 26 NOVEMBER 2026", 3, INK)
text(28, 168, "ALL THE WORLD'S NEWS IN ONE IMAGE  *  48 STORIES  *  8 SECTIONS", 1, GREY)
# date badge
rect(680, 36, 316, 128, NAVY)
text(696, 48, "THURSDAY", 3, WHITE)
text(696, 76, "26 NOVEMBER", 3, WHITE)
text(696, 104, "2026", 5, GOLD)
text(850, 112, "ONE DAY", 1, WHITE); text(850, 124, "ONE PAGE", 1, WHITE)
text(850, 136, "ONE WORLD", 1, WHITE)

# hero band
rect(28, 186, 968, 196, LIGHT); frame(28, 186, 968, 196, INK, 2)
text(44, 196, "LEAD STORY", 1, RED, bold=True)
text(44, 210, "TARIFFS, STRIKES +", 3, INK)
text(44, 234, "A DAY OF DEALS", 3, INK)
hero = ["US TARIFF PLAN SHAKES MARKETS AS UKRAINE", "HITS RUSSIAN BASES, HORMUZ TANKERS ARE", "MINED, AND A PAKISTANI ASTRONAUT JOINS", "CHINA'S SPACE STATION - ALL ON ONE DAY."]
y = 266
for ln in hero: text(44, y, ln, 1, INK); y += 12
text(44, 322, "SEE SECTIONS BELOW FOR 48 BRIEFS.", 1, GREY)
# globe illustration: ocean disc, graticule, continent blobs, story pins
gx, gy, gr = 560, 282, 72
disc(gx, gy, gr, C(198, 220, 235))
ring(gx, gy, gr, NAVY, 3)
for off in (-44, -22, 22, 44):
    hline(gx - gr + 6, gy + off, gr * 2 - 12, NAVY, 1)
    vline(gx + off, gy - gr + 6, gr * 2 - 12, NAVY, 1)
vline(gx, gy - gr, gr * 2, NAVY, 2); hline(gx - gr, gy, gr * 2, NAVY, 2)
# continents as clustered blobs
for (dx, dy, r) in [(-38,-26,13),(-28,-12,10),(-20,16,9),(-12,30,6),(2,-30,9),(16,-22,11),(28,-6,12),(36,12,8),(18,26,7),(44,-30,6)]:
    disc(gx + dx, gy + dy, r, TEAL)
for (dx, dy) in [(-32,-20),(24,-12),(34,16),(-16,22)]:
    disc(gx + dx, gy + dy, 3, RED); ring(gx + dx, gy + dy, 6, RED, 1)
text(gx - 66, gy + gr + 6, "26 NOV 2026", 1, NAVY, bold=True)
# timeline
tx = 700
text(tx, 196, "DAY TIMELINE (UTC)", 1, RED, bold=True)
tl = [("00:00","WORDLE + MARKETS OPEN"),("06:00","CONSTITUTION DAY, INDIA"),
      ("09:00","TARIFFS + FUTURES SLIDE"),("13:00","HORMUZ + GAZA REPORTS"),
      ("17:00","CHESS GAME 2 DRAWN"),("21:00","UCL NIGHT IN EUROPE")]
yy = 214
for t, s in tl:
    disc(tx + 4, yy + 4, 3, RED); text(tx + 14, yy, t, 1, INK, bold=True); text(tx + 56, yy, s, 1, INK); yy += 16
# mini world map: continent blocks + red story pins
text(tx, 318, "WORLD MAP - STORY LOCATIONS", 1, NAVY, bold=True)
mx, my = tx, 332
for (dx, dy, w, h) in [(2,2,52,16),(16,20,20,16),(66,0,34,12),(78,14,22,20),(112,2,60,16),(150,20,34,14),(196,30,26,10)]:
    rect(mx + dx, my + dy, w, h, TEAL)
for (dx, dy) in [(24,8),(88,8),(132,8),(160,26),(208,34),(30,26)]:
    disc(mx + dx, my + dy, 3, RED)

# sections grid: 2 cols x 4 rows
cols_x = [28, 522]; col_w = 474
row_y = [396, 544, 692, 840]; row_h = 140
for idx, (name, col, items) in enumerate(SECTIONS):
    cx = cols_x[idx % 2]; cy = row_y[idx // 2]
    rect(cx, cy, col_w, 22, col)
    text(cx + 10, cy + 5, name, 2, WHITE)
    text(cx + col_w - 60, cy + 7, "6 NEWS", 1, WHITE)
    frame(cx, cy, col_w, row_h, INK, 1)
    iy = cy + 28
    for (title, sub) in items:
        disc(cx + 10, iy + 4, 3, col)
        text(cx + 20, iy, title[:50], 1, INK, bold=True)
        s = sub
        if len(s) > 62:
            s = s[:62].rsplit(" ", 1)[0] + "."
        text(cx + 20, iy + 9, s, 1, GREY)
        iy += 18

text(28, 990, "THE WORLD TODAY  *  THURSDAY 26 NOVEMBER 2026  *  SUM OF ONE DAY, IN ONE IMAGE  *  PAGE 1 OF 1", 1, GREY)
hline(28, 984, 968, INK, 2)

# ---------------- PNG write ----------------
def chunk(typ, data):
    return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
raw = bytearray()
for yy in range(H):
    raw.append(0)
    raw.extend(px[yy * W * 3:(yy + 1) * W * 3])
png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
png += chunk(b"IEND", b"")
out = "/output/entry.png"
try:
    os.makedirs("/output", exist_ok=True)
    with open(out, "wb") as f: f.write(png)
except OSError:
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "entry.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f: f.write(png)
print("wrote", out, len(png), "bytes")
