#!/usr/bin/env bash
#
# Seeds the catalog with sample products through the public API.
#
# Deliberately NOT a Flyway migration. Migrations are schema, they run in
# every environment including production, and they are immutable once
# applied. Demo data belongs to whoever wants it, in whichever
# environment they choose.
#
# Safe to re-run: a duplicate sku returns 409, which is reported rather
# than treated as a failure.
#
# Usage:
#   scripts/seed.sh                            # dev, via localhost:8081
#   scripts/seed.sh http://localhost:8080      # local, app run from the IDE
#   scripts/seed.sh https://dev.catalog.com    # dev, through the proxy

set -uo pipefail

BASE="${1:-http://localhost:8081}"
API="${BASE%/}/api/v1/products"

# curl -k so the self-signed proxy certificate does not need to be
# trusted just to run a seed script.
CURL=(curl -sS -k -o /dev/null -w '%{http_code}')

created=0 duplicate=0 failed=0

post() {
    local sku=$1 name=$2 category=$3 price=$4 stock=$5 description=$6
    local code
    code=$("${CURL[@]}" -X POST "$API" \
        -H 'Content-Type: application/json' \
        -d "$(printf '{"sku":"%s","name":"%s","category":"%s","price":%s,"stockQuantity":%s,"description":"%s"}' \
              "$sku" "$name" "$category" "$price" "$stock" "$description")")

    case "$code" in
        201) printf '  created    %-18s %s\n' "$sku" "$name"; ((created++)) ;;
        409) printf '  exists     %-18s %s\n' "$sku" "$name"; ((duplicate++)) ;;
        *)   printf '  FAILED %s  %-18s %s\n' "$code" "$sku" "$name"; ((failed++)) ;;
    esac
}

echo "Seeding $API"
echo

post "LAPTOP-001"  "ThinkPad X1 Carbon Gen 12"  "laptops"     149999.00  12  "14 inch business laptop, 32GB RAM, 1TB SSD"
post "LAPTOP-002"  "MacBook Air M4 13"          "laptops"     114900.00  25  "13 inch, 16GB unified memory, 512GB SSD"
post "LAPTOP-003"  "Dell XPS 15"                "laptops"     189990.00   6  "15.6 inch OLED, RTX 4060, 32GB RAM"
post "LAPTOP-004"  "ASUS ROG Zephyrus G14"      "laptops"     164990.00   0  "Gaming laptop, currently out of stock"

post "PHONE-001"   "iPhone 17 Pro"              "phones"      134900.00  40  "6.3 inch, 256GB, titanium"
post "PHONE-002"   "Samsung Galaxy S26 Ultra"   "phones"      129999.00  33  "6.8 inch AMOLED, 512GB, S Pen"
post "PHONE-003"   "Google Pixel 10 Pro"        "phones"       99999.00  18  "6.7 inch, 256GB"
post "PHONE-004"   "Nothing Phone 3a"           "phones"       27999.00  60  "6.5 inch, 128GB"

post "AUDIO-001"   "Sony WH-1000XM6"            "audio"        34990.00  22  "Over-ear noise cancelling headphones"
post "AUDIO-002"   "AirPods Pro 3"              "audio"        26900.00  55  "In-ear, active noise cancellation"
post "AUDIO-003"   "Sennheiser HD 660S2"        "audio"        49990.00   4  "Open-back reference headphones"

post "ACC-001"     "Logitech MX Master 4"       "accessories"   9995.00 120  "Wireless mouse, multi-device"
post "ACC-002"     "Keychron Q1 Pro"            "accessories"  18500.00  35  "75 percent mechanical keyboard, hot swappable"
post "ACC-003"     "Anker 737 Power Bank"       "accessories"  12999.00  80  "24000mAh, 140W output"
post "ACC-004"     "CalDigit TS5 Plus Dock"     "accessories"  42999.00   9  "Thunderbolt 5 dock, 18 ports"
post "ACC-005"     "USB-C to USB-C Cable 2m"    "accessories"    899.00 500  "240W, USB4"

post "DISPLAY-001" "Dell UltraSharp U2725QE"    "displays"     58990.00  14  "27 inch 4K IPS Black, USB-C hub"
post "DISPLAY-002" "LG UltraFine 32UN880"       "displays"     72990.00   7  "32 inch 4K, ergo arm"
post "DISPLAY-003" "BenQ PD3226G"               "displays"     94990.00   3  "32 inch 4K, designer monitor"

post "STORAGE-001" "Samsung T9 Portable SSD 2TB" "storage"     19999.00  45  "USB 3.2 Gen 2x2, 2000MB/s"
post "STORAGE-002" "WD Black SN850X 4TB"         "storage"     34999.00  16  "NVMe Gen4 internal SSD"

echo
echo "created: $created   already existed: $duplicate   failed: $failed"
[ "$failed" -eq 0 ]
