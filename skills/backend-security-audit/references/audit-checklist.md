# Backend Security Audit Checklist

Use this checklist to keep coverage broad while auditing a user's authorized backend codebase. Treat it as prompts for investigation; confirm every reported issue against actual code.

## Discovery

- Entry points: HTTP routes, RPC handlers, GraphQL resolvers, webhooks, background workers, cron jobs, CLIs, queues.
- Security middleware: auth, authorization, CORS, CSRF, rate limiting, request parsing, error handling, logging.
- Data layer: ORM models, raw queries, migrations, row-level security, tenant/org scoping, transactions.
- Config: `.env.example`, deployment manifests, Dockerfiles, CI, cloud config, framework config, reverse proxy config.
- Dependencies: package manifests and lockfiles, security-sensitive libraries, deprecated packages.

## High-Impact Vulnerability Classes

- Auth bypass: route missing auth middleware, optional session accepted as trusted identity, broken callback state/nonce, password reset token misuse.
- Authorization flaws: IDOR, missing tenant/org scope, trusting client-supplied role/user/org IDs, admin checks only in UI, mass assignment of privileged fields.
- Injection: raw SQL/NoSQL with user input, shell command construction, template injection, unsafe eval/dynamic import, path traversal.
- SSRF: fetching user-controlled URLs, webhook URL testers, image/document importers, redirect-following clients, access to internal IP ranges or metadata services.
- File upload abuse: trusting filename/MIME, writing outside intended directory, public executable uploads, oversized uploads, dangerous archive extraction.
- Secret exposure: committed secrets, secrets in logs/errors/responses, long-lived tokens, weak API-key hashing, service-role keys exposed to clients.
- Session/token weakness: missing cookie flags, weak JWT validation, no token rotation, long-lived reset/invite tokens, logout not invalidating server-side sessions.
- CSRF/CORS: credentialed cross-origin access with broad origins, state-changing routes without CSRF protection when cookie-authenticated.
- Webhook trust: missing signature verification, no timestamp/replay checks, trusting event payload state for billing or permissions.
- Data leakage: returning password hashes/tokens/private fields, verbose errors, debug endpoints, stack traces, OpenAPI exposing internal endpoints.
- Rate limit gaps: login, signup, password reset, email verification, OTP, invite, expensive search/export endpoints.
- Dependency and supply chain: known vulnerable versions, lockfile missing, install scripts in risky packages, abandoned security-critical packages.
- Deployment issues: debug mode in production, public database/admin ports, overly permissive IAM, public buckets, containers running as root, missing TLS assumptions.

## Review Tactics

- Trace each sensitive operation from route to service to database query and response.
- Search for risky terms: `TODO security`, `bypass`, `admin`, `role`, `tenant`, `orgId`, `userId`, `raw`, `queryRaw`, `exec`, `spawn`, `eval`, `redirect`, `fetch(`, `axios`, `upload`, `webhook`, `secret`, `token`, `cookie`, `cors`.
- Compare route lists against auth middleware; unauthenticated routes should be intentional.
- Compare database queries against tenant/user ownership requirements.
- Inspect tests for negative authorization cases; missing tests are not a finding alone, but increase confidence in risky code paths.
- Check both server and deployment config when a protection depends on infrastructure.

## Reporting Rules

- Prefer confirmed, code-backed findings over speculation.
- Include file paths and line numbers whenever possible.
- Explain uncertainty explicitly when behavior depends on missing production config.
- Do not include weaponized exploit payloads. Describe abuse scenarios defensively.
- After reporting, ask whether to fix the findings before editing code.
