---
name: legal-policy-drafter
description: Draft, update, or audit legal-policy documents such as TERMS.md, PRIVACY.md, cookie notices, SaaS policies, app-store privacy text, and GDPR-friendly privacy disclosures from repository evidence. Use for legal policy work that requires inspecting product behavior, data flows, billing, auth, analytics, subprocessors, and missing business facts without inventing unsupported claims.
---

# Legal Policy Drafter

## Core Rule

Draft practical legal-policy documents from evidence, not guesses. Treat the output as a professional draft for owner/counsel review, not legal advice.

Before writing policy text, inspect the current repository and ask for missing blockers. Do not invent company identity, jurisdiction, contact details, retention periods, subprocessors, pricing terms, children policy, compliance claims, or security guarantees.

If the user wants speed, ask at most 5 blocker questions and mark unresolved facts with `TODO(confirm):`.

## Modes

Infer the mode from the request:

- `draft`: create fresh `TERMS.md` and `PRIVACY.md`.
- `update`: revise existing policy docs while preserving accurate useful text.
- `audit`: report gaps and contradictions without editing unless asked.
- `app-store`: produce concise mobile/app-store privacy wording in addition to or instead of full docs.
- `enterprise`: emphasize subprocessors, DPA/security posture, admin/workspace controls, SLAs, support, and organization authority.

## Intake

Ask only for facts that block a truthful draft and are not present in the repo or user prompt:

- Legal/service identity: company or owner name, product name, website URL, country/state of establishment, governing law preference.
- Contact: support/legal/privacy email, postal address if needed, DPO/EU representative if applicable.
- Effective date: confirm the current/effective date; use the runtime/system date as the proposed default when available.
- Audience and tone: plain, formal, friendly, developer-focused, consumer, enterprise, or app-store style.
- Commercial model: free, paid, subscriptions, trials, refunds, cancellation, taxes, invoicing.
- User data: account data, billing data, analytics, logs, uploaded content, AI prompts/files, cookies, location, device data, sensitive data, children/minors.
- Operations: hosting region, providers/subprocessors, retention/deletion/export process, security contact, data transfer mechanism.
- Output preferences: overwrite existing files, update existing docs, or create first drafts.

## Exploration Workflow

1. Read existing policy/legal files first: `TERMS.md`, `PRIVACY.md`, `LICENSE`, `README`, docs, marketing pages, app-store metadata, footer/contact copy.
2. Map product behavior from source: routes/pages, auth, onboarding, billing, uploads, messaging, admin areas, API endpoints, SDKs, telemetry, emails, background jobs, and data export/deletion paths.
3. Inspect data and infrastructure: schemas, migrations, ORM models, config files, env examples, Docker/worker/deploy files, analytics/error tracking, payment/email/storage/cloud providers.
4. Search or fetch current official documentation for detected third-party services that affect privacy or terms. Prefer official docs, subprocessor lists, DPA/privacy pages, SDK docs, and configuration docs. Use Context7 for library/framework/API/CLI docs when available; use web search for current provider privacy, cookie, subprocessor, and DPA facts. Record source names/URLs in working notes, not necessarily in the final policy unless useful.
5. Compare evidence against the GDPR checklist in `references/gdpr-policy-checklist.md`.
6. Build a working evidence matrix before drafting:

```md
| Finding | Evidence file/provider | Policy impact | Confidence |
```

7. Draft, update, or audit the requested output, defaulting to repo-root `TERMS.md` and `PRIVACY.md` for full policy work.

## References

Load these files only when needed:

- `references/gdpr-policy-checklist.md`: GDPR-friendly coverage checklist and repo search hints.
- `references/provider-research.md`: how to verify third-party provider privacy, DPA, cookie, and subprocessor facts.
- `references/privacy-template.md`: preferred `PRIVACY.md` structure and section-level prompts.
- `references/terms-template.md`: preferred `TERMS.md` structure and section-level prompts.
- `references/output-checklist.md`: final self-check before presenting the work.

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
- Never claim SOC 2, HIPAA, GDPR compliance, encryption details, uptime, support response times, refund rights, data residency, or deletion timelines unless the repo or user confirms them.

## Final Response

Summarize:

- Files created or updated.
- Key evidence used from the repo and provider lookups.
- Any `TODO(confirm)` items that need owner/legal review.
- Validation performed, such as markdown lint/checks if available.

Do not present the documents as guaranteed legal compliance.
