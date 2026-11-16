# Planned architecture

Only the Next.js frontend is implemented in this iteration. The remaining
components below describe the intended architecture, not running services.

```text
Browser (Next.js / React / TypeScript / Tailwind)
    │ HTTPS + authenticated WebSocket connection
    ▼
Nginx reverse proxy
    ├── Frontend
    └── FastAPI
          ├── PostgreSQL: users, roles, cases, updates, audit records
          ├── Knowledge-base search and article suggestions
          └── Restricted diagnostic workers: Linux, DNS, TCP, TLS, HTTP
```

Backend implementation should enforce authorization on every case operation,
record audit events, and authenticate and authorize WebSocket subscriptions.
Diagnostic workers need explicit target validation, network restrictions,
timeouts, and output limits before any real checks are enabled.

Use Docker Compose for local services and Nginx for HTTPS termination. Start
with one appropriately sized EC2 instance for a cost-conscious demonstration.
Add RDS PostgreSQL for managed database operations when needed. CloudWatch can
collect operational logs; S3 can hold attachments; Secrets Manager can manage
runtime secrets. Evaluate ECS when container orchestration is justified.

GitHub Actions should run frontend type checking and builds, backend tests once
the backend exists, and image/deployment checks. No AWS resources, live diagnostic
workers, authentication, or CI deployment jobs are created by this design change.
