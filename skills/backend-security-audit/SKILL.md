---
name: backend-security-audit
description: Defensive backend security review for source code, API servers, auth flows, database access, dependency configuration, secrets handling, file uploads, webhooks, background jobs, and deployment settings. Use when Codex is asked to audit, review, deep research, harden, or find vulnerabilities in a user's own backend or authorized codebase, and to report findings before making fixes.
---

# Backend Security Audit

## Overview

Perform a defensive, evidence-led backend security audit. Find as many real vulnerabilities and risky patterns as possible, report them clearly to the user, then ask whether to implement fixes.

Use this only on systems the user owns or is authorized to assess. Do not provide exploit payloads, attack playbooks, or instructions for compromising third-party systems.

## Audit Workflow

1. Establish scope from the repository:
   - Identify backend entry points, framework, package manager, runtime, API routes, middleware, auth/session libraries, database layer, background jobs, file storage, webhook handlers, and deployment files.
   - Read project docs, environment examples, schema files, route definitions, middleware, and dependency manifests before judging individual files.
   - Prefer `rg` and `rg --files` for discovery.

2. Load the checklist when needed:
   - Read `references/audit-checklist.md` before the detailed pass, or when the backend uses unfamiliar patterns.
   - Use it as coverage guidance, not as a substitute for code-specific reasoning.

3. Trace trust boundaries:
   - For each external input path, follow data from request, queue message, webhook, file upload, CLI job, or third-party callback into validation, authorization, persistence, side effects, and responses.
   - Pay special attention to paths that cross user, tenant, organization, admin, payment, or internal-service boundaries.

4. Verify findings against code:
   - Report a finding only when there is concrete evidence in the code or configuration.
   - Include file references and the relevant behavior. Avoid vague claims like "may be vulnerable" unless the uncertainty is explicitly explained.
   - Separate confirmed vulnerabilities from hardening recommendations.

5. Assess severity:
   - `Critical`: likely account takeover, remote code execution, credential exposure, broad data breach, auth bypass, or payment/security boundary compromise.
   - `High`: unauthorized access/modification of sensitive data, tenant isolation failure, privilege escalation, serious injection, exploitable SSRF, or dangerous file handling.
   - `Medium`: meaningful security weakness requiring specific conditions, missing defense-in-depth around sensitive paths, weak session/cookie/CORS/CSRF posture, dependency risk with reachable impact.
   - `Low`: limited-impact leak, minor misconfiguration, logging issue, weak validation with constrained impact, or maintainability issue that increases security risk.

6. Report before fixing:
   - Lead with findings ordered by severity.
   - For each finding include: severity, title, affected file(s), evidence, impact, likely exploit scenario in defensive terms, and recommended fix.
   - Include "No finding" notes only for important areas that were checked and looked safe.
   - End by asking whether the user wants fixes implemented.

## Review Priorities

Cover these areas during the audit:

- Authentication: login, registration, password reset, email verification, OAuth callbacks, MFA, session creation, session rotation, logout, cookies, JWTs, API keys.
- Authorization: object ownership, tenant/org membership, role checks, admin checks, horizontal/vertical privilege escalation, IDOR, route-level and service-level enforcement.
- Input handling: schema validation, type coercion, parser limits, unsafe deserialization, query parameters, JSON bodies, multipart uploads, path parameters.
- Injection: SQL/NoSQL, command, template, LDAP, ORM raw queries, unsafe dynamic code, shell-outs, path traversal.
- Data exposure: sensitive fields in API responses, logs, errors, caches, analytics, client bundles, OpenAPI specs, debug endpoints.
- Secrets: committed credentials, weak env handling, secret logging, token storage, overbroad service keys.
- Web security: CORS, CSRF, cookies, redirects, host header trust, rate limits, request size limits, security headers where backend-controlled.
- File and media handling: upload validation, MIME/content sniffing, storage permissions, filename/path use, malware scanning expectations, signed URL scope.
- SSRF and outbound requests: user-controlled URLs, metadata services, internal host access, redirect following, DNS/IP allowlists.
- Webhooks and integrations: signature verification, replay protection, idempotency, event trust, payment state transitions.
- Dependencies and supply chain: vulnerable packages, unsafe lifecycle scripts, lockfile drift, unmaintained auth/security libraries.
- Deployment: production debug flags, database/network exposure, TLS assumptions, container permissions, cloud IAM, public buckets.

## Output Format

Use this structure:

```markdown
**Findings**
1. [Severity] Title
   - Evidence: `path/to/file.ext:line` and concise code behavior.
   - Impact: What can go wrong.
   - Scenario: Defensive abuse case, without weaponized payloads.
   - Fix: Specific implementation direction.

**Checked**
- Important surfaces reviewed with no confirmed issue.

**Next**
Should I implement the fixes for these findings?
```

If no vulnerabilities are found, say that clearly, summarize the reviewed surfaces, note residual risk, and offer targeted hardening or tests.
