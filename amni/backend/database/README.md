# AMNI development database

PostgreSQL runs in a single Docker container. The frontend and future FastAPI
application can run on the host to keep the initial development setup small.
This setup requires no hosted database or AWS account.

## Start

From the repository root:

```sh
cd amni
```

`amni/.env` contains the local database settings and is automatically read by
Compose. This workspace has a generated database password configured. The file
is Git-ignored and readable only by its owner.

On another machine, create `amni/.env` locally and set `POSTGRES_DB`,
`POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT`. Use `amni` for the
database and user, `5433` for the port, and a long random password. Compose
refuses to start with an empty password.

```sh
docker compose up -d --wait db
docker compose ps
```

The first start downloads the PostgreSQL image. Database files are stored in the
named Docker volume `amni_postgres_data`.

## Development resource limits

| Setting | Initial value |
| --- | --- |
| Container memory cap | 512 MiB |
| CPU cap | 1 CPU |
| PostgreSQL shared buffers | 64 MiB |
| Work memory | 2 MiB per operation |
| Maintenance work memory | 32 MiB |
| Maximum database connections | 20 |
| Host address | `127.0.0.1:5433` by default |

These are starting limits for a small development workload. The memory cap is
not a reservation or a guarantee that every workload will fit. Inspect actual
usage with `docker stats` as data and queries grow. The database stays on the
local machine, and the container does not automatically restart after stopping.

PostgreSQL 18 uses a version-specific data directory beneath
`/var/lib/postgresql`; the volume mounts that parent directory, following the
[official image documentation](https://hub.docker.com/_/postgres).

## Inspect the database

From `amni/`, open the PostgreSQL command-line client inside the running container:

```sh
docker compose exec db sh -c 'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Useful `psql` commands:

```text
\l       List databases
\dt      List application tables
\q       Exit
```

The first migration creates `users`, `sessions`, `issue_categories`, and `cases`,
plus Alembic’s version table. Open [schema.sql](schema.sql) to inspect the SQL and
see the [backend guide](../README.md) for model details and migration commands.
Assignment history, resolutions, notifications, and FastAPI endpoints come next.

The image creates an administrative database user on first initialization.
A restricted application role will be added when backend database access is
implemented. Changing `.env` credentials later does not change users or passwords
already stored in an initialized volume.

## Stop and resume

```sh
docker compose stop db
docker compose start db
```

Stopping releases the running container's resources while retaining its data.
`docker compose down` also preserves the named volume. Adding `-v` removes the
volume and its database contents.

## Backend connection details

For a backend running on the host, use `127.0.0.1`, the configured host port
(default `5433`), and the database name/user/password from `.env`. For a backend
container added to this Compose project later, use hostname `db` and port `5432`.

`docker-compose.prod.yml` is still a placeholder; this configuration is for local
development only.
