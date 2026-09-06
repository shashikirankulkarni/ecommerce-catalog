#!/usr/bin/env python3
"""
Generates docs/architecture.svg.

Drawn in the style used by most published technical architecture diagrams:
bare icons with a label beneath rather than cards, dashed frames grouping
related components, thin connectors, numbered call-outs, and horizontal
bands for each layer - source control, CI, CD, runtime.

Every fact is read from the live system rather than drawn from memory:
container names, images, ports and the network CIDR from docker inspect,
and branch, environment and workflow facts from gh api. Brand marks are
the real logos from simple-icons, embedded as paths, so the SVG has no
external references.

Render to PNG:
  python3 docs/generate-architecture.py
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \\
    --headless --force-device-scale-factor=2 --window-size=1960,1580 \\
    --screenshot=docs/architecture.png file://$PWD/docs/render.html
"""
import json, pathlib
S = pathlib.Path("/private/tmp/claude-501/-Users-shashikirankulkarni/7b5a6f65-40a9-44f6-a521-8821d92fcbd0/scratchpad")
P = json.loads((S/"logos"/"paths.json").read_text())

BR = {"docker":"#2496ED","github":"#181717","react":"#149ECA","postgresql":"#336791","nginx":"#009639",
      "spring":"#6DB33F","openjdk":"#E76F00","apple":"#111111","apachemaven":"#C71A36","nodedotjs":"#5FA04E",
      "swagger":"#85EA2D","apachetomcat":"#F8DC75","hibernate":"#59666C","letsencrypt":"#003A70",
      "googlechrome":"#4285F4","vite":"#646CFF","typescript":"#3178C6","gnubash":"#4EAA25",
      "ubuntu":"#E95420","sonarqube":"#4E9BCD","openssl":"#721412","jsonwebtokens":"#000000"}

INK, INK2, MUTED = "#111417", "#3E4A52", "#7A858E"
LINE, PAPER = "#3A444C", "#FFFFFF"
TEAL, VIOLET, OCHRE, BLUE, CRIM, GREEN = "#0B6B75", "#5B4A93", "#B26A0F", "#2C5F8D", "#A3302B", "#2F7D4F"
MONO = "'JetBrains Mono','SF Mono',Menlo,monospace"
SANS = "'Archivo','Helvetica Neue',Arial,sans-serif"

o=[]
def add(s): o.append(s)

def ic(cx, cy, name, size=52, color=None):
    if name not in P: return
    k = size/24
    add(f'<g transform="translate({cx-size/2:.1f},{cy-size/2:.1f}) scale({k:.4f})">'
        f'<path d="{P[name]}" fill="{color or BR.get(name, INK)}"/></g>')

def glyph(cx, cy, kind, size=52, color=INK):
    s=size/2; w=2.4
    if kind=="browser":
        add(f'<g stroke="{color}" stroke-width="{w}" fill="none"><circle cx="{cx}" cy="{cy}" r="{s*0.82:.1f}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{s*0.36:.1f}" ry="{s*0.82:.1f}"/>'
            f'<path d="M{cx-s*0.82:.1f} {cy}h{s*1.64:.1f}M{cx-s*0.7:.1f} {cy-s*0.42:.1f}h{s*1.4:.1f}'
            f'M{cx-s*0.7:.1f} {cy+s*0.42:.1f}h{s*1.4:.1f}"/></g>')
    elif kind=="volume":
        add(f'<g stroke="{color}" stroke-width="{w}" fill="none">'
            f'<ellipse cx="{cx}" cy="{cy-s*0.5:.1f}" rx="{s*0.8:.1f}" ry="{s*0.26:.1f}"/>'
            f'<path d="M{cx-s*0.8:.1f} {cy-s*0.5:.1f} v{s:.1f}c0 {s*0.26:.1f} {s*0.72:.1f} {s*0.26:.1f} {s*1.6:.1f} 0 v-{s:.1f}"/>'
            f'<path d="M{cx-s*0.8:.1f} {cy} c0 {s*0.26:.1f} {s*0.72:.1f} {s*0.26:.1f} {s*1.6:.1f} 0"/></g>')
    elif kind=="lock":
        add(f'<g stroke="{color}" stroke-width="{w}" fill="none">'
            f'<rect x="{cx-s*0.62:.1f}" y="{cy-s*0.16:.1f}" width="{s*1.24:.1f}" height="{s*0.9:.1f}" rx="4"/>'
            f'<path d="M{cx-s*0.36:.1f} {cy-s*0.16:.1f} v-{s*0.34:.1f}a{s*0.36:.1f} {s*0.36:.1f} 0 0 1 {s*0.72:.1f} 0v{s*0.34:.1f}"/></g>')
    elif kind=="pkg":
        add(f'<g stroke="{color}" stroke-width="{w}" fill="none">'
            f'<path d="M{cx} {cy-s*0.85:.1f} {cx+s*0.78:.1f} {cy-s*0.42:.1f} v{s*0.86:.1f} L{cx} {cy+s*0.85:.1f} '
            f'{cx-s*0.78:.1f} {cy+s*0.44:.1f} v-{s*0.86:.1f} Z"/>'
            f'<path d="M{cx-s*0.78:.1f} {cy-s*0.42:.1f} L{cx} {cy} l{s*0.78:.1f} -{s*0.42:.1f}M{cx} {cy}v{s*0.85:.1f}"/></g>')
    elif kind=="shield":
        add(f'<g stroke="{color}" stroke-width="{w}" fill="none">'
            f'<path d="M{cx} {cy-s*0.85:.1f} l{s*0.72:.1f} {s*0.3:.1f}v{s*0.5:.1f}c0 {s*0.5:.1f}-{s*0.3:.1f} {s*0.8:.1f}-{s*0.72:.1f} {s*0.95:.1f}'
            f'c-{s*0.42:.1f}-{s*0.15:.1f}-{s*0.72:.1f}-{s*0.45:.1f}-{s*0.72:.1f}-{s*0.95:.1f}v-{s*0.5:.1f}Z"/>'
            f'<path d="M{cx-s*0.28:.1f} {cy+s*0.02:.1f} l{s*0.2:.1f} {s*0.22:.1f} {s*0.38:.1f}-{s*0.44:.1f}"/></g>')

def node(cx, cy, name, l1, l2=None, l3=None, size=52, kind=None, color=None, num=None):
    (glyph(cx, cy, kind, size, color or INK) if kind else ic(cx, cy, name, size, color))
    y = cy + size/2 + 18
    add(f'<text x="{cx}" y="{y}" font-family="{SANS}" font-size="12.5" font-weight="600" fill="{INK}" '
        f'text-anchor="middle">{l1}</text>')
    if l2: add(f'<text x="{cx}" y="{y+15}" font-family="{MONO}" font-size="10" fill="{MUTED}" text-anchor="middle">{l2}</text>')
    if l3: add(f'<text x="{cx}" y="{y+29}" font-family="{MONO}" font-size="10" fill="{MUTED}" text-anchor="middle">{l3}</text>')
    if num is not None:
        add(f'<circle cx="{cx+size/2+11}" cy="{cy-size/2-2}" r="11.5" fill="{INK}"/>'
            f'<text x="{cx+size/2+11}" y="{cy-size/2+2.4}" font-family="{MONO}" font-size="12" font-weight="700" '
            f'fill="#fff" text-anchor="middle">{num}</text>')

def group(x, y, w, h, title, color=LINE, tint=None, right=False):
    if tint: add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{color}" fill-opacity="{tint}"/>')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="none" stroke="{color}" '
        f'stroke-width="1.3" stroke-dasharray="6 4"/>')
    if title:
        tx, anch = ((x+w-12), "end") if right else ((x+12), "start")
        add(f'<text x="{tx}" y="{y-8}" font-family="{MONO}" font-size="11" font-weight="700" '
            f'letter-spacing="1.3" fill="{color}" text-anchor="{anch}">{title}</text>')

def chip(x, y, t, color=MUTED, fs=9.5):
    w = 6.2*len(t)+16
    add(f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="9" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.4"/>')
    add(f'<text x="{x+w/2}" y="{y+12.6}" font-family="{MONO}" font-size="{fs}" fill="{color}" text-anchor="middle">{t}</text>')
    return w

def arw(d, color=LINE, w=1.6, dash=None):
    da=f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"{da} marker-end="url(#ar-{color[1:]})"/>')

def elab(t, x, y, color=INK2):
    add(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="10" fill="{color}" text-anchor="middle">{t}</text>')

W,H = 1960, 1580
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs>')
for c in (LINE, TEAL, OCHRE, BLUE, VIOLET, CRIM, GREEN):
    add(f'<marker id="ar-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>')
add('</defs>')
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
add(f'<text x="{W/2}" y="46" font-family="{SANS}" font-size="25" font-weight="700" fill="{INK}" text-anchor="middle">'
    f'Catalog Platform &mdash; Technical Architecture</text>')
add(f'<text x="{W/2}" y="70" font-family="{MONO}" font-size="11" fill="{MUTED}" text-anchor="middle">'
    f'Spring Boot 4.1 &middot; React 19 &middot; PostgreSQL 17 &middot; GitHub Actions &middot; Docker &nbsp;|&nbsp; two repositories, two pipelines, one origin</text>')

# ============================= BAND 1 : SOURCE =============================
group(48, 118, 1864, 176, "SOURCE CONTROL &middot; GITHUB", VIOLET, "0.035")
node(130, 175, "apple", "Developer", "macOS &middot; M4", size=44)
arw("M182 175 H244"); elab("git push", 213, 166)

node(300, 172, "spring", "ecommerce-catalog", "backend repository", num=1)
for i,(b,c) in enumerate([("main",MUTED),("dev",TEAL),("qa",OCHRE),("prod",CRIM)]):
    chip(232+i*62, 236, b, c)
node(560, 172, "react", "catalog-frontend", "frontend repository")
chip(530, 236, "main", MUTED)

arw("M356 172 H500")
group(700, 140, 300, 132, "BRANCH PROTECTION", CRIM)
node(790, 186, None, "Ruleset", "PR required", "0 bypass actors", size=40, kind="lock", color=CRIM)
node(915, 186, None, "Fork policy", "hosted only", size=40, kind="shield", color=CRIM)

group(1040, 140, 330, 132, "ENVIRONMENTS &middot; SECRETS", OCHRE)
node(1120, 182, None, "dev", "8 secrets", "4 variables", size=38, kind="lock", color=OCHRE)
node(1230, 182, None, "qa", "configured", size=38, kind="lock", color=OCHRE)
node(1325, 182, None, "prod", "+ reviewer", size=38, kind="lock", color=OCHRE)

group(1410, 140, 480, 132, "TRIGGERS", MUTED)
add(f'<text x="1432" y="176" font-family="{MONO}" font-size="11" fill="{INK2}">pull_request &rarr; main</text>')
add(f'<text x="1432" y="196" font-family="{MONO}" font-size="11" fill="{INK2}">&nbsp;&nbsp;&rarr; CI on ubuntu-latest</text>')
add(f'<text x="1432" y="224" font-family="{MONO}" font-size="11" fill="{INK2}">push &rarr; dev / qa / prod</text>')
add(f'<text x="1432" y="244" font-family="{MONO}" font-size="11" fill="{INK2}">&nbsp;&nbsp;&rarr; Deploy on self-hosted</text>')

# ============================= BAND 2 : CI =============================
group(48, 348, 1864, 194, "CONTINUOUS INTEGRATION &middot; GITHUB-HOSTED RUNNER &middot; x86_64 &middot; EPHEMERAL VM", OCHRE, "0.035")
arw("M330 296 V342"); elab("merge / PR", 392, 322)

xs = [140, 330, 520, 710, 900, 1090, 1290]
node(xs[0], 410, "github", "checkout", "fetch-depth 0", size=42, num=2)
node(xs[1], 410, "openjdk", "JDK 21", "temurin &middot; cached", size=42)
node(xs[2], 410, "apachemaven", "mvn verify", "compile &middot; test", size=42)
node(xs[3], 410, "postgresql", "Testcontainers", "postgres:17", size=42)
node(xs[4], 410, "gnubash", "gitleaks", "secret scan", size=42, num=3)
node(xs[5], 410, "sonarqube", "grype", "CVE scan &middot; SARIF", size=42, color=BLUE)
node(xs[6], 410, None, "artifact", "SHA-256 recorded", size=42, kind="pkg", color=OCHRE, num=4)
for a,b in zip(xs, xs[1:]):
    arw(f"M{a+34} 410 H{b-34}")

node(1520, 410, "nodedotjs", "npm ci", "lockfile exact", size=42)
node(1690, 410, "vite", "vite build", "tsc &middot; oxlint", size=42)
node(1812, 410, None, "bundle", "SHA-256 recorded", size=42, kind="pkg", color=OCHRE)
arw("M1554 410 H1656"); arw("M1724 410 H1778")
add(f'<path d="M1420 410 H1486" fill="none" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="4 4"/>')
add(f'<text x="1453" y="400" font-family="{MONO}" font-size="9.5" fill="{MUTED}" text-anchor="middle">frontend lane</text>')

# ============================= BAND 3 : CD =============================
group(48, 596, 1864, 214, "CONTINUOUS DELIVERY &middot; SELF-HOSTED RUNNERS &middot; arm64 &middot; PERSISTENT", TEAL, "0.035")
arw("M1290 452 V590"); elab("artifact + digest", 1372, 530)
arw("M1812 452 V590"); elab("bundle", 1862, 530)

group(80, 626, 900, 160, "catalog-runner &middot; labels: self-hosted, catalog", OCHRE)
cs = [170, 330, 490, 650, 810, 930]
node(cs[0], 690, "github", "verify digest", "= build SHA", size=38, num=5)
node(cs[1], 690, None, "render .env", "umask 077 &middot; 600", size=38, kind="lock", color=OCHRE)
node(cs[2], 690, "openssl", "ssh-keyscan", "pin host key", size=38)
node(cs[3], 690, "gnubash", "scp + ssh", "JAR &rarr; /opt/catalog", size=38, num=6)
node(cs[4], 690, None, "health gate", "30 &times; 2s retry", size=38, kind="shield", color=GREEN)
node(cs[5], 690, None, "shred .env", "workspace clean", size=38, kind="lock", color=CRIM)
for a,b in zip(cs, cs[1:]): arw(f"M{a+30} 690 H{b-30}")

group(1020, 626, 860, 160, "frontend-runner &middot; labels: self-hosted, frontend", OCHRE)
fs_ = [1110, 1290, 1470, 1650, 1810]
node(fs_[0], 690, "github", "verify digest", "= build SHA", size=38, num=7)
node(fs_[1], 690, None, "stage dev.new", "write to volume", size=38, kind="volume", color=TEAL)
node(fs_[2], 690, "gnubash", "atomic swap", "dev.old retained", size=38)
node(fs_[3], 690, None, "verify page", "grep app root", size=38, kind="shield", color=GREEN)
node(fs_[4], 690, None, "rollback", "on failure", size=38, kind="pkg", color=CRIM)
for a,b in zip(fs_, fs_[1:]): arw(f"M{a+30} 690 H{b-30}")

# ============================= BAND 4 : RUNTIME =============================
group(48, 872, 1864, 386, "RUNTIME &middot; DOCKER NETWORK catalog-net-nonprod &middot; 172.20.0.0/16 &middot; ON THE DEVELOPER MACHINE", TEAL, "0.03", right=True)

node(150, 960, None, "Browser", "dev.catalog.com", size=48, kind="browser")
arw("M150 1012 V1070"); elab("HTTPS", 182, 1046)
node(150, 1120, "letsencrypt", "/etc/hosts", "127.0.0.1", size=40, color=MUTED)

group(280, 906, 330, 320, "EDGE", TEAL, right=True)
node(370, 970, "nginx", "catalog-nginx", "nginx 1.27-alpine", ":443 &middot; :80 &rarr; 301", size=50, num=8)
node(370, 1120, None, "frontend-dist", "volume &middot; read-only", size=44, kind="volume", color=TEAL)
arw("M370 1044 V1092"); elab("serves", 412, 1072)
chip(300, 1180, "TLS termination", TEAL); chip(450, 1180, "Host routing", TEAL)

arw("M198 970 H336"); elab("443", 267, 960)

group(650, 906, 620, 320, "APPLICATION SERVER &middot; srv-dev", TEAL, right=True)
node(740, 972, "ubuntu", "ubuntu 24.04", "container as VM", size=44)
node(890, 972, "gnubash", "supervisord", "sshd + JVM", size=44)
node(1040, 972, "openjdk", "JRE 21", "no JDK present", size=44)
node(1190, 972, "apachetomcat", "Tomcat 11", ":8080 embedded", size=44, color="#D1A63F")
node(740, 1120, "spring", "Spring Boot 4.1", "catalog.jar", size=44)
node(890, 1120, "hibernate", "JPA / Hikari", "ddl-auto validate", size=44)
node(1040, 1120, "postgresql", "Flyway", "V1 on startup", size=44, color=CRIM)
node(1190, 1120, "swagger", "Actuator", "health &middot; info only", size=44, color=GREEN)
arw("M410 970 H700", TEAL); elab("/api &rarr; :8080", 555, 960)

group(1310, 906, 570, 320, "DATA", BLUE, right=True)
node(1420, 972, "postgresql", "catalog-postgres", "postgres 17.11", size=48, num=9)
node(1420, 1120, None, "pgdata-nonprod", "volume", size=44, kind="volume", color=BLUE)
arw("M1420 1046 V1092")
for i,(db,role) in enumerate([("catalog_local","local_user"),("catalog_dev","dev_user"),("catalog_qa","qa_user")]):
    y = 950 + i*56
    add(f'<rect x="1560" y="{y}" width="280" height="42" rx="6" fill="{BLUE}" fill-opacity="0.07" stroke="{BLUE}" stroke-opacity="0.35"/>')
    add(f'<text x="1578" y="{y+18}" font-family="{MONO}" font-size="11" font-weight="700" fill="{BLUE}">{db}</text>')
    add(f'<text x="1578" y="{y+34}" font-family="{MONO}" font-size="9.5" fill="{MUTED}">owner {role} &middot; CONNECT revoked from PUBLIC</text>')
arw("M1470 972 H1550", BLUE)
arw("M1240 1030 H1370", BLUE); elab("JDBC :5432", 1305, 1020)

# deploy arrows down into runtime
arw("M650 750 V828 H740 V898", OCHRE, 1.8, "7 5"); elab("deploy JAR &middot; scp", 700, 820, OCHRE)
arw("M1110 750 V850 H232 V1120 H336", OCHRE, 1.8, "7 5"); elab("publish bundle &middot; volume write", 1000, 842, OCHRE)

# ============================= LEGEND =============================
LY = 1310
add(f'<text x="48" y="{LY}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{INK}">NUMBERED FLOW</text>')
fl = [("1","Developer opens a pull request &mdash; the only way onto a protected branch"),
      ("2","CI checks out with full history so gitleaks can walk every commit"),
      ("3","gitleaks and grype gate the merge; findings publish as SARIF"),
      ("4","The artifact is hashed here; this exact file is what ships"),
      ("5","The runner re-verifies the digest before touching the server"),
      ("6","JAR and a 600-mode .env travel separately; the env file is shredded after"),
      ("7","Frontend digest verified, staged, then swapped atomically"),
      ("8","nginx terminates TLS and splits static from /api on one origin"),
      ("9","Each environment connects as its own role; CONNECT revoked from PUBLIC")]
for i,(n,t) in enumerate(fl):
    cx = 62 + (i//3)*640; yy = LY+28+(i%3)*24
    add(f'<circle cx="{cx}" cy="{yy-5}" r="10" fill="{INK}"/>')
    add(f'<text x="{cx}" y="{yy-1}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')
    add(f'<text x="{cx+18}" y="{yy}" font-family="{SANS}" font-size="12.5" fill="{INK2}">{t}</text>')

add(f'<text x="48" y="{LY+120}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{INK}">NOT BUILT YET</text>')
for i,t in enumerate(["srv-qa and srv-prod application servers",
                      "catalog-net-prod, the isolated production network",
                      "the production approval gate exercised end to end",
                      "an artifact registry for true build-once-promote-many"]):
    add(f'<text x="62" y="{LY+146+i*22}" font-family="{SANS}" font-size="12.5" fill="{CRIM}">&bull;&nbsp; {t}</text>')

add(f'<text x="{W-48}" y="{LY+28}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" '
    f'fill="{INK}" text-anchor="end">HOST PORTS</text>')
for i,t in enumerate(["443 / 80 &rarr; catalog-nginx","8081 &rarr; srv-dev","2222 &rarr; srv-dev ssh","5433 &rarr; catalog-postgres"]):
    add(f'<text x="{W-48}" y="{LY+52+i*22}" font-family="{MONO}" font-size="11" fill="{INK2}" text-anchor="end">{t}</text>')

add('</svg>')
(S/"architecture-diagram.svg").write_text("".join(o))
print("wrote", len("".join(o)), "bytes")
