#!/bin/bash
#
# Runs ONCE, on the very first start of an empty pgdata volume.
# Editing this file later has no effect until the volume is destroyed:
#     docker compose --profile db down -v
#
# This is a .sh rather than a .sql because Postgres executes .sql files
# literally - it has no way to expand an environment variable. A shell
# script can, which is what keeps the passwords out of the repository.
#
# Passwords arrive from docker/postgres/.env via env_file in compose.

set -euo pipefail

: "${CATALOG_LOCAL_PASSWORD:?must be set - see docker/postgres/.env.example}"
: "${CATALOG_DEV_PASSWORD:?must be set - see docker/postgres/.env.example}"
: "${CATALOG_QA_PASSWORD:?must be set - see docker/postgres/.env.example}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
    CREATE USER catalog_local_user WITH PASSWORD '${CATALOG_LOCAL_PASSWORD}';
    CREATE DATABASE catalog_local OWNER catalog_local_user;

    CREATE USER catalog_dev_user WITH PASSWORD '${CATALOG_DEV_PASSWORD}';
    CREATE DATABASE catalog_dev OWNER catalog_dev_user;

    CREATE USER catalog_qa_user WITH PASSWORD '${CATALOG_QA_PASSWORD}';
    CREATE DATABASE catalog_qa OWNER catalog_qa_user;

    -- Postgres grants CONNECT on every new database to PUBLIC, so without
    -- these revokes any role in the cluster can open a connection to any
    -- database in it. Owning the database does not prevent that.
    REVOKE CONNECT ON DATABASE catalog_local FROM PUBLIC;
    REVOKE CONNECT ON DATABASE catalog_dev   FROM PUBLIC;
    REVOKE CONNECT ON DATABASE catalog_qa    FROM PUBLIC;

    GRANT CONNECT ON DATABASE catalog_local TO catalog_local_user;
    GRANT CONNECT ON DATABASE catalog_dev   TO catalog_dev_user;
    GRANT CONNECT ON DATABASE catalog_qa    TO catalog_qa_user;
EOSQL

# Owning a database is not the same as owning the schema inside it. Since
# Postgres 15 the public schema is owned by pg_database_owner and is no
# longer writable by PUBLIC, so Flyway could not create tables without
# these grants. They must be run inside each database.
for pair in "catalog_local:catalog_local_user" \
            "catalog_dev:catalog_dev_user" \
            "catalog_qa:catalog_qa_user"; do
    db="${pair%%:*}"
    role="${pair##*:}"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" \
         -c "GRANT ALL ON SCHEMA public TO ${role};"
done

echo "initdb: created catalog_local, catalog_dev, catalog_qa"
