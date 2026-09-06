# Security Findings — Phase 3 Baseline

**Artifact:** `catalog-0.0.1-SNAPSHOT.jar` (61 MB, 98 bundled jars)
**Scanned:** 2026-09-05
**Stack:** Spring Boot 4.1.1, Java 21, macOS 15.6 arm64
**Tools:** grype 0.118.0 · syft 1.51.1 · trivy 0.74.0 · gitleaks 8.30.1

> **All credentials in this document are fabricated.** They were planted deliberately so the
> scanners had something real to find. No live system, account or key is exposed. The values are
> reproduced in full because *which ones the scanners miss* is the point.

This is the **baseline**. Phase 5 remediates it, re-runs the same tools, and the proof of
remediation is the diff between that report and this one.

---

## Summary

| Metric | Count |
|---|---|
| CVEs in dependencies | 13 |
| Rated Critical | 6 |
| On the CISA KEV list | 2 |
| Inherited from Spring Boot (not planted) | 3 |
| Credentials planted | 13 |
| Credentials detected by scanners | 3 |
| SBOM components | 100 |

---

## 1. What was scanned

Four tools, two targets. `grype` and `syft` read the **packaged JAR** — the artifact that would
actually be deployed. `trivy` and `gitleaks` read the **source tree**. That split matters: a
scanner pointed at source sees what you wrote; a scanner pointed at the artifact sees what you
shipped. They are not the same thing.

| Tool | Version | Target | Looks for | Findings |
|---|---|---|---|---|
| syft | 1.51.1 | packaged JAR | software bill of materials | 100 components |
| grype | 0.118.0 | packaged JAR | known CVEs in dependencies | 13 |
| trivy | 0.74.0 | source tree | CVEs, secrets, misconfiguration | 13 + 2 secrets |
| gitleaks | 8.30.1 | source tree | hardcoded secrets | 6 |

**OWASP dependency-check was not run.** It requires an NVD API key; without one the first run
downloads the entire National Vulnerability Database at throttled speed and routinely times out.
grype and trivy ship pre-built databases and have no such dependency.

---

## 2. Vulnerable dependencies

Ten of the thirteen came from three dependencies pinned to known-bad versions on purpose. **The
other three arrived on their own**, inside Spring Boot 4.1.1, in a project generated the same day
it was scanned. That is the honest baseline of any real build: you inherit your framework's
vulnerabilities from the first commit.

### Planted deliberately (10)

| Package | Version | CVE | Severity | CVSS | EPSS | Fixed in | Issue |
|---|---|---|---|---|---|---|---|
| log4j-core | 2.14.1 | CVE-2021-44228 | Critical **KEV** | 10.0 | 100.0% | 2.15.0 | Log4Shell — RCE via JNDI lookup |
| log4j-core | 2.14.1 | CVE-2021-45046 | Critical **KEV** | 9.0 | 100.0% | 2.16.0 | Incomplete Log4Shell fix |
| log4j-core | 2.14.1 | CVE-2021-45105 | High | 5.9 | 100.0% | 2.17.0 | DoS via self-referential lookups |
| commons-text | 1.9 | CVE-2022-42889 | Critical | 9.8 | 99.9% | 1.10.0 | Text4Shell — RCE via interpolation |
| log4j-core | 2.14.1 | CVE-2021-44832 | Medium | 6.6 | 97.9% | 2.17.1 | RCE via JDBC appender |
| commons-collections | 3.2.1 | CVE-2015-7501 | Critical | 9.8 | 85.6% | 3.2.2 | Deserialization RCE |
| commons-collections | 3.2.1 | CVE-2015-6420 | High | 9.8 | 17.9% | 3.2.2 | Deserialization of untrusted data |
| log4j-core | 2.14.1 | CVE-2026-34480 | Medium | 7.5 | 1.0% | 2.25.4 | XmlLayout emits invalid XML |
| log4j-core | 2.14.1 | CVE-2025-68161 | Medium | 4.8 | 0.8% | 2.25.3 | Socket appender skips TLS hostname check |
| log4j-core | 2.14.1 | CVE-2026-34477 | Medium | 5.9 | 0.4% | 2.25.4 | Incomplete fix for the above |

### Inherited from Spring Boot 4.1.1 (3)

| Package | Version | CVE | Severity | CVSS | EPSS | Fixed in | Issue |
|---|---|---|---|---|---|---|---|
| tomcat-embed-core | 11.0.24 | CVE-2026-65905 | Critical | 9.8 | 0.8% | 11.0.25 | DIGEST authenticator capture-replay |
| tomcat-embed-core | 11.0.24 | CVE-2026-65182 | Critical | 9.1 | 0.6% | 11.0.25 | Security constraint bypass |
| tomcat-embed-core | 11.0.24 | CVE-2026-68525 | Critical | — | 0.6% | 11.0.25 | FORM auth bypass, POST vs GET |

---

## 3. Severity is not urgency

Six findings are labelled Critical. Treating them as equally urgent would be a mistake.

- **CVSS** scores how bad exploitation would be.
- **EPSS** estimates the probability exploitation is actually attempted in the next 30 days.
- **KEV** is CISA's catalogue of vulnerabilities confirmed exploited in the wild.

They disagree constantly:

| CVE | CVSS | EPSS | Reading |
|---|---|---|---|
| CVE-2021-44228 (Log4Shell) | 10.0 | **100.0%** | Critical *and* actively exploited |
| CVE-2026-65905 (Tomcat) | 9.8 | **0.8%** | Same severity label, ~125× less likely |
| CVE-2021-44832 (log4j) | 6.6 | **97.9%** | Only Medium, yet exploited constantly |

A queue sorted by CVSS alone works on these in the wrong order. CVE-2021-44832 is rated *below*
the Tomcat findings and is roughly 120× more likely to be attacked.

---

## 4. Present ≠ exploitable

A scanner reports what is on the classpath. It does not know whether your code can reach it.

**The ten planted CVEs are unreachable.** No application class imports `commons-collections`,
`commons-text` or `log4j-core`. The jars sit in `BOOT-INF/lib/` and are never loaded. Log4Shell
needs attacker-controlled text to reach a Log4j2 logger; this application logs through Logback.
There is no path.

**The three inherited CVEs are reachable.** Every HTTP request passes through `tomcat-embed-core`.
They score lower on likelihood but sit directly in the request path.

So the ranking flips depending on the question asked. By exploit likelihood, Log4Shell dominates.
By reachability *in this application*, the Tomcat findings are the only ones an attacker could
touch. Both readings are correct; triage needs both, and neither is what the scanner hands you.

**Unreachable is not ignorable.** A future dependency that pulls `log4j-core` into the logging path
converts a dormant finding into a live one with no visible change to your own code. Unused
vulnerable dependencies get removed because they are unused — not because they are harmless.

---

## 5. What the secret scanners missed

Thirteen credentials were planted across four files. Two dedicated secret scanners, run together,
found **three**.

| Credential | Location | gitleaks | trivy | Why |
|---|---|---|---|---|
| Stripe test key `sk_test_…` | `application.properties:46` | **FOUND** | **FOUND** | Distinctive `sk_` prefix |
| Stripe live key `sk_live_…` | `PaymentConfig.java:24` | **FOUND** | **FOUND** | Same rule, matched in Java too |
| AWS access key ID `AKIA…` | `application.properties:52` | **FOUND** | missed | gitleaks has an AWS rule |
| AWS secret access key | `application.properties:53` | missed | missed | 40 random chars, no prefix |
| Database password | `application.properties:23` | missed | missed | Reads as English, low entropy |
| JWT signing secret | `application.properties:45` | missed | missed | No standard format |
| Stripe webhook secret `whsec_…` | `application.properties:47` | missed | missed | Prefix not in default ruleset |
| Webhook signing secret | `PaymentConfig.java:26` | missed | missed | Same gap |
| Merchant ID `acct_…` | `PaymentConfig.java:28` | missed | missed | Identifier, not obviously a credential |
| Postgres superuser password | `docker-compose.yml:19` | missed | missed | Plain YAML assignment |
| 3 × per-env DB passwords | `initdb/00-create-databases.sql` | missed | missed | SQL `CREATE USER … PASSWORD` not scanned |

### The allowlist trap

The AWS key was originally `AKIAIOSFODNN7EXAMPLE` — Amazon's own published documentation example,
chosen *because* it matches the AWS pattern exactly. gitleaks reported nothing. It **allowlists
that exact string by name**, since it appears in every AWS tutorial and would otherwise generate
endless false positives.

Swapping it for a realistic fake produced an immediate hit:

```
aws.access.key  = AKIAIOSFODNN7EXAMPLE   → no finding (allowlisted)
aws.access.key2 = AKIA<redacted>   → aws-access-token
```

The allowlist is not wrong — it is correct and necessary. The lesson is that **detection depends on
shape**. Anything with a distinctive prefix gets caught. A password, a JWT secret, or the
40-character half of an AWS pair that actually grants access has no shape to match, and passes
straight through.

**A clean gitleaks run is not evidence of a clean repository.**

---

## 6. Secrets survive into the artifact

A JAR is a zip file. Every credential in the source is readable from the shipped artifact with no
source access, no decompiler, and no privileged position — only the file.

```
$ unzip -p catalog-0.0.1-SNAPSHOT.jar BOOT-INF/classes/application.properties

spring.datasource.password=<redacted>
app.jwt.secret=<redacted>
app.payment.stripe-key=sk_test_<redacted>
app.aws.access-key=AKIA<redacted>
app.aws.secret-key=<redacted>
```

### Deleting the field does not delete the secret

`PaymentConfig` holds its keys in `static final String` fields. In Java those are **compile-time
constants**, so the compiler inlines them into every class that references them.
`PaymentService.java` never writes the key — but its bytecode contains it:

```
$ javap -c -p com.shashi.catalog.payment.PaymentService

public java.lang.String buildAuthorizationHeader();
  Code:
     0: ldc  #9   // String Bearer sk_live_<redacted>
     2: areturn
```

There is no field lookup at runtime — the finished string sits in the constant pool. Removing the
field from `PaymentConfig.java` leaves the inlined copies untouched until a **full** rebuild. On an
incremental or cache-backed CI build, the "removed" secret ships anyway. That is a documented way
credentials outlive the commit that deleted them.

### macOS `strings` cannot read `.class` files

Java's `0xCAFEBABE` magic number is also the Mach-O universal binary magic, so BSD `strings`
misparses the header and aborts:

```
strings: fat file: ... truncated or malformed
```

GNU `strings` on Linux reads it fine. A verification step that passes on the CI runner can fail on
a developer's Mac for reasons unrelated to the code. Portable alternative:

```bash
LC_ALL=C tr -c '[:print:]' '\n' < File.class | grep -a sk_
```

---

## 7. The reports are themselves sensitive

Trivy, scanning the working tree, flagged eight secrets in a file that had not existed an hour
earlier:

```
reports/gitleaks.json   secrets=8   stripe-secret-token
```

Scanner output quotes the secrets it finds, in plaintext, with exact file and line. Obvious once
stated, routinely missed in practice — which is how scan reports end up committed, attached to
tickets, or published as public CI artifacts.

`reports/` is now in `.gitignore`. **A scan report is as sensitive as the secrets it describes.**

---

## 8. Remediation plan

Ordered deliberately. **Rotation comes first** — it is the only step that actually revokes access.
Removing a secret from code while the credential stays valid changes nothing for an attacker who
already copied it.

| # | Step | Why |
|---|---|---|
| 1 | Rotate every exposed credential at its source | The only step that revokes access. Skipping it is the common real-world failure |
| 2 | Gitignore `reports/` before `git init` | Scan output contains the secrets verbatim |
| 3 | Move properties to env vars, **no defaults** | `${DB_PASSWORD}`, never `${DB_PASSWORD:changeme}` — a fallback boots the app on the wrong credential |
| 4 | Replace `static final` constants with `@ConfigurationProperties` | Stops the value being compiled into bytecode |
| 5 | `mvn clean package`, then re-grep the JAR | Incremental builds retain inlined copies |
| 6 | Drop `commons-collections`, `commons-text`, `log4j-core`; bump Tomcat to 11.0.25 | Clears all 13 CVEs |
| 7 | `management.endpoints.web.exposure.include=health,info`, drop `show-values` | Exposed, it returns every credential over unauthenticated HTTP |
| 8 | `git filter-repo`, verify with `gitleaks detect` | Deleting a file does not remove it from earlier commits |
| 9 | gitleaks pre-commit hook | Prevention, so it cannot recur silently |
| 10 | Re-run every scanner and diff against this baseline | The proof is the difference between two reports |

---

## 9. Reproducing this

```bash
# build the artifact
./mvnw clean package

# inventory and CVEs, against the shipped JAR
syft  target/catalog-0.0.1-SNAPSHOT.jar -o spdx-json > reports/sbom.spdx.json
grype target/catalog-0.0.1-SNAPSHOT.jar -o table     > reports/grype.txt

# source tree: CVEs, secrets, misconfiguration
trivy fs --scanners vuln,secret,misconfig --skip-dirs target .

# secrets. use `dir` before git init; `detect` scans history after
gitleaks dir . --report-path reports/gitleaks.json --report-format json

# prove the secret shipped inside the artifact
unzip -p target/catalog-*.jar BOOT-INF/classes/application.properties | grep -i password
```
