#!/usr/bin/env bash
#
# Generates the self-signed certificate the local proxy serves.
#
# The certificate and key are gitignored - they are per-machine, and a
# private key is a private key even when self-signed. Run this once after
# cloning, then trust the certificate (see the end of this script).

set -euo pipefail

cd "$(dirname "$0")"
mkdir -p certs

# 397 days, deliberately. Since September 2020 macOS and Safari reject
# any TLS server certificate valid for more than 398 days, and the error
# they give does not explain why.
openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout certs/catalog.key \
    -out    certs/catalog.crt \
    -days   397 \
    -config openssl.cnf

chmod 600 certs/catalog.key
chmod 644 certs/catalog.crt

echo
openssl x509 -in certs/catalog.crt -noout -subject -dates -ext subjectAltName

cat <<'EOF'

Generated. Two things left:

1. Trust it, so the browser stops warning:

     sudo security add-trusted-cert -d -r trustRoot \
       -k /Library/Keychains/System.keychain \
       "$(pwd)/certs/catalog.crt"

   To remove it later:

     sudo security delete-certificate -c catalog.com \
       /Library/Keychains/System.keychain

2. Make sure /etc/hosts points the names at this machine:

     127.0.0.1  catalog.com dev.catalog.com qa.catalog.com

EOF
