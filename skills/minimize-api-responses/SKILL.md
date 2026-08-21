---
name: minimize-api-responses
description: Minimize API response data while preserving required consumer contracts and enforcing field-level authorization. Use when Codex builds, changes, audits, or reviews REST, GraphQL, RPC, webhook, or server-action endpoints; maps database or domain objects into responses; reduces payloads; prevents excessive data exposure; designs DTOs, serializers, or response schemas; or verifies that each caller receives only the fields it needs and is allowed to access.
---

# Minimize API Responses

Make each endpoint return the smallest stable response that satisfies its declared consumers. Treat response shape as an authorization and privacy boundary, not merely a bandwidth optimization.

## Core rule

For every returned field, require answers to both questions:

1. Which current consumer behavior or public contract requires it?
2. Why may this requester receive it in this context?

Remove the field when either answer is missing. If compatibility or consumer evidence is uncertain, report it as unresolved instead of silently breaking the contract.

## Workflow

### 1. Establish the real contract

- Identify the endpoint, operation, caller types, authentication state, tenant or ownership boundary, and success and error variants.
- Trace actual consumers through UI code, mobile clients, SDKs, integrations, jobs, API documentation, schemas, and contract tests.
- Distinguish a field that is consumed from one that is merely present in a type, fixture, snapshot, or generic model.
- Determine whether the API is private, partner-facing, or public and versioned. Do not remove a documented public field without an explicit compatibility plan.
- Include list responses, nested objects, pagination metadata, headers, errors, and alternate role-specific representations in the review.

Do not assume that data hidden by a UI is safe. Anyone able to call the endpoint can inspect the raw response.

### 2. Inventory every exposed field

Create a compact field table when the response is non-trivial:

| Field path | Required by | Purpose | Allowed for | Sensitivity | Decision |
| --- | --- | --- | --- | --- | --- |
| `user.displayName` | Profile header | Identify account | Owner | Low | Keep |
| `user.passwordHash` | None | Internal authentication | Nobody | Secret | Remove |

Expand nested objects and array items. Review derived fields, identifiers, links, debug metadata, and error details instead of treating their parent object as one safe unit.

### 3. Apply a necessity test

Keep a field only when it is needed for at least one present-tense reason:

- Complete the endpoint's stated user or system operation.
- Preserve a supported public contract until it can be versioned or deprecated.
- Drive required client behavior such as pagination, concurrency control, retry timing, or state transitions.
- Provide information the requester is authorized to see for this resource and relationship.

Remove or redesign fields that exist only because they are easy to serialize, might be useful later, duplicate available data without justification, or expose an entire related object when a small summary or opaque reference is enough.

Treat these as high-risk until proven necessary and authorized:

- Password material, secrets, tokens, session data, reset or verification values, and private keys.
- Personal, financial, health, location, or contact data.
- Roles, permission internals, moderation flags, fraud or risk signals, and internal notes.
- Database keys, infrastructure details, audit provenance, stack traces, queries, configuration, and third-party payloads.
- Data belonging to another user, tenant, organization, or privilege level.

### 4. Enforce the response at the server boundary

- Map to a purpose-specific response DTO, serializer, or explicit allowlist for the endpoint and caller context.
- Prefer constructing allowed output over serializing a model and deleting forbidden fields. Blacklists fail when models gain new properties.
- Separate persistence models, input models, and output models. Never spread, dump, or automatically stringify raw database or domain objects into responses.
- Apply object- and field-level authorization before mapping the response. A requested field is not an authorization grant.
- Restrict database queries to required columns where practical, but keep the explicit response schema as the final security boundary.
- Validate runtime output against a closed response schema when the stack supports it. Reject or fail tests on undeclared properties.
- Give error responses their own minimal schema. Keep stack traces, internal paths, queries, and provider details in protected logs.
- Prefer separate representations for materially different audiences when one highly conditional response becomes difficult to reason about.

For client-controlled field selection, intersect requested fields with a server-owned allowlist and the requester's permissions. For GraphQL, remove fields that should never be public and authorize every sensitive field that remains queryable.

### 5. Prove both presence and absence

Add the narrowest meaningful tests that verify:

- Required fields and behavior remain intact.
- Forbidden and unnecessary fields are absent, including from nested objects and list items.
- Anonymous, owner, peer, cross-tenant, privileged, and downgraded callers receive the correct shapes.
- Detail, list, search, error, empty, and alternate response paths do not bypass filtering.
- Newly added persistence-model fields cannot appear automatically in existing API responses.
- Response schemas reject undeclared properties where closed-schema validation is available.

Prefer exact key-set assertions or closed schemas over broad snapshots that obscure why a field is allowed. Test the public response, not only the mapping helper.

### 6. Report the result honestly

For implementation work, summarize:

- Endpoints changed.
- Fields removed and the reason for each group.
- Fields retained because of a verified consumer or compatibility requirement.
- Authorization distinctions added or preserved.
- Contract tests run and any unresolved compatibility risk.

For audits, separate:

- **Security or privacy exposure:** unauthorized, secret, personal, financial, tenant, or operationally sensitive data.
- **Unnecessary contract surface:** fields without a demonstrated consumer that increase coupling or payload size but have no confirmed sensitive impact.
- **Unresolved:** fields whose consumers or compatibility obligations cannot be established from available evidence.

Do not label every redundant field a vulnerability. State the concrete impact and confidence.

## Guardrails

- Do not rely on client-side filtering.
- Do not treat authentication as permission to every property on an object.
- Do not solve response minimization with a denylist alone.
- Do not remove public fields solely because the current first-party UI does not use them.
- Do not broaden the task into unrelated request validation or general security cleanup unless the user asks.
- Preserve unrelated working-tree changes and validate only the affected contract surface plus proportionate broader checks.

## Research grounding

Read [references/research.md](references/research.md) when explaining the security or privacy rationale, updating this skill's controls, or handling a disputed finding.
