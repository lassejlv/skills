# Research grounding

These primary sources support the skill's controls. They were checked on 2026-08-16.

## OWASP API Security Top 10: API3:2023

[Broken Object Property Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/) treats excessive data exposure as a property-level authorization failure. Its prevention guidance says to verify access to every exposed property, select specific properties instead of using generic object serialization, validate responses against schemas, and keep returned structures to the functional minimum.

Applied controls:

- Require both necessity and authorization for each field.
- Prefer endpoint-specific allowlists and output schemas.
- Avoid direct model serialization and denylist-only filtering.
- Keep field selection server-owned even when clients request particular fields.

## OWASP Web Security Testing Guide

[Testing for Excessive Data Exposure](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure) defines the issue as returning more information than the client needs. It recommends comparing raw responses with actual client needs and checking multiple endpoints, privilege levels, nested objects, GraphQL fields, and error output. Its remediation guidance calls for server-side filtering, purpose-specific DTOs or serializer allowlists, field-level access control, restricted schemas, and sanitized errors.

Applied controls:

- Trace real consumers before deciding that a field is required.
- Review list, detail, nested, role-specific, and error paths.
- Test raw response shapes and negative field assertions.
- Treat UI hiding as presentation only, never as access control.

## EU General Data Protection Regulation

[GDPR Article 5(1)(c)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) defines data minimisation for personal data as limiting processing to what is necessary for its purpose. Article 25 requires data protection by design and, by default, processing only the personal data necessary for each specific purpose.

Applied controls when personal data is in scope:

- Tie each personal-data field to a specific endpoint purpose.
- Default to omission when that purpose does not require the field.
- Treat this as engineering guidance, not a substitute for project-specific legal advice.
