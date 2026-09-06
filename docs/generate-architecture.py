#!/usr/bin/env python3
"""
Generates docs/architecture.svg.

Layout follows the conventions in AWS and general architecture-diagram
guidance: one flow direction per column and keep to it; no connector
crossing a node or pointing into empty space; protocol labels on the
connectors; numbered call-outs where a step needs more than a label;
grouping containers only where they add clarity; category colour carried
by the icon tile rather than a hairline.

Left column  - the request path, top to bottom.
Right column - the delivery pipeline, top to bottom.
Dashed arrows cross right to left: the two deployments.

Every fact is read from the live system rather than drawn from memory:
container names, images, ports and the network CIDR from docker inspect,
and the branch, environment and workflow facts from gh api. Brand marks
are the real logos from simple-icons, embedded as paths, so the SVG has
no external references.

Render to PNG:
  python3 docs/generate-architecture.py
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\
    --headless --force-device-scale-factor=2 --window-size=1640,1120 \\
    --screenshot=docs/architecture.png file://$PWD/docs/render.html
"""
import json, pathlib
S = pathlib.Path("/private/tmp/claude-501/-Users-shashikirankulkarni/7b5a6f65-40a9-44f6-a521-8821d92fcbd0/scratchpad")
P = json.loads((S / "logos" / "paths.json").read_text())

BR = {"docker":"#2496ED","github":"#24292F","react":"#149ECA","postgresql":"#336791",
      "nginx":"#009639","spring":"#6DB33F","openjdk":"#E76F00","apple":"#111111"}

INK, INK2, MUTED = "#0D1418", "#46545E", "#7C8892"
RULE, SURF, PAPER = "#D8E0E5", "#FFFFFF", "#FFFFFF"
TEAL, VIOLET, OCHRE, BLUE, CRIM = "#0B6B75", "#5B4A93", "#B26A0F", "#2C5F8D", "#A3302B"
MONO = "'JetBrains Mono','SF Mono',Menlo,monospace"
SANS = "'Archivo','Helvetica Neue',Arial,sans-serif"

o=[]
def add(s): o.append(s)

def tile(x, y, s, icon, color):
    """Large colour-filled icon tile - the icon leads, the colour carries the category."""
    add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="15" fill="{color}" fill-opacity="0.12"/>')
    add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="15" fill="none" stroke="{color}" stroke-opacity="0.28"/>')
    if icon in P:
        k = 42/24
        add(f'<g transform="translate({x+(s-42)/2:.1f},{y+(s-42)/2:.1f}) scale({k:.4f})">'
            f'<path d="{P[icon]}" fill="{BR.get(icon, color)}"/></g>')

def globe(x, y, s, color):
    add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="15" fill="{color}" fill-opacity="0.12"/>')
    add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="15" fill="none" stroke="{color}" stroke-opacity="0.28"/>')
    cx, cy, r = x+s/2, y+s/2, 20
    add(f'<g stroke="{color}" stroke-width="2.2" fill="none"><circle cx="{cx}" cy="{cy}" r="{r}"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{r*0.44:.1f}" ry="{r}"/><path d="M{cx-r} {cy}h{2*r}"/>'
        f'<path d="M{cx-r*0.86:.1f} {cy-r*0.5:.1f}h{1.72*r:.1f}M{cx-r*0.86:.1f} {cy+r*0.5:.1f}h{1.72*r:.1f}"/></g>')

def card(x, y, w, h, icon, color, title, sub, sub2=None, glyph=False):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{SURF}" stroke="{RULE}" '
        f'stroke-width="1.3" filter="url(#sh)"/>')
    add(f'<path d="M{x} {y+12} v{h-24}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
    ts = h - 34
    (globe if glyph else tile)(x+18, y+17, ts, color) if glyph else tile(x+18, y+17, ts, icon, color)
    tx = x + 18 + ts + 20
    add(f'<text x="{tx}" y="{y+h/2-8}" font-family="{SANS}" font-size="17" font-weight="700" fill="{INK}">{title}</text>')
    add(f'<text x="{tx}" y="{y+h/2+12}" font-family="{MONO}" font-size="11" fill="{MUTED}">{sub}</text>')
    if sub2:
        add(f'<text x="{tx}" y="{y+h/2+29}" font-family="{MONO}" font-size="11" fill="{MUTED}">{sub2}</text>')

def card_sm(x, y, w, h, icon, color, title, sub):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{SURF}" stroke="{RULE}" '
        f'stroke-width="1.3" filter="url(#sh)"/>')
    add(f'<path d="M{x} {y+12} v{h-24}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
    ts = h - 34
    tile(x+16, y+17, ts, icon, color)
    tx = x + 16 + ts + 14
    add(f'<text x="{tx}" y="{y+h/2-4}" font-family="{SANS}" font-size="14.5" font-weight="700" fill="{INK}">{title}</text>')
    add(f'<text x="{tx}" y="{y+h/2+15}" font-family="{MONO}" font-size="10" fill="{MUTED}">{sub}</text>')

def zone(x, y, w, h, color, label, tintop="0.05"):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{color}" fill-opacity="{tintop}" '
        f'stroke="{color}" stroke-width="1.8" stroke-dasharray="10 6"/>')
    add(f'<rect x="{x+20}" y="{y-13}" width="{11.6*len(label)+26}" height="26" rx="13" fill="{color}"/>')
    add(f'<text x="{x+33}" y="{y+5}" font-family="{MONO}" font-size="12" font-weight="700" '
        f'letter-spacing="1.8" fill="#fff">{label}</text>')

def arrow(d, color, w=2.6, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"{da} '
        f'marker-end="url(#m-{color[1:]})"/>')

def label(t, x, y, color, anchor="middle"):
    add(f'<rect x="{x - (6.9*len(t))/2 - 9}" y="{y-13}" width="{6.9*len(t)+18}" height="21" rx="10.5" '
        f'fill="#fff" stroke="{color}" stroke-opacity="0.3"/>')
    add(f'<text x="{x}" y="{y+2}" font-family="{MONO}" font-size="10.5" font-weight="500" fill="{color}" '
        f'text-anchor="{anchor}">{t}</text>')

def step(n, x, y, color):
    add(f'<circle cx="{x}" cy="{y}" r="15" fill="{color}"/>'
        f'<text x="{x}" y="{y+5.2}" font-family="{MONO}" font-size="14" font-weight="700" fill="#fff" '
        f'text-anchor="middle">{n}</text>')

W, H = 1640, 1120
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs>')
for c in (MUTED, TEAL, OCHRE, BLUE, VIOLET, CRIM):
    add(f'<marker id="m-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" '
        f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>')
add('<filter id="sh" x="-10%" y="-10%" width="122%" height="128%">'
    '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0D1418" flood-opacity="0.10"/></filter>')
add('</defs>')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')

add(f'<text x="48" y="50" font-family="{SANS}" font-size="26" font-weight="700" fill="{INK}" '
    f'letter-spacing="-0.5">Catalog Platform &mdash; Architecture</text>')
add(f'<text x="48" y="74" font-family="{MONO}" font-size="11.5" fill="{MUTED}">'
    f'Request path flows down the left &nbsp;&middot;&nbsp; delivery pipeline flows down the right</text>')

CW, CH = 300, 104
LX1, LX2 = 90, 420
RX = 926; RW = 624
rows = [140, 288, 436, 584]

zone(56, 112, 700, 616, TEAL, "RUNTIME &middot; DOCKER &middot; catalog-net-nonprod")
zone(892, 112, 692, 616, OCHRE, "DELIVERY &middot; CI / CD")

# ---- left column: request path, strictly top-to-bottom
card(LX1, rows[0], CW, CH, None, INK,  "Browser",          "dev.catalog.com", "TLS 1.3", glyph=True)
card(LX1, rows[1], CW, CH, "nginx", TEAL, "catalog-nginx", "nginx 1.27 &middot; edge", ":443 &middot; :80 redirect")
card(LX1, rows[2], CW, CH, "openjdk", TEAL, "srv-dev",     "ubuntu &middot; JRE 21", ":8080 &middot; :22 ssh")
card(LX1, rows[3], CW, CH, "postgresql", BLUE, "catalog-postgres", "postgres 17.11", "3 databases &middot; 3 roles")

card(LX2, rows[1], CW, CH, "docker", TEAL, "frontend-dist", "volume &middot; read-only", "SPA bundle")
card(LX2, rows[3], CW, CH, "docker", BLUE, "pgdata-nonprod", "volume", "Flyway schema")

# ---- right column: pipeline, strictly top-to-bottom
rrows = [140, 300, 452, 604]
HW = (RW - 18) / 2
card_sm(RX,        rrows[0], HW, 96, "spring", VIOLET, "ecommerce-catalog", "backend &middot; 4 branches")
card_sm(RX+HW+18,  rrows[0], HW, 96, "react",  VIOLET, "catalog-frontend",  "frontend &middot; main")
card(RX, rrows[1], RW, 100, "github", OCHRE,  "CI &mdash; build &amp; test", "ubuntu-latest &middot; ephemeral VM")
card(RX, rrows[2], RW, 100, "github", OCHRE,  "catalog-runner",    "self-hosted &middot; arm64")
card(RX, rrows[3], RW, 100, "github", OCHRE,  "frontend-runner",   "self-hosted &middot; arm64")

# ---- request path arrows (left, top-down)
mid = LX1 + CW/2
arrow(f"M{mid} {rows[0]+CH} L{mid} {rows[1]-8}", TEAL);  step(1, mid-52, (rows[0]+CH+rows[1])/2, TEAL); label("HTTPS :443", mid+64, (rows[0]+CH+rows[1])/2+4, TEAL)
arrow(f"M{mid} {rows[1]+CH} L{mid} {rows[2]-8}", TEAL);  step(3, mid-52, (rows[1]+CH+rows[2])/2, TEAL); label("/api &rarr; :8080", mid+70, (rows[1]+CH+rows[2])/2+4, TEAL)
arrow(f"M{mid} {rows[2]+CH} L{mid} {rows[3]-8}", BLUE);  step(4, mid-52, (rows[2]+CH+rows[3])/2, BLUE); label("JDBC :5432", mid+66, (rows[2]+CH+rows[3])/2+4, BLUE)
arrow(f"M{LX1+CW} {rows[1]+CH/2} L{LX2-8} {rows[1]+CH/2}", TEAL); step(2, (LX1+CW+LX2)/2, rows[1]+CH/2-30, TEAL); label("serves SPA", (LX1+CW+LX2)/2, rows[1]+CH/2+30, TEAL)
arrow(f"M{LX1+CW} {rows[3]+CH/2} L{LX2-8} {rows[3]+CH/2}", BLUE); label("persists", (LX1+CW+LX2)/2, rows[3]+CH/2-14, BLUE)

# ---- pipeline arrows (right, top-down)
rmid = RX + RW/2
q1, q2 = RX + HW/2, RX + HW + 18 + HW/2
jy = rrows[0] + 96 + 30
arrow(f"M{q1} {rrows[0]+96} L{q1} {jy} L{rmid} {jy} L{rmid} {rrows[1]-8}", VIOLET, 2.4)
add(f'<path d="M{q2} {rrows[0]+96} L{q2} {jy} L{rmid} {jy}" fill="none" stroke="{VIOLET}" stroke-width="2.4" stroke-linejoin="round"/>')
label("pull request", rmid, jy - 22, VIOLET)
arrow(f"M{rmid} {rrows[1]+100} L{rmid} {rrows[2]-8}", OCHRE, 2.4)
label("artifact + digest", rmid, rrows[1]+128, OCHRE)
arrow(f"M{rmid} {rrows[2]+100} L{rmid} {rrows[3]-8}", OCHRE, 2.4)

# ---- deploy arrows: right column into left column, no crossings
y_be = rows[2] + CH/2 + 22
arrow(f"M{RX-8} {rrows[2]+50} L{812} {rrows[2]+50} L{812} {y_be} L{LX1+CW+8} {y_be}", OCHRE, 2.4, dash="8 5")
step(6, 612, y_be, OCHRE); label("scp JAR + .env &middot; ssh :22", 612, y_be-32, OCHRE)

y_fe = rows[1] + CH/2 + 30
arrow(f"M{RX-8} {rrows[3]+50} L{844} {rrows[3]+50} L{844} {y_fe} L{LX2+CW+8} {y_fe}", OCHRE, 2.4, dash="8 5")
step(5, 844, y_fe, OCHRE); label("publish bundle", 824, y_fe-36, OCHRE)

# ---- legend
LY = 800
add(f'<text x="48" y="{LY}" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing="1.6" fill="{INK}">FLOW</text>')
steps = [("1","Browser reaches nginx over TLS; port 80 redirects to 443"),
         ("2","nginx serves index.html and hashed assets from the volume"),
         ("3","/api is proxied to the application over plain HTTP"),
         ("4","The app connects as that environment&rsquo;s own database role"),
         ("5","frontend-runner publishes the built bundle into the volume"),
         ("6","catalog-runner copies the JAR and a 600-mode .env, then restarts")]
for i,(n,t) in enumerate(steps):
    cx = 62 + (i//3)*700; yy = LY+30+(i%3)*27
    c = TEAL if n in "1234" else OCHRE
    add(f'<circle cx="{cx}" cy="{yy-5}" r="11" fill="{c}"/>')
    add(f'<text x="{cx}" y="{yy-1}" font-family="{MONO}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')
    add(f'<text x="{cx+20}" y="{yy}" font-family="{SANS}" font-size="13.5" fill="{INK2}">{t}</text>')

add(f'<text x="48" y="{LY+130}" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing="1.6" fill="{INK}">NOTES</text>')
notes = ["Runners poll GitHub outbound over HTTPS &mdash; nothing connects inward.",
         "Pull requests build on GitHub-hosted runners only; fork code never reaches this machine.",
         "srv-qa and srv-prod are not built yet; prod is planned on its own isolated network.",
         "Host ports &nbsp; 443/80 &rarr; nginx &nbsp;&middot;&nbsp; 8081 &rarr; srv-dev &nbsp;&middot;&nbsp; 2222 &rarr; ssh &nbsp;&middot;&nbsp; 5433 &rarr; postgres"]
for i,t in enumerate(notes):
    add(f'<text x="62" y="{LY+158+i*24}" font-family="{SANS}" font-size="13.5" fill="{INK2}">&bull;&nbsp; {t}</text>')

add(f'<text x="{W-48}" y="{LY+30}" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing="1.6" fill="{INK}" text-anchor="end">PLANE</text>')
for i,(c,l) in enumerate([(VIOLET,"source control"),(OCHRE,"build &amp; deploy"),(TEAL,"runtime"),(BLUE,"data")]):
    yy = LY+58+i*26
    add(f'<rect x="{W-190}" y="{yy-12}" width="14" height="14" rx="4" fill="{c}"/>')
    add(f'<text x="{W-168}" y="{yy}" font-family="{SANS}" font-size="13.5" fill="{INK2}">{l}</text>')

add('</svg>')
(S/"architecture-diagram.svg").write_text("".join(o))
print("wrote", len("".join(o)), "bytes")
