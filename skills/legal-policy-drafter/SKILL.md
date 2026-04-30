---
name: legal-policy-drafter
description: Draft professional Terms of Service and Privacy Policy markdown files from a real codebase. Use when Codex is asked to create, update, or audit TERMS.md, PRIVACY.md, Terms, Privacy Policy, cookie/privacy notices, GDPR-friendly legal docs, SaaS policy docs, or app-store/legal website policy pages. The skill guides repo exploration, 4-5 subagent research passes when delegation is explicitly allowed, targeted lookup of detected libraries/services/providers, user intake questions for business/legal details, and writing TERMS.md plus PRIVACY.md without inventing unknown facts.
---

# Legal Policy Drafter

## Core Rule

Draft practical legal-policy documents from evidence, not guesses. Treat the output as a professional draft for review, not legal advice.

Before writing `TERMS.md` or `PRIVACY.md`, inspect the current repository and ask for missing business facts. Do not invent company identity, jurisdiction, support email, retention periods, subprocessors, pricing terms, children policy, or contact details.

## Intake

Ask concise questions before drafting unless the answers are already present in the repo or user prompt:

- Legal/service identity: company or owner name, product name, website URL, country/state of establishment, governing law preference.
- Contact: support/legal/privacy email, postal address if needed, DPO/EU representative if applicable.
- Effective date: confirm the current/effective date; use the runtime/system date as the proposed default when available.
- Audience and tone: plain, formal, friendly, developer-focused, consumer, enterprise, or app-store style.
- Commercial model: free, paid, subscriptions, trials, refunds, cancellation, taxes, invoicing.
- User data: account data, billing data, analytics, logs, uploaded content, AI prompts/files, cookies, location, device data, sensitive data, children/minors.
- Operations: hosting region, providers/subprocessors, retention/deletion/export process, security contact, data transfer mechanism.
- Output preferences: overwrite existing files, update existing docs, or create first drafts.

If the user wants speed, ask only for blockers and mark unresolved items with `TODO(confirm):`.

## Exploration Workflow

1. Read existing policy/legal files first: `TERMS.md`, `PRIVACY.md`, `LICENSE`, `README`, docs, marketing pages, app-store metadata, footer/contact copy.
2. Map product behavior from source: routes/pages, auth, onboarding, billing, uploads, messaging, admin areas, API endpoints, SDKs, telemetry, emails, background jobs, and data export/deletion paths.
3. Inspect data and infrastructure: schemas, migrations, ORM models, config files, env examples, Docker/worker/deploy files, analytics/error tracking, payment/email/storage/cloud providers.
4. Search or fetch current official documentation for detected third-party services that affect privacy or terms. Prefer official docs, subprocessor lists, DPA/privacy pages, SDK docs, and configuration docs. Use Context7 for library/framework/API/CLI docs when available; use web search for current provider privacy, cookie, subprocessor, and DPA facts. Record source names/URLs in working notes, not necessarily in the final policy unless useful.
5. Compare evidence against the GDPR checklist in `references/gdpr-policy-checklist.md`.
6. Draft or update both files at the requested location, defaulting to the repo root.

## Subagent Plan

When the user explicitly authorizes subagents, spawn 4-5 independent agents with read-only exploration tasks. If authorization is unclear and the active environment requires explicit delegation permission, ask once before spawning. Keep write ownership in the main agent; subagents should return notes, not edit files.

Use these passes:

- Product and user flows: app purpose, target users, account model, user-generated content, public/private surfaces, risky terms clauses.
- Data model and backend: personal data categories, API endpoints, database fields, retention/deletion/export evidence, logs, admin access.
- Infrastructure and subprocessors: hosting, storage, payment, email, auth, analytics, error tracking, AI providers, CDNs, package/service integrations.
- Frontend and tracking: cookies/local storage, analytics scripts, consent UX, forms, marketing pages, privacy-facing copy.
- Existing docs and legal consistency: current policies, README claims, pricing/refund wording, license, jurisdiction hints, support/contact details.

Merge the notes into a single evidence table before drafting. Resolve conflicts by checking the source files yourself.

## Drafting Standards

- Write clear markdown with an effective date near the top.
- Generate exactly `TERMS.md` and `PRIVACY.md` unless the user requested different filenames.
- Keep language professional and specific to the product. Avoid fake legal certainty, boilerplate-only policies, and broad claims not supported by the codebase.
- Use `TODO(confirm): ...` for missing facts instead of fabricating them.
- Include a short "not legal advice / review with counsel" note only if appropriate for the project style; do not make it the main content.
- Keep GDPR friendliness concrete: legal bases, data categories, purposes, processors, transfers, retention, rights, deletion/export/contact, security, cookies/tracking, and children.
- For Terms, cover service description, accounts, acceptable use, user content, payments/refunds if relevant, third-party services, availability, termination, disclaimers, liability, governing law, changes, and contact.
- Preserve useful existing policy text when updating files, but remove contradictions and stale claims after confirming with evidence.

## Final Response

Summarize:

- Files created or updated.
- Key evidence used from the repo and provider lookups.
- Any `TODO(confirm)` items that need owner/legal review.
- Validation performed, such as markdown lint/checks if available.

Do not present the documents as guaranteed legal compliance.
