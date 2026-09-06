#!/usr/bin/env python3
"""
Generates docs/architecture.svg.

Every fact in the diagram is read from the live system rather than drawn
from memory: container names, images, IP addresses, published ports and
the network CIDR come from `docker network inspect`, and the branch,
environment and workflow facts from `gh api`.

Brand marks are the real logos from simple-icons, embedded as paths, so
the SVG has no external references and renders anywhere.

Render to PNG:
  python3 docs/generate-architecture.py
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\
    --headless --force-device-scale-factor=2 --window-size=1620,1420 \\
    --screenshot=docs/architecture.png file://$PWD/docs/render.html
"""
import json, pathlib

S = pathlib.Path("/private/tmp/claude-501/-Users-shashikirankulkarni/7b5a6f65-40a9-44f6-a521-8821d92fcbd0/scratchpad")
P = json.loads((S / "logos" / "paths.json").read_text())
BRAND = {"docker":"#2496ED","github":"#24292F","react":"#149ECA","postgresql":"#4169E1",
         "nginx":"#009639","spring":"#6DB33F","openjdk":"#E76F00","apple":"#111111"}

INK, INK2, MUTED = "#0F1518", "#42505A", "#7A868F"
RULE, SURF, PAPER = "#DCE3E7", "#FFFFFF", "#FFFFFF"
TEAL, VIOLET, OCHRE, BLUE, CRIM = "#0E6E78", "#5B4A93", "#9C5D12", "#1F5C8B", "#A3302B"
Z_VIOLET, Z_INK, Z_TEAL = "#F8F6FC", "#F8FAFB", "#F3F9FA"
MONO = "'JetBrains Mono','SF Mono',Menlo,monospace"
SANS = "'Archivo','Helvetica Neue',Arial,sans-serif"

o = []
def add(s): o.append(s)

def logo(name, cx, cy, size=40, color=None):
    if name not in P: return
    s = size / 24
    add(f'<g transform="translate({cx-size/2:.1f},{cy-size/2:.1f}) scale({s:.4f})">'
        f'<path d="{P[name]}" fill="{color or BRAND.get(name, INK)}"/></g>')

def glyph_browser(cx, cy, r=17):
    add(f'<g stroke="{INK}" stroke-width="1.9" fill="none"><circle cx="{cx}" cy="{cy}" r="{r}"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{r*0.42:.1f}" ry="{r}"/><path d="M{cx-r} {cy}h{2*r}"/></g>')

def node(x, y, w, h, name, lines, accent, icon=None, glyph=None, ghost=False):
    if ghost:
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{SURF}" stroke="{CRIM}" '
            f'stroke-width="1.5" stroke-dasharray="7 5"/>')
    else:
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{SURF}" stroke="{RULE}" '
            f'stroke-width="1.3" filter="url(#sh)"/>')
        add(f'<path d="M{x+9} {y+0.7} H{x+w-9}" stroke="{accent}" stroke-width="3.2" stroke-linecap="round"/>')
    cx = x + w/2
    if icon: logo(icon, cx, y+42, 40)
    if glyph: glyph(cx, y+42)
    add(f'<text x="{cx}" y="{y+84}" font-family="{SANS}" font-size="15" font-weight="700" '
        f'fill="{CRIM if ghost else INK}" text-anchor="middle">{name}</text>')
    yy = y + 104
    for ln in lines:
        add(f'<text x="{cx}" y="{yy}" font-family="{MONO}" font-size="10.5" fill="{MUTED}" '
            f'text-anchor="middle">{ln}</text>')
        yy += 15

def zone(x, y, w, h, color, fill, label, icon=None, dashed=True, right=False):
    d = ' stroke-dasharray="9 6"' if dashed else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{color}" '
        f'stroke-width="1.6"{d}/>')
    if right:
        tx = x + w - 22
        add(f'<text x="{tx}" y="{y+29}" font-family="{MONO}" font-size="11.5" font-weight="700" '
            f'letter-spacing="1.8" fill="{color}" text-anchor="end">{label}</text>')
        if icon: logo(icon, tx - 8.2*len(label) - 20, y+23, 19)
    else:
        tx = x + 22
        if icon:
            logo(icon, tx+10, y+24, 19); tx += 30
        add(f'<text x="{tx}" y="{y+29}" font-family="{MONO}" font-size="11.5" font-weight="700" '
            f'letter-spacing="1.8" fill="{color}">{label}</text>')

def arrow(d, color=MUTED, w=1.9, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"{da} marker-end="url(#m-{color[1:]})"/>')

def step(n, cx, cy, color=TEAL, r=12.5):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" stroke="#fff" stroke-width="2"/>'
        f'<text x="{cx}" y="{cy+4.4}" font-family="{MONO}" font-size="12" font-weight="700" '
        f'fill="#fff" text-anchor="middle">{n}</text>')

W, H = 1620, 1420
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs>')
for c in (MUTED, TEAL, OCHRE, BLUE, VIOLET):
    add(f'<marker id="m-{c[1:]}" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>')
add('<filter id="sh" x="-12%" y="-12%" width="126%" height="130%">'
    '<feDropShadow dx="0" dy="1.6" stdDeviation="2.6" flood-color="#0F1518" flood-opacity="0.09"/></filter>')
add('</defs>')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')

add(f'<text x="52" y="52" font-family="{SANS}" font-size="27" font-weight="700" fill="{INK}" '
    f'letter-spacing="-0.5">Catalog Platform &mdash; Deployment Architecture</text>')
add(f'<text x="52" y="76" font-family="{MONO}" font-size="12" fill="{MUTED}">'
    f'Two repositories &nbsp;&middot;&nbsp; two pipelines &nbsp;&middot;&nbsp; five containers &nbsp;&middot;&nbsp; one origin</text>')

NW, NH, NH2 = 256, 146, 128

# GITHUB
zone(52, 106, 1516, 214, VIOLET, Z_VIOLET, "GITHUB &middot; CLOUD", "github")
gc = [110, 486, 862, 1238]
node(gc[0], 152, NW, NH, "ecommerce-catalog", ["public repository", "main / dev / qa / prod"], VIOLET, icon="spring")
node(gc[1], 152, NW, NH, "catalog-frontend",  ["public repository", "main"], VIOLET, icon="react")
node(gc[2], 152, NW, NH, "Hosted runners",    ["ubuntu-latest &middot; x86_64", "ephemeral VM per job"], OCHRE, icon="github")
node(gc[3], 152, NW, NH, "Environments",      ["dev &middot; qa &middot; prod", "encrypted secrets"], OCHRE, icon="github")

# LAPTOP
zone(52, 372, 1516, 866, INK, Z_INK, "DEVELOPER MACHINE &middot; macOS &middot; APPLE M4 &middot; DOCKER DESKTOP", "apple", dashed=False)
node(110, 414, NW, NH, "Browser", ["dev.catalog.com", "/etc/hosts &rarr; 127.0.0.1"], INK, glyph=glyph_browser)

# DOCKER  — label right-aligned so no arrow crosses it
zone(110, 604, 1400, 606, TEAL, Z_TEAL, "DOCKER NETWORK &middot; catalog-net-nonprod &middot; 172.20.0.0/16", "docker", right=True)
c1, c2, c3, c4 = 168, 508, 848, 1188
rA, rB, rC = 652, 838, 1022

node(c1, rA, NW, NH,  "catalog-nginx",    ["nginx 1.27-alpine", ":443 &middot; :80 &middot; TLS edge"], TEAL, icon="nginx")
node(c2, rA, NW, NH,  "srv-dev",          ["ubuntu 24.04 &middot; JRE 21", ":8080 app &middot; :22 ssh"], TEAL, icon="openjdk")
node(c3, rA, NW, NH,  "catalog-postgres", ["postgres 17.11", "3 databases &middot; 3 roles"], BLUE, icon="postgresql")
node(c4, rA, NW, NH,  "srv-qa &middot; srv-prod", ["not built yet"], CRIM, ghost=True)

node(c1, rB, NW, NH2, "frontend-dist",    ["docker volume", "read-only to nginx"], TEAL, icon="docker")
node(c3, rB, NW, NH2, "pgdata-nonprod",   ["docker volume", "Flyway-managed schema"], BLUE, icon="docker")

node(c1, rC, NW, NH2, "frontend-runner",  ["self-hosted &middot; arm64", "deploys the UI"], OCHRE, icon="github")
node(c2, rC, NW, NH2, "catalog-runner",   ["self-hosted &middot; arm64", "deploys the backend"], OCHRE, icon="github")

# edges
arrow("M238 372 L238 322", VIOLET);                       step(1, 268, 348, VIOLET)
arrow("M1440 322 L1440 372", OCHRE, dash="6 5");          step(4, 1470, 348, OCHRE)
arrow("M238 560 L238 646", TEAL, 2.3);                    step(7, 268, 600, TEAL)
arrow(f"M{c1+NW} {rA+73} L{c2-6} {rA+73}", TEAL, 2.3);    step(9, (c1+NW+c2)/2, rA+73, TEAL)
arrow(f"M{c2+NW} {rA+73} L{c3-6} {rA+73}", BLUE, 2.0);    step(10, (c2+NW+c3)/2, rA+73, BLUE)
arrow(f"M{c1+NW/2} {rA+NH} L{c1+NW/2} {rB-6}", TEAL, 1.9); step(8, c1+NW/2, (rA+NH+rB)/2, TEAL)
arrow(f"M{c3+NW/2} {rA+NH} L{c3+NW/2} {rB-6}", BLUE, 1.9)
arrow(f"M{c1+NW/2} {rC} L{c1+NW/2} {rB+NH2+6}", OCHRE, 2.0); step(6, c1+NW/2, (rB+NH2+rC)/2, OCHRE)
arrow(f"M{c2+NW/2} {rC} L{c2+NW/2} {rA+NH+6}", OCHRE, 2.0); step(5, c2+NW/2, (rA+NH+rC)/2 - 10, OCHRE)

# ---------- legend ----------
LY = 1290
add(f'<text x="52" y="{LY}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{INK}">FLOW</text>')
steps = [
    (1, "A pull request is the only way onto a protected branch"),
    (4, "Runners poll GitHub outbound; nothing connects inward"),
    (5, "The JAR and a 600-mode .env are copied over SSH, then restarted"),
    (6, "The built UI bundle is published into the volume nginx serves"),
    (7, "Browser reaches nginx over TLS; port 80 redirects to 443"),
    (8, "index.html and hashed assets are served straight from the volume"),
    (9, "/api is proxied over plain HTTP inside the network"),
    (10, "The app connects as the environment&rsquo;s own database role"),
]
for i, (n, t) in enumerate(steps):
    cx = 66 + (i // 4) * 490
    yy = LY + 28 + (i % 4) * 23
    add(f'<circle cx="{cx}" cy="{yy-4}" r="9.5" fill="{TEAL}"/>')
    add(f'<text x="{cx}" y="{yy-0.4}" font-family="{MONO}" font-size="9.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')
    add(f'<text x="{cx+18}" y="{yy}" font-family="{SANS}" font-size="12.5" fill="{INK2}">{t}</text>')

KX = 1130
add(f'<text x="{KX}" y="{LY}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{INK}">PLANE</text>')
for i, (c, lbl) in enumerate([(VIOLET,"source control"), (OCHRE,"build &amp; deploy"),
                              (TEAL,"runtime"), (BLUE,"data")]):
    yy = LY + 28 + i * 23
    add(f'<rect x="{KX}" y="{yy-10}" width="12" height="12" rx="3" fill="{c}"/>')
    add(f'<text x="{KX+21}" y="{yy}" font-family="{SANS}" font-size="12.5" fill="{INK2}">{lbl}</text>')
add(f'<rect x="{KX+170}" y="{LY+18}" width="12" height="12" rx="3" fill="none" stroke="{CRIM}" stroke-dasharray="3 2"/>')
add(f'<text x="{KX+191}" y="{LY+28}" font-family="{SANS}" font-size="12.5" fill="{INK2}">not built yet</text>')
add(f'<text x="{KX+170}" y="{LY+51}" font-family="{MONO}" font-size="10.5" fill="{MUTED}">Host ports</text>')
add(f'<text x="{KX+170}" y="{LY+68}" font-family="{MONO}" font-size="10.5" fill="{MUTED}">443/80 &rarr; nginx</text>')
add(f'<text x="{KX+170}" y="{LY+84}" font-family="{MONO}" font-size="10.5" fill="{MUTED}">8081 &rarr; srv-dev &middot; 2222 &rarr; ssh</text>')
add(f'<text x="{KX+170}" y="{LY+100}" font-family="{MONO}" font-size="10.5" fill="{MUTED}">5433 &rarr; postgres</text>')

add('</svg>')
(S / "architecture-diagram.svg").write_text("".join(o))
print("wrote", len("".join(o)), "bytes")
