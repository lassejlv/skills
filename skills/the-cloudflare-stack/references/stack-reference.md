# Stack Reference

Use primary documentation and refresh the relevant pages before implementation. Package names, adapters, runtime flags, CLI syntax, and generated types can change.

## Application runtime and build

- [Bun package manager](https://bun.sh/docs/pm) — installs, lockfiles, scripts, workspaces, and package executable commands when Bun is available.
- [TanStack Start: Cloudflare Workers official partner hosting](https://tanstack.com/start/latest/docs/framework/react/guide/hosting#cloudflare-workers-official-partner) — required Vite plugin, SSR environment, Worker entrypoint, scripts, and deployment flow.
- [Cloudflare Vite plugin](https://developers.cloudflare.com/workers/vite-plugin/) — Worker runtime emulation, configuration, bindings, environments, and limitations.
- [Vite 8 migration guide](https://vite.dev/guide/migration) — Rolldown/Oxc changes and removed or deprecated configuration.
- [Cloudflare bindings](https://developers.cloudflare.com/workers/runtime-apis/bindings/) — binding configuration and runtime access.
- [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/) — current `wrangler.jsonc` schema and environment rules.

## Authentication and database

- [Better Auth Drizzle adapter](https://better-auth.com/docs/adapters/drizzle) — adapter package, provider values, schema generation, relations, and table mapping.
- [Better Auth database concepts](https://better-auth.com/docs/concepts/database) — auth schema, migration boundaries, joins, IDs, and hooks.
- [Drizzle with Cloudflare D1](https://orm.drizzle.team/docs/sqlite/connect-cloudflare-d1) — D1 driver and SQLite schema/query behavior.
- [Drizzle Kit with D1](https://orm.drizzle.team/docs/guides/d1-http-with-drizzle-kit) — remote migration tooling configuration.
- [Cloudflare D1 Worker API](https://developers.cloudflare.com/d1/worker-api/) — D1 binding behavior and platform types.
- [Cloudflare D1 migrations](https://developers.cloudflare.com/d1/reference/migrations/) — generating, applying, and inspecting D1 migrations.
- [Hyperdrive getting started](https://developers.cloudflare.com/hyperdrive/get-started/) — binding, connection string, local development, and driver setup.
- [Hyperdrive with Drizzle](https://developers.cloudflare.com/hyperdrive/examples/connect-to-postgres/postgres-drivers-and-libraries/drizzle-orm/) — current Worker-compatible PostgreSQL/Drizzle pattern.
- [Hyperdrive FAQ](https://developers.cloudflare.com/hyperdrive/reference/faq/) — D1 incompatibility, placement, caching, and read-after-write rules.
- [Hyperdrive supported databases](https://developers.cloudflare.com/hyperdrive/reference/supported-databases-and-features/) — supported PostgreSQL/MySQL engines and features.

### Database invariant

Cloudflare documents that Hyperdrive does not support D1. D1 is already designed for direct, low-latency Worker access. Hyperdrive pools and accelerates connections to separate PostgreSQL/MySQL-compatible databases.

## UI system

- [Tailwind CSS with Vite](https://tailwindcss.com/docs/installation/using-vite) — Tailwind v4 Vite plugin and CSS import.
- [Tailwind CSS v4 upgrade guide](https://tailwindcss.com/docs/upgrade-guide) — v3-to-v4 removals and configuration changes.
- [shadcn/ui for Vite](https://ui.shadcn.com/docs/installation/vite) — current CLI, aliases, Tailwind setup, and component installation.
- [shadcn/ui with Tailwind v4](https://ui.shadcn.com/docs/tailwind-v4) — v4 tokens, components, and migration notes.
- [coss ui LLM index](https://coss.com/ui/llms.txt) — current component and hook documentation map.
- [coss ui getting started](https://coss.com/ui/docs/get-started) — installation and project setup.
- [coss Radix/shadcn migration](https://coss.com/ui/docs/radix-migration) — migration guidance when replacing existing primitives.

Read the individual coss component page linked from `llms.txt` before copying that component. Do not assume its API matches shadcn or Radix.

## Object storage

- [Cloudflare R2 API](https://developers.cloudflare.com/r2/api/) — Workers binding, S3-compatible API, and REST API roles.
- [R2 Workers API](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/) — Worker-side bucket methods and object types.
- [R2 S3 compatibility](https://developers.cloudflare.com/r2/api/s3/api/) — S3 endpoint, supported operations, and differences from AWS S3.
- [R2 presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/) — direct client transfer design and restrictions.

Prefer the R2 Worker binding for application runtime traffic. Use S3 credentials only for callers outside the Worker binding boundary or when an S3-specific workflow is required.
