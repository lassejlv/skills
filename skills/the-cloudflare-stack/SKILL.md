---
name: the-cloudflare-stack
description: Build, migrate, review, and deploy full-stack React applications on Cloudflare Workers with TanStack Start, the official Cloudflare Vite adapter, Vite 8, Better Auth, Drizzle ORM, D1 or Hyperdrive-backed SQL, R2 object storage, Tailwind CSS v4, shadcn/ui, and coss ui. Use when creating or changing an app on this stack, wiring Cloudflare bindings, authentication, database migrations, storage, components, local development, or production validation.
---

# The Cloudflare Stack

Build one coherent Cloudflare-native application. Keep server-only code inside the Worker runtime, access Cloudflare resources through typed bindings, and prove the real authentication, database, and storage flows before calling the work complete.

## Stack contract

- **Application:** TanStack Start with React, deployed to Cloudflare Workers through the official `@cloudflare/vite-plugin` integration.
- **Build:** Vite 8. Check plugin compatibility with Vite 8's Rolldown/Oxc toolchain; do not silently downgrade to Vite 7.
- **Authentication:** Better Auth using its official Drizzle adapter.
- **Database:** Drizzle ORM with either Cloudflare D1 or an external PostgreSQL/MySQL database reached through Hyperdrive.
- **UI:** Tailwind CSS v4, shadcn/ui, and coss ui.
- **Object storage:** Cloudflare R2. R2 is the Cloudflare product; “Cloudflare S3” means its S3-compatible API, not AWS S3.
- **Language:** TypeScript with generated Cloudflare binding types.

Preserve the package manager, lockfile, and repository structure in an existing project. For a new project, check whether Bun is available with `bun --version`. If it succeeds, use Bun consistently for package installation, scripts, tests, and one-off package executables. Otherwise use `pnpm` unless the user requests another package manager.

## Package manager policy

When Bun is selected:

```text
bun install                    install dependencies
bun install --frozen-lockfile  reproduce an existing lockfile
bun add <package>              add a dependency
bun add -d <package>           add a development dependency
bun run <script>               run a package.json script
bunx <package>                 execute a package CLI
```

- Prefer the Bun equivalent for every package-manager command in upstream documentation.
- Keep `bun.lock` as the only package-manager lockfile in a new Bun project.
- Do not mix Bun, pnpm, npm, or Yarn commands in one workflow unless an upstream tool genuinely requires it; document that exception.
- Do not replace an existing project's package manager merely because Bun is installed unless the user asks for that migration.

## Critical database boundary

Hyperdrive cannot connect to D1. Select a database lane before writing auth or schema code:

| Lane | Runtime client | Drizzle dialect | Better Auth provider | Migration path |
| --- | --- | --- | --- | --- |
| D1, the default | D1 Worker binding via `drizzle-orm/d1` | SQLite | `sqlite` | Drizzle-generated SQL applied with Wrangler D1 migrations |
| Hyperdrive | Hyperdrive connection string plus a Worker-compatible PostgreSQL or MySQL driver | PostgreSQL or MySQL | `pg` or `mysql` | Drizzle migrations applied to the external database |

Use D1 unless the existing system or user explicitly requires an external PostgreSQL/MySQL database. If both D1 and Hyperdrive are present, assign them distinct responsibilities and document which one owns each table. Never place Hyperdrive in front of D1 or mirror auth records across both without a designed synchronization boundary.

For auth, sessions, authorization, or other consistency-sensitive Hyperdrive reads, use a cache-disabled Hyperdrive configuration. Hyperdrive does not invalidate cached query results after writes.

## Workflow

### 1. Inspect and refresh documentation

1. Read repository instructions, `package.json`, lockfiles, `vite.config.*`, `wrangler.*`, Drizzle config, schemas, auth code, routes, and global CSS.
2. Inspect `git status --short --branch` and preserve unrelated changes.
3. Confirm the chosen database lane, existing Cloudflare resources, binding names, environments, and deployment target.
4. Read the current primary documentation before installing or configuring packages. Use [references/stack-reference.md](references/stack-reference.md) to route the research.
5. Treat current official documentation and installed package types as authoritative when examples in this skill drift.

Do not provision Cloudflare resources, apply remote migrations, rotate secrets, or deploy unless the user requested that external change.

### 2. Establish the Worker application

- Use TanStack Start's official Cloudflare Workers setup, not a generic Node server, Pages adapter, or a Nitro preset.
- Install the current compatible releases of `@cloudflare/vite-plugin`, `wrangler`, TanStack Start, React, and the React Vite plugin while keeping `vite` on major version 8.
- Preserve the official Vite plugin ordering. The current TanStack pattern places the Cloudflare plugin configured for the `ssr` Vite environment before `tanstackStart()` and the React plugin.
- Add the Tailwind Vite plugin without removing or replacing the Cloudflare/TanStack plugins.
- Point Wrangler at TanStack Start's Worker server entry exactly as the current hosting guide specifies.
- Use a current `compatibility_date`. Add `nodejs_compat` only when required by TanStack Start, Better Auth, the selected database driver, or another verified dependency.
- Keep `dev`, `build`, `preview`, `deploy`, and Cloudflare type-generation scripts explicit in `package.json`.

After changing Wrangler bindings, regenerate types and use those types in application code. Do not maintain a handwritten binding interface that can drift from `wrangler.jsonc`.

### 3. Model bindings and server boundaries

Use clear binding names unless the project already has established names:

```text
DB          D1Database
HYPERDRIVE  Hyperdrive              # only for the external SQL lane
STORAGE     R2Bucket
```

- Build request-aware factories such as `createDb(env)`, `createAuth(env)`, and `createStorage(env)` instead of hiding bindings in client-importable globals.
- Keep bindings, database clients, auth secrets, and R2 operations in server-only modules.
- Use Worker bindings inside the Worker. Do not replace them with account API tokens or public REST calls.
- Use Wrangler secrets or the deployment platform's secret store for `BETTER_AUTH_SECRET`, OAuth credentials, and R2 S3 credentials used for presigning or by callers outside Workers.
- Never expose a secret through a `VITE_` variable, serialized loader data, server-function return value, or client bundle.

### 4. Configure Drizzle and migrations

For D1:

- Create the Drizzle client from the request's D1 binding with the D1 driver.
- Use SQLite schema types and the D1-compatible query surface.
- Keep generated migrations in version control and declare the migration directory in Wrangler/Drizzle configuration where supported.
- Apply migrations locally first. Apply remote migrations only after reviewing the generated SQL and confirming the target database.
- Do not assume interactive transactions. Design atomic multi-statement work around D1-supported batching and current platform guarantees.

For Hyperdrive:

- Create the selected PostgreSQL/MySQL driver from `env.HYPERDRIVE.connectionString` using Cloudflare's current driver guidance.
- Initialize Drizzle with the matching dialect and Better Auth provider.
- Decide deliberately whether query caching is safe. Authentication and read-after-write paths require fresh reads.
- Close or release clients according to the selected Workerd-compatible driver's lifecycle rules.

For both lanes:

- Keep one canonical schema for application and Better Auth tables.
- Generate Better Auth's Drizzle schema with the current Better Auth CLI, review it, then generate migrations through Drizzle Kit.
- Pass the schema and required relations to the Better Auth adapter. Keep custom table/model names mapped explicitly.
- Never run schema migrations during an application request or Worker startup.

### 5. Configure Better Auth

- Use Better Auth's official Drizzle adapter package and its current documented import path. Prefer the minimal server build when the installed Better Auth version supports the chosen adapter and features.
- Construct Better Auth with the same Drizzle database and schema used by the application.
- Use provider `sqlite` for D1, `pg` for PostgreSQL through Hyperdrive, or `mysql` for MySQL through Hyperdrive.
- Mount `auth.handler` at the TanStack Start auth API route using the framework's current server-route conventions.
- Keep the canonical application URL and trusted origins environment-specific. Configure secure cookies, proxy headers, and OAuth callback URLs for the real deployment origin.
- Read sessions on the server from request headers/cookies. Return only the minimal user/session fields needed by client components.
- Add schema and migrations for every enabled Better Auth plugin before exercising its endpoints.

At minimum, verify sign-up or the configured sign-in method, sign-in, session retrieval, a protected server action/route, sign-out, invalid credentials, and an unauthenticated request.

### 6. Build the component system

- Install Tailwind CSS v4 through `@tailwindcss/vite` and import it with `@import "tailwindcss";` in the global stylesheet.
- Initialize shadcn/ui against the project's real source alias and global CSS. Use the current CLI rather than copying an old v3 Tailwind setup.
- For a new coss-based component system, use the current coss style initializer. With Bun, run `bunx --bun shadcn@latest init @coss/style`; otherwise use the selected package manager's equivalent. Add components through the coss registry with `bunx --bun shadcn@latest add @coss/<component>` or the matching non-Bun command, then review the generated source.
- Read `https://coss.com/ui/llms.txt`, then open the component-specific coss page before adding a coss component.
- Treat shadcn and coss components as owned source code: adapt tokens and behavior locally, preserve accessibility, and review generated changes.
- Use one implementation source per component family. Prefer coss when it provides the exact component and use shadcn for gaps or project-established primitives. Do not keep competing dialog, form, menu, or toast foundations without a documented reason.
- When replacing existing Radix/shadcn primitives with coss, follow coss's migration guide and test keyboard, focus, layering, form, and mobile behavior.
- Keep server-only imports out of components that can enter the browser bundle.

### 7. Use R2 for object storage

- Inside Workers, prefer the `R2Bucket` binding for reads, writes, listing, multipart operations, and deletes.
- Use R2's S3-compatible API for presigning, external tools, migrations, or SDK workflows that cannot use a Worker binding.
- Keep buckets private by default. Serve objects through authorized Worker routes or narrowly scoped, short-lived presigned URLs when direct upload/download is justified.
- Validate object keys, ownership, content type, and size on the server. Use unguessable keys and never trust a client-supplied key as authorization.
- Store object bytes in R2; store ownership, logical metadata, status, and the R2 object key in the database.
- Define failure handling for database/R2 partial success. Make upload finalization and deletion retryable and idempotent.
- Test unauthorized access as well as upload, download, overwrite policy, and deletion.

## Suggested project boundaries

Adapt these names to the existing repository instead of forcing a rewrite:

```text
src/
  db/
    client.server.ts
    schema.ts
  lib/
    auth.server.ts
    storage.server.ts
  routes/
    api/auth/...
  styles.css
drizzle/
vite.config.ts
drizzle.config.ts
wrangler.jsonc
```

Files containing `.server` are a convention, not a security boundary by themselves. Confirm they cannot be reached from the client dependency graph.

## Validation gates

Run the narrowest available project commands plus these stack-specific checks:

1. Install dependencies from the lockfile with the selected package manager and confirm the resolved Vite major is 8. In a Bun project, use `bun install --frozen-lockfile` for reproducible validation.
2. Generate Cloudflare types and run TypeScript checking.
3. Generate/review migrations, apply them to the local database, and verify a representative Drizzle query.
4. Run the app through the Cloudflare Vite development runtime; do not validate only in a generic Node runtime.
5. Exercise the complete Better Auth flow and a protected mutation in the browser or with an equivalent cookie-preserving client.
6. Exercise an R2 upload/read/delete round trip and one rejected unauthorized attempt.
7. If using Hyperdrive, execute a real query through the Hyperdrive binding and verify consistency-sensitive reads do not use stale cache results.
8. Run unit/integration tests, production build, SSR/hydration checks, and `wrangler deploy --dry-run` when supported.
9. Test the production URL after deployment only when deployment is in scope. Check bounded Worker logs for runtime, binding, auth callback, and migration errors.

Report exactly which local, preview, and production checks ran. A successful build alone does not prove auth, D1/Hyperdrive, or R2 behavior.

## Guardrails

- Do not connect Hyperdrive to D1.
- Do not use both D1 and Hyperdrive for the same data without an explicit ownership and synchronization design.
- Do not use Hyperdrive query caching for auth/session/permission reads that require freshness.
- Do not deploy TanStack Start with an unrelated adapter when the Cloudflare Workers adapter is required.
- Do not downgrade Vite to work around an incompatible plugin without user approval; find a Vite 8-compatible version or report the blocker.
- Do not carry Tailwind v3 directives, obsolete PostCSS setup, or stale shadcn component assumptions into a Tailwind v4 project.
- Do not expose R2 S3 credentials to browser code or use them for ordinary Worker object operations when a binding is available. Server-side presigning is the intentional exception.
- Do not apply production migrations or create/replace remote resources implicitly.
- Do not claim completion until the user-visible path has been exercised in the Cloudflare runtime.

## Reference routing

Read [references/stack-reference.md](references/stack-reference.md) for the official documentation map, the D1/Hyperdrive distinction, and the minimum pages to refresh for each subsystem.
