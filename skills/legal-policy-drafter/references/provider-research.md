# Provider Research

Use this reference when the repository reveals third-party services that affect `TERMS.md`, `PRIVACY.md`, cookies, subprocessors, international transfers, or payment/refund wording.

## Rule

Verify current official provider pages before naming a provider as a processor/subprocessor or making claims about privacy, DPAs, subprocessors, data location, retention, cookies, or AI training. Prefer official privacy pages, DPA pages, subprocessor pages, product docs, and security pages. Do not rely on package names alone.

Use Context7 for library/framework/API/CLI docs. Use web search for current provider legal/privacy/subprocessor/DPA pages.

## Research Notes Format

Keep working notes like this before drafting:

```md
| Provider | Evidence | Role | Data likely involved | Policy impact | Confidence |
| --- | --- | --- | --- | --- | --- |
| Stripe | package.json + official privacy/DPA URL | payment processor | billing/contact/payment metadata | Payments, retention, subprocessors, transfers | High |
```

## Common Provider Categories

- Payments: Stripe, Paddle, Lemon Squeezy, Chargebee, PayPal. Check checkout, invoices, tax records, subscription renewal, refund/cancellation flow, and payment processor wording.
- Email: Resend, SendGrid, Mailgun, Postmark, AWS SES, SMTP. Check transactional email, marketing email, unsubscribe, message metadata, and provider role.
- Authentication: Clerk, Auth0, Supabase Auth, Firebase Auth, Better Auth, OAuth providers. Check account identifiers, sessions, OAuth profile data, cookies, and security logs.
- Analytics: PostHog, Plausible, Google Analytics, Vercel Analytics, Segment, Amplitude, Mixpanel. Check cookies/local storage, event data, consent, IP handling, and opt-out controls.
- Error tracking/monitoring: Sentry, Bugsnag, Datadog, Logtail/Better Stack, Axiom. Check logs, stack traces, IP/device data, user IDs, retention, and masking.
- Hosting/storage/database: Vercel, Cloudflare, AWS, GCP, Azure, Railway, Fly.io, Supabase, Neon, PlanetScale, R2, S3. Check hosting region, backups, logs, storage, transfers, and subprocessors.
- AI providers: OpenAI, Anthropic, Google AI, Mistral, Groq, Replicate. Check prompts/files/outputs, model training settings, retention, abuse monitoring, and user-facing AI disclosures.
- Support/customer messaging: Intercom, Crisp, Zendesk, Help Scout, Linear, GitHub Issues. Check support messages, contact details, attachments, and retention.
- CDN/media: Cloudflare, Imgix, UploadThing, Cloudinary. Check IP logs, uploaded media, transformations, and retention.

## Claims To Avoid Without Evidence

- "We never share data."
- "We are GDPR compliant."
- "Data is encrypted at rest and in transit."
- "We delete all data within X days."
- "We host exclusively in the EU/US."
- "We do not use cookies."
- "AI providers never train on your data."
- "We offer refunds" or "all sales are final."

Use `TODO(confirm):` instead.
