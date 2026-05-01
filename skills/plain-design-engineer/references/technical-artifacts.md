# Technical Artifacts

Use this reference when a page needs to feel real. Replace generic decoration with product evidence.

## Artifact Rules

- Artifacts must be plausible for the product domain.
- Prefer real code, real command names, real data shapes, or accurate abstractions from the repo.
- Do not invent fake impressive metrics. If numbers are illustrative, make that clear or avoid them.
- Keep artifacts readable on mobile with wrapping, horizontal scroll, or simplified stacked forms.
- Dark code panels need readable contrast and should not dominate the palette.

## Recipes

### CLI Output

Use for developer tools, databases, deploy products, and infrastructure.

Content:

- One command.
- 4-8 lines of meaningful output.
- Status, latency, region, version, or resource IDs if supported by product evidence.

### API Request/Response

Use for API products, SDKs, auth, billing, AI, and workflow tools.

Content:

- Endpoint or method name.
- Minimal request body.
- Response with concrete fields.
- Error or rate-limit example if relevant.

### Schema Or Data Model

Use for databases, backends, CRMs, analytics, and devtools.

Content:

- Table/model names.
- 4-8 fields.
- Relationship hints.
- Migration or version note when useful.

### Architecture Diagram

Use for infrastructure products and platform tools.

Format:

- Mono boxes, thin connector lines, small labels.
- 3-6 nodes maximum in hero surfaces.
- Show data flow, deployment path, request path, or failover path.

### Benchmark Table

Use only when the repo/user provides real data or the table is clearly framed as an example.

Columns:

- Workload or scenario.
- Baseline.
- Product/result.
- Notes or constraints.

### Query Trace Or Event Timeline

Use for observability, database, queue, AI agent, or build systems.

Rows:

- Timestamp or step.
- Operation.
- Duration/status.
- Resource or detail.

### Dashboard Strip

Use when the product is operational and repeated-use.

Rows over cards:

- Service/resource name.
- Status.
- Version/region.
- Usage or latency.
- Last event.

### Diff, Changelog, Or Release Feed

Use for developer workflows, docs, CI/CD, and product update pages.

Content:

- Version/tag.
- Files or APIs changed.
- Status.
- Short technical note.
