# GDPR-Friendly Policy Checklist

Use this checklist while drafting `PRIVACY.md` and cross-checking `TERMS.md`. Keep unresolved items explicit with `TODO(confirm):`.

## Privacy Policy

- Controller: legal entity or owner, website/product name, contact email, postal address when available.
- Scope: website, app, API, CLI, mobile app, SaaS workspace, browser extension, or other surface.
- Data categories: account profile, contact details, billing, authentication, uploaded/user content, support messages, logs, device/browser data, cookies/local storage, analytics events, AI prompts/outputs, location, sensitive data if any.
- Sources: user-provided, automatically collected, third-party login/payment/provider data, imported workspace data.
- Purposes and legal bases: contract, consent, legitimate interests, legal obligation, vital interests, public task when applicable.
- Processing details: account creation, authentication, payments, service delivery, security/fraud prevention, analytics, support, marketing, legal compliance.
- Processors/subprocessors: hosting, database/storage, payment provider, email provider, analytics, crash/error tracking, auth provider, AI provider, customer support, CDN, monitoring.
- International transfers: EEA/non-EEA processing, SCCs, adequacy decisions, provider safeguards when known.
- Retention: account data, billing/tax records, logs, backups, support messages, analytics, deleted accounts.
- Rights: access, rectification, deletion, restriction, portability, objection, withdraw consent, complain to supervisory authority.
- Cookies/tracking: essential cookies, analytics cookies, marketing cookies, local storage, consent controls, browser controls.
- Security: reasonable technical and organizational measures; avoid overpromising certifications unless verified.
- Children: minimum age and whether knowingly collecting children's data.
- Automated decisions/AI: profiling, automated decision-making, AI feature data handling when applicable.
- Changes: policy updates and notice method.
- Contact: support/privacy/legal email and DPO/EU representative if applicable.

## Terms Of Service

- Service identity: product name, owner/company, website URL, short service description.
- Eligibility: minimum age, authority for organizations/workspaces, account responsibility.
- Accounts: registration, credential security, truthful information, suspension/termination rights.
- Acceptable use: illegal activity, abuse, scraping, spam, reverse engineering where appropriate, service disruption, rights infringement.
- User content: ownership retained by user, license needed to operate the service, responsibility for content, removal rights.
- Plans/payment: pricing, subscription renewal, trials, cancellation, refunds, taxes, failed payments, changes to fees.
- Third-party services: integrations, external providers, separate terms, no control over third parties.
- Availability/support: uptime/support promises only if verified; otherwise use reasonable-efforts language.
- Intellectual property: service ownership, trademarks, feedback license if desired.
- Privacy cross-reference: link to `PRIVACY.md`.
- Disclaimers: service provided as-is/as-available where enforceable.
- Liability limits: jurisdiction-sensitive; keep balanced and mark for legal review.
- Indemnity: include only when suitable for the product audience.
- Termination: user cancellation, service suspension, post-termination data handling.
- Changes: updates to terms and continued use.
- Governing law/disputes: ask user; mark `TODO(confirm)` if unknown.
- Contact: support/legal email.

## Evidence Hints

Search the repository for:

- `stripe`, `paddle`, `lemonsqueezy`, `billing`, `checkout`, `subscription`
- `auth`, `oauth`, `session`, `better-auth`, `clerk`, `supabase`, `firebase`
- `posthog`, `plausible`, `analytics`, `gtag`, `sentry`, `bugsnag`
- `openai`, `anthropic`, `ai`, `llm`, `prompt`, `upload`, `storage`, `s3`, `r2`
- `email`, `resend`, `sendgrid`, `mailgun`, `smtp`, `support`
- `cookie`, `localStorage`, `sessionStorage`, `consent`
- `delete`, `export`, `retention`, `backup`, `log`
