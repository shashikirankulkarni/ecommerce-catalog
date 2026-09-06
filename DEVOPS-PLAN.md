# E-commerce Catalog Service — DevOps Learning Track

## Context

Build a fresh Spring Boot product catalog service in `~/Documents/ecommerce-catalog`, used as the vehicle for learning the full DevOps chain end to end: artifact scanning, secret remediation, environment separation, Git workflow, GitHub Actions, self-hosted runners, and deployment.

The method is deliberate: **ship it insecure, scan it, read the reports, then fix what the scanners actually found.** Hardcoded credentials come first on purpose so that remediation has something real to remediate.

Nothing in `~/Projects/b2b-order-platform` is touched — that existing catalog service (Boot 3.3.4, zero git commits) stays as-is.

Guiding principle throughout: **simplest thing that works now, improve later.** Deferred improvements are listed at the end so they are recorded decisions, not oversights.

---

## Verified environment

| Item | State |
|---|---|
| Hardware | Apple M4, 16 GB RAM, 10 cores, 229 GB free |
| JDK | Oracle 21.0.9 arm64 — the only JDK installed |
| Maven | `/opt/homebrew/bin/mvn` |
| Docker Desktop | Installed, **daemon stopped** — must be started |
| `gh` CLI | Authenticated as `shashikirankulkarni`, scopes `repo`, `workflow` |
| Scanners | None installed; all available via brew |
| Spring Boot | Initializr default `4.1.1.RELEASE`; 3.x no longer offered |
| springdoc | `3.1.0` — verified Boot 4 compatible |
| IDE | Spring Tools for Eclipse 5.3.0 at `/Applications/SpringToolsForEclipse.app` |

---

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Framework | Spring Boot 4.1.1, Java 21, Maven | Java 21 is the only JDK present |
| API docs | springdoc 3.1.0 | Only 3.x supports Boot 4 |
| Database | PostgreSQL + Flyway, `ddl-auto: validate` | Flyway genuinely enabled — the old project had `flyway.enabled: false` *and* `ddl-auto: update`, which is contradictory |
| **Packaging** | **Executable JAR**, `scp`'d to servers | Matches the original "scan the JAR/WAR" goal; simpler start. Images deferred |
| Servers | Docker containers used **as VMs** (Ubuntu + JRE + sshd + supervisord) | Real hosts, real SSH, no image-build complexity yet |
| Runners | **One** self-hosted runner, its own container | Simplest; never co-located with an app server |
| Repo | **Private** | Deliberate fake secrets must not reach a public repo |
| Branching | Branch-per-environment with a PR gate at every hop | User's explicit choice; PR history becomes the audit trail |

> All hardcoded secrets use values that match scanner regexes but are unmistakably fake — `AKIAIOSFODNN7EXAMPLE` is AWS's own documentation example key. Once committed they persist in git history even after removal; that permanence is one of the lessons, and fake data must be what teaches it.

---

## Topology

```
catalog-net-nonprod                      catalog-net-prod
├── catalog-postgres-nonprod  :5433      ├── catalog-postgres-prod  :5434
│     ├── catalog_local                  │     └── catalog_prod
│     ├── catalog_dev                    └── srv-prod   :8083  ssh :2224
│     └── catalog_qa
├── srv-dev   :8081  ssh :2222
├── srv-qa    :8082  ssh :2223
└── catalog-runner        (attached to both networks — see caveat)

Mac = local environment → app from Eclipse on :8080, DB at localhost:5433
```

Every database has its own user and password, so prod credentials genuinely do not work against dev.

**Tier separation**: app servers hold no data; database servers run no application code. Losing an app server costs a redeploy; losing a database server is the real disaster.

**Prod isolation**: `srv-dev` cannot resolve `catalog-postgres-prod` — it fails at the *network* layer, not the auth layer. Docker networks demonstrate this convincingly at zero cost.

### Resource budget

| Container | Idle |
|---|---|
| `catalog-postgres-nonprod` / `-prod` | ~200 MB each |
| `srv-dev` / `srv-qa` / `srv-prod` (JRE + app) | ~350 MB each |
| `catalog-runner` | ~200 MB idle, **1–2 GB building** |

Everything up ≈ 2.5 GB. Use compose profiles to run only what is needed:

```bash
docker compose --profile db  up -d     # daily coding: ~400 MB
docker compose --profile dev up -d     # + runner + srv-dev
docker compose --profile all up -d     # full pipeline demo
```

Set `restart: unless-stopped` on the databases; deliberately omit it on the runner so it does not idle in the background.

### OS and architecture

Every server is **Linux** — Docker Desktop runs containers inside a LinuxKit VM, and Windows containers cannot run on macOS at all. Three distinct contexts exist:

| Context | OS | Arch |
|---|---|---|
| `local` — Eclipse / `mvn` on the Mac | macOS 15.6 | arm64 |
| `srv-*`, Postgres, runner containers | Linux (Ubuntu 24.04) | arm64 |
| GitHub-hosted runners | Linux (Ubuntu) | **x86_64** |

Rows 1 and 2 differ by coreutils — macOS ships **BSD**, Linux ships **GNU**. `sed -i` and `date` flags diverge, so scripts that work locally can fail on the runner.

### Access

All servers are **headless** — no GUI, terminal only. Two access paths:

```bash
ssh deploy@localhost -p 2222        # what CI uses
docker exec -it srv-dev bash        # out-of-band rescue, like a cloud console
```

`docker exec` is the way back in after breaking `sshd_config` — worth breaking once on purpose.

The OS has no desktop, but services on it serve web UIs: Swagger at `:8081/swagger-ui.html`, health at `:8081/actuator/health`, reached from the Mac's browser.

---

## Branching and pipeline model

```
feature/product-category-search
        │ PR + CI
        ▼
      main       ← integration branch, no deploy
        │ PR + CI
        ▼
      dev        ← merge → build + deploy to srv-dev
        │ PR + CI
        ▼
       qa        ← merge → build + deploy to srv-qa
        │ PR + CI
        ▼
      prod       ← merge → build + deploy to srv-prod (+ reviewer approval)
```

Two workflow files, not four:

- **`ci.yml`** — on `pull_request` into `main`/`dev`/`qa`/`prod`: `mvn verify`, gitleaks, dependency-check, grype. No deploy. This is the merge gate.
- **`deploy.yml`** — on `push` to `dev`/`qa`/`prod`. The single line `environment: ${{ github.ref_name }}` selects which environment's secrets and variables resolve, and arms the prod approval gate. Same YAML, three outcomes, no `if:` branching.

### Action matrix

| Event | Workflow | Compile | Package | Scan | Deploy |
|---|---|---|---|---|---|
| PR `feature/*` → `main` | `ci.yml` | ✅ | discarded | ✅ | ❌ |
| Merge to `main` | `ci.yml` | ✅ | discarded | ✅ | ❌ |
| PR `main` → `dev` | `ci.yml` | ✅ | discarded | ✅ | ❌ |
| **Merge to `dev`** | `deploy.yml` | ✅ | ✅ JAR | ✅ | ✅ `srv-dev` |
| PR `dev` → `qa` | `ci.yml` | ✅ | discarded | ✅ | ❌ |
| **Merge to `qa`** | `deploy.yml` | ✅ | ✅ JAR | ✅ | ✅ `srv-qa` |
| PR `qa` → `prod` | `ci.yml` | ✅ | discarded | ✅ | ❌ |
| **Merge to `prod`** | `deploy.yml` | ✅ | ✅ JAR | ✅ | ✅ `srv-prod` + approval |

PR builds produce a JAR that is deliberately discarded — they answer "is this mergeable?", nothing more.

**Runner placement**: one runner, its own container, never on an app server. Co-locating would put a JDK, Maven, the source tree and a GitHub token on a box serving traffic, and Maven's 1–2 GB build spike would contend with live requests. One runner processes one job at a time, so near-simultaneous merges queue — accepted for now.

*Known simplification*: a single runner must attach to **both** networks to deploy everywhere, making it a bridge that softens prod isolation. Deferred fix listed at the end.

**Branch protection** on all four branches: PR required, `ci.yml` green, no direct or force pushes. `prod` carries a second gate — the Environment reviewer — since PR approval and deploy approval are separate moments.

**Hotfix path**: branch from `prod`, PR back into `prod` to ship, then **back-merge into `qa`, `dev` and `main`** or the next promotion silently reverts the fix. Document this checklist in the README.

---

## Phase 0 — Prerequisites

```bash
open -a Docker
brew install trivy grype syft gitleaks dependency-check
```

## Phase 1 — Generate from Spring Initializr

```bash
mkdir -p ~/Documents/ecommerce-catalog && cd ~/Documents/ecommerce-catalog
curl https://start.spring.io/starter.zip \
  -d type=maven-project -d language=java \
  -d bootVersion=4.1.1.RELEASE -d javaVersion=21 \
  -d groupId=com.shashi -d artifactId=catalog -d name=catalog \
  -d packageName=com.shashi.catalog -d packaging=jar \
  -d dependencies=web,data-jpa,postgresql,flyway,validation,actuator,lombok,testcontainers \
  -o catalog.zip
unzip catalog.zip && rm catalog.zip
```

Add springdoc `3.1.0` (`springdoc-openapi-starter-webmvc-ui`) to `pom.xml` manually — Initializr does not offer it.

## Phase 2 — Domain + deliberately hardcoded credentials

Under `src/main/java/com/shashi/catalog/`:

| File | Purpose |
|---|---|
| `domain/Product.java` | `id`, `sku` (unique), `name`, `description`, `price` (`BigDecimal`), `category`, `stockQuantity`, `active`, `createdAt`, `updatedAt` |
| `domain/ProductRepository.java` | `JpaRepository`, finders by sku and category |
| `service/ProductService.java` | CRUD, `@Transactional` |
| `web/ProductController.java` | `/api/v1/products` — list, get, create, update, delete, search by category |
| `web/dto/ProductRequest.java` | Bean-validated input |
| `web/dto/ProductResponse.java` | Output |
| `web/GlobalExceptionHandler.java` | `@RestControllerAdvice`, RFC 7807 problem details |
| `config/OpenApiConfig.java` | springdoc metadata |

`src/main/resources/db/migration/V1__create_product_table.sql` — Flyway.

**Five deliberate secret placements**, each caught by a different tool:

| # | File | Value | Caught by | Lesson |
|---|---|---|---|---|
| 1 | `application.properties` | DB password, JWT secret | gitleaks, `trivy fs` | The obvious case |
| 2 | `config/PaymentConfig.java` | `static final String API_KEY` | `strings` on the JAR | **Compiled into the artifact** |
| 3 | `docker-compose.yml` | `POSTGRES_PASSWORD` inline | gitleaks | Infra files leak too |
| 4 | `Dockerfile` (server image) | `ENV DB_PASSWORD=` | `trivy image`, `docker history` | Baked into a layer forever |
| 5 | `.github/workflows/ci.yml` | literal token | GitHub secret scanning | CI config is source code |

```properties
spring.datasource.password=<redacted>
app.jwt.secret=dev_only_not_a_real_signing_key_0000
app.payment.stripe-key=sk_test_<redacted>
app.aws.access-key=AKIAIOSFODNN7EXAMPLE
```

Also pin **one or two knowingly outdated dependencies** so the CVE scanners return real findings rather than a clean report.

## Phase 3 — Build and scan

```bash
./mvnw clean package
syft target/catalog-0.0.1-SNAPSHOT.jar -o spdx-json > sbom.json
grype target/catalog-0.0.1-SNAPSHOT.jar -o table
dependency-check --scan target/ --format HTML --out reports/
gitleaks detect --source . --report-path reports/gitleaks.json
trivy fs --scanners vuln,secret,misconfig .
trivy image ubuntu:24.04          # base image the servers are built from
```

Then prove #2 survives into the artifact:

```bash
unzip -p target/catalog-0.0.1-SNAPSHOT.jar \
  BOOT-INF/classes/com/shashi/catalog/config/PaymentConfig.class | strings | grep sk_
```

Deleting a secret from `application.properties` feels like fixing it. A `static final String` is baked into the class constant pool — this single command reframes what artifact scanning is for.

## Phase 4 — Read the reports

Cover CVSS vs EPSS; direct vs transitive dependencies (`mvn dependency:tree` finds the real offender); false positives; reachability. Deliverable: `SECURITY-FINDINGS.md`, written from the actual output.

## Phase 5 — Remediate

Each placement gets its own fix:

| # | Fix |
|---|---|
| 1 | Environment variable — `${DB_PASSWORD}`, **no default value** |
| 2 | Constructor-injected `@ConfigurationProperties` |
| 3 | `env_file` in compose |
| 4 | Runtime env, never `ENV` in the Dockerfile |
| 5 | `${{ secrets.* }}` |

Then:

1. `.gitignore` a local `.env`; commit `.env.example` with empty keys.
2. Profiles: `application-{local,dev,qa,prod}.properties`, selected by `SPRING_PROFILES_ACTIVE`. Only `local` ships usable defaults. Note `localhost:5433` (local) vs `catalog-postgres-nonprod:5432` (containers) — a classic "works on my machine" source.
3. Upgrade the vulnerable dependencies; re-run Phase 3 and **diff the reports**.
4. Show the secrets still live in git history; remediate with `git filter-repo`.
5. Add a **gitleaks pre-commit hook** so it cannot recur.

**`${DB_PASSWORD:changeme}` is a trap** — the app boots happily on the fallback and you find out in production. Omit the default so startup fails loudly.

### Where secrets live after cleanup

| Context | Storage | Reaches the app via |
|---|---|---|
| local | gitignored `.env`; `.env.example` committed | compose, or Eclipse Run Config → Environment |
| CI | **GitHub Environment Secrets** — same name per dev/qa/prod | `${{ secrets.DB_PASSWORD }}` |
| runtime | `/opt/catalog/.env`, `chmod 600`, owned by `deploy`, rewritten each deploy | app service reads it |

**One place you manage.** The server file is *generated* by each deploy, never hand-edited — the same relationship as source code and a compiled binary. Rotation is a single action: update the GitHub secret, redeploy.

Secrets vs variables: `secrets.*` for passwords and keys (masked, write-only); `vars.*` for hostname, port, profile, DB URL (visible, keeps logs debuggable).

Caveat to teach: env vars are not truly secret on a host — `/proc/<pid>/environ` exposes them to root.

**Cleanup is three steps, in order**: **rotate** at the source (the only step that revokes access) → **remove** from code and history → **prevent** with a hook. Skipping rotation is the common real-world failure.

## Phase 6 — Git and GitHub

```bash
git init && git add . && git commit -m "Initial catalog service"
gh repo create ecommerce-catalog --private --source=. --push
git branch dev && git branch qa && git branch prod && git push --all
```

Then configure branch protection on all four branches, and create GitHub Environments `dev`, `qa`, `prod` with per-environment secrets and variables. Required reviewer on `prod`.

> No `Co-Authored-By: Claude` trailer on commits.

## Phase 7 — CI on GitHub-hosted runners

`.github/workflows/ci.yml`:

- Trigger on `pull_request` into `main`/`dev`/`qa`/`prod`
- `actions/setup-java@v4` (temurin 21) with Maven cache
- `mvn verify` — unit tests plus Testcontainers-backed integration tests
- gitleaks, dependency-check, grype steps
- Upload SARIF to the GitHub Security tab
- Fail on HIGH/CRITICAL

Answers *where the build runs*: GitHub's ephemeral VM, fresh per job, destroyed after.

## Phase 8 — Self-hosted runner

`docker/runner/Dockerfile` — Ubuntu 24.04 + `actions/runner` (linux-**arm64** package), JDK 21, Maven.

Register with a token from `gh api`, label `self-hosted,linux,arm64,catalog`, then route a job with `runs-on: [self-hosted, catalog]` and watch it land there instead of on GitHub.

Cover: registration tokens and label routing; **persistent vs ephemeral** runners and how workspace state leaks between jobs; runner groups; and why self-hosted runners on public repos are dangerous (a fork PR executes arbitrary code on your machine).

## Phase 9 — Servers and deployment to dev

`docker/server/Dockerfile` — built **once per server**, not per deploy:

```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
      openjdk-21-jre-headless openssh-server supervisor
# supervisord manages sshd + the catalog app, standing in for systemd
```

The JRE is installed once, when this image is built. Only the **JAR** moves on each deploy.

`deploy.yml` deploy job:

```yaml
environment: ${{ github.ref_name }}      # dev | qa | prod
steps:
  - run: |                                # render .env on the runner
      umask 077                           # 600, not 644
      cat > catalog.env <<EOF
      SPRING_PROFILES_ACTIVE=${{ vars.SPRING_PROFILE }}
      SPRING_DATASOURCE_URL=${{ vars.DB_URL }}
      DB_PASSWORD=${{ secrets.DB_PASSWORD }}
      JWT_SECRET=${{ secrets.JWT_SECRET }}
      EOF
  - run: |
      scp -P ${{ vars.SSH_PORT }} target/catalog-*.jar catalog.env \
          deploy@${{ vars.DEPLOY_HOST }}:/opt/catalog/
      ssh -p ${{ vars.SSH_PORT }} deploy@${{ vars.DEPLOY_HOST }} \
          'chmod 600 /opt/catalog/.env && supervisorctl restart catalog'
  - if: always()
    run: shred -u catalog.env             # persistent runner keeps its workspace
```

Three security details worth noticing: `umask 077` before writing, so the file is never briefly world-readable; `scp` rather than `ssh host "echo $PASSWORD > file"`, which would expose the password in the remote process list; and `if: always()` cleanup, because a persistent runner's workspace survives into the next job.

Flyway applies pending migrations on startup. Health gate:

```bash
curl -f localhost:8081/actuator/health   # retry until {"status":"UP"}
```

On failure, restore the previous JAR and fail the workflow — dev stays on the last good build.

## Phase 10 — Add qa and prod, and promote

Create the `qa` and `prod` branches, protect them, and extend `deploy.yml`'s branch mapping. Wire the GitHub Environments with a required reviewer on prod, so the job pauses with a **Review deployments** button before touching production.

Exercise: point `application-dev.properties` at the prod database and confirm it fails at the network layer, not the auth layer.

---

## Verification

1. `./mvnw verify` passes; Testcontainers starts a throwaway Postgres.
2. `curl localhost:8080/api/v1/products` returns data; Swagger UI at `/swagger-ui.html`; `/actuator/health` reports `UP`.
3. `strings` on the JAR finds the Stripe key **before** Phase 5 and nothing after.
4. `gitleaks detect` clean on the working tree; HIGH/CRITICAL count measurably lower than the Phase 3 baseline.
5. Opening a PR triggers `ci.yml`; a deliberately reintroduced vulnerable dependency fails the build and blocks the merge.
6. `gh run list` shows one job on a GitHub-hosted runner and one on `self-hosted,catalog`.
7. Merging `main` → `dev` deploys automatically; `srv-dev:8081/actuator/health` responds.
8. Merging `qa` → `prod` **pauses** for approval before deploying.
9. `docker exec -it srv-dev bash` then `getent hosts catalog-postgres-prod` resolves nothing.

---

## Deferred improvements

Each is a deliberate later step, not an oversight:

| Improvement | Fixes |
|---|---|
| **Docker images + GHCR** | Image-layer CVE scanning (OS packages, OpenSSL, glibc), immutable artifacts, one-command rollback, servers needing only Docker |
| **GitHub Packages / Nexus** for the JAR | Restores build-once-deploy-many — a Maven repo is a registry, no Docker needed |
| Runner **pool** (2–3 runners) | Jobs queueing behind one another |
| Separate **prod deploy agent** on `catalog-net-prod` | The single runner bridging both networks; the agent carries no build tooling |
| **Ephemeral** runners (`--ephemeral`) | State leaking between jobs |
| **Vault / AWS Secrets Manager** | Secret copies at rest on the server and in the process environment |
| **OIDC** instead of stored credentials | Long-lived secrets in GitHub entirely |
| Runner on a real cloud VM | Provisioning, firewalls, TLS, DNS |

## Open items

- A `frontend/` module later — React vs JSP undecided. JSP would force WAR packaging and give up Boot's executable jar; React would want Wild Web Developer in Eclipse, or VS Code alongside.
