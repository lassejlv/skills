# Output Checklist

Run this self-check before finalizing `TERMS.md`, `PRIVACY.md`, app-store privacy text, cookie notices, or an audit.

## Evidence

- Existing policy/legal docs were read first.
- Product behavior was inspected from routes/pages/API/backend code.
- Data model/schema/env/deploy/provider evidence was inspected.
- Third-party providers affecting privacy or terms were verified against current official sources when possible.
- A working evidence matrix exists, even if summarized only in notes.

## Truthfulness

- No invented legal entity, owner, address, contact email, governing law, jurisdiction, or effective date.
- No unsupported claims about GDPR compliance, SOC 2, HIPAA, encryption, uptime, SLAs, refunds, deletion timelines, data residency, or AI training.
- Missing facts use `TODO(confirm):`.
- Existing policy text was preserved only where still accurate.

## Privacy Coverage

- Controller/operator and contact.
- Scope and covered surfaces.
- Data categories and sources.
- Purposes and legal bases where relevant.
- Cookies/local storage/tracking and consent controls.
- Processors/subprocessors and provider categories.
- International transfers and safeguards where known.
- Retention/deletion/export.
- User rights and choices.
- Security, children, AI processing, changes, and contact.

## Terms Coverage

- Service description and eligibility.
- Accounts and account responsibility.
- Acceptable use.
- User content ownership and operating license.
- Payments, subscriptions, trials, cancellation, taxes, invoices, and refunds if relevant.
- Third-party services.
- Availability/support without unsupported promises.
- IP, feedback, privacy cross-reference, termination, disclaimers, liability, governing law, changes, and contact.

## Final Response

- List created or updated files.
- Summarize key repo evidence and provider lookups.
- Call out all `TODO(confirm):` categories needing owner/legal review.
- Mention validation performed.
- Do not present the documents as guaranteed legal compliance.
