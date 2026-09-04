# Skills

Personal agent skills packaged as a multi-skill repository.

Repository: https://github.com/lassejlv/skills

## Install

List available skills:

```sh
npx skills add lassejlv/skills --list
```

Install every skill:

```sh
npx skills add lassejlv/skills --skill '*'
```

Install one skill:

```sh
npx skills add lassejlv/skills --skill aws-account-cleanup
npx skills add lassejlv/skills --skill legal-policy-drafter
npx skills add lassejlv/skills --skill plain-design-engineer
npx skills add lassejlv/skills --skill backend-security-audit
npx skills add lassejlv/skills --skill libtermy-implementation
npx skills add lassejlv/skills --skill use-aws
npx skills add lassejlv/skills --skill no-vibe-code
npx skills add lassejlv/skills --skill no-yak-shaving
npx skills add lassejlv/skills --skill project-orientation-sweep
npx skills add lassejlv/skills --skill project-roadmap
npx skills add lassejlv/skills --skill gitty
npx skills add lassejlv/skills --skill paper-to-gpui
npx skills add lassejlv/skills --skill clean-codebase
npx skills add lassejlv/skills --skill build-planetscale-landing-pages
npx skills add lassejlv/skills --skill build-gpui-apps
npx skills add lassejlv/skills --skill minimize-api-responses
npx skills add lassejlv/skills --skill tcut-terminal-video
npx skills add lassejlv/skills --skill use-goal
npx skills add lassejlv/skills --skill codex-image-generation
npx skills add lassejlv/skills --skill the-cloudflare-stack
```

You can also install from the full GitHub URL:

```sh
npx skills add https://github.com/lassejlv/skills --skill aws-account-cleanup
npx skills add https://github.com/lassejlv/skills --skill legal-policy-drafter
npx skills add https://github.com/lassejlv/skills --skill plain-design-engineer
npx skills add https://github.com/lassejlv/skills --skill backend-security-audit
npx skills add https://github.com/lassejlv/skills --skill libtermy-implementation
npx skills add https://github.com/lassejlv/skills --skill use-aws
npx skills add https://github.com/lassejlv/skills --skill no-vibe-code
npx skills add https://github.com/lassejlv/skills --skill no-yak-shaving
npx skills add https://github.com/lassejlv/skills --skill project-orientation-sweep
npx skills add https://github.com/lassejlv/skills --skill project-roadmap
npx skills add https://github.com/lassejlv/skills --skill gitty
npx skills add https://github.com/lassejlv/skills --skill paper-to-gpui
npx skills add https://github.com/lassejlv/skills --skill clean-codebase
npx skills add https://github.com/lassejlv/skills --skill build-planetscale-landing-pages
npx skills add https://github.com/lassejlv/skills --skill build-gpui-apps
npx skills add https://github.com/lassejlv/skills --skill minimize-api-responses
npx skills add https://github.com/lassejlv/skills --skill tcut-terminal-video
npx skills add https://github.com/lassejlv/skills --skill use-goal
npx skills add https://github.com/lassejlv/skills --skill codex-image-generation
npx skills add https://github.com/lassejlv/skills --skill the-cloudflare-stack
```

For local development from this checkout:

```sh
npx skills add . --list
npx skills add . --skill aws-account-cleanup
npx skills add . --skill legal-policy-drafter
npx skills add . --skill plain-design-engineer
npx skills add . --skill backend-security-audit
npx skills add . --skill libtermy-implementation
npx skills add . --skill use-aws
npx skills add . --skill no-vibe-code
npx skills add . --skill no-yak-shaving
npx skills add . --skill project-orientation-sweep
npx skills add . --skill project-roadmap
npx skills add . --skill gitty
npx skills add . --skill paper-to-gpui
npx skills add . --skill clean-codebase
npx skills add . --skill build-planetscale-landing-pages
npx skills add . --skill build-gpui-apps
npx skills add . --skill minimize-api-responses
npx skills add . --skill tcut-terminal-video
npx skills add . --skill use-goal
npx skills add . --skill codex-image-generation
npx skills add . --skill the-cloudflare-stack
```

## Layout

Each skill lives in its own directory under `skills/` and must include a
`SKILL.md` file with YAML frontmatter plus `agents/openai.yaml` interface
metadata:

```text
skills/
  aws-account-cleanup/
    SKILL.md
    references/
    agents/
  backend-security-audit/
    SKILL.md
    references/
    agents/
  legal-policy-drafter/
    SKILL.md
    references/
    agents/
  libtermy-implementation/
    SKILL.md
    scripts/
    references/
    agents/
  plain-design-engineer/
    SKILL.md
    references/
    agents/
  use-aws/
    SKILL.md
    scripts/
    references/
    agents/
  no-vibe-code/
    SKILL.md
    slop-check.mjs
    samples/
    agents/
  no-yak-shaving/
    SKILL.md
    agents/
  project-orientation-sweep/
    SKILL.md
    scripts/
    references/
    agents/
  project-roadmap/
    SKILL.md
    agents/
  gitty/
    SKILL.md
    references/
    agents/
  paper-to-gpui/
    SKILL.md
    scripts/
    references/
    agents/
  clean-codebase/
    SKILL.md
    references/
    agents/
  build-planetscale-landing-pages/
    SKILL.md
    references/
    assets/
    agents/
  build-gpui-apps/
    SKILL.md
    scripts/
    references/
    assets/
      reference-app/       # exact-revision compile/test fixture
    tests/                 # realistic forward-test scenarios
    agents/
  minimize-api-responses/
    SKILL.md
    references/
    agents/
  tcut-terminal-video/
    SKILL.md
    references/
    agents/
  use-goal/
    SKILL.md
    examples.md
    agents/
  codex-image-generation/
    SKILL.md
    references/
    agents/
  the-cloudflare-stack/
    SKILL.md
    references/
    agents/
```

## Validate

Validate every skill package, metadata file, Markdown fence, and local link:

```sh
python -m pip install pyyaml==6.0.3
python scripts/validate_skills.py
```

Exercise the deterministic inventory, GPUI inspection, frontend lint, and
spring fixtures:

```sh
scripts/test_skill_tools.sh
```

The GPUI suite also has an exact-revision compile/test fixture:

```sh
skills/build-gpui-apps/scripts/validate_reference_app.sh
```

The same checks run in GitHub Actions on pull requests and pushes to `main`.

## Skills

- `aws-account-cleanup`: Dry-run AWS account inventory and guarded resource
  deletion with explicit confirmation gates.
- `backend-security-audit`: Review backend code, auth, data access, secrets,
  integrations, dependencies, and deployment settings for confirmed security
  findings.
- `legal-policy-drafter`: Draft professional Terms of Service and Privacy Policy
  markdown files from a real codebase.
- `libtermy-implementation`: Implement and optimize libtermy hosts across the
  Rust core, C FFI, and native macOS Swift rendering stack.
- `plain-design-engineer`: Create, restyle, or review frontend interfaces with a
  plain infrastructure-product visual direction.
- `use-aws`: Operate and investigate AWS accounts through profile-aware CLI
  workflows with read-only discovery first and explicit safety gates.
- `no-vibe-code`: Review frontend source and rendered UI for generic design
  patterns with a zero-dependency Node linter, triage matches against the brief,
  and preserve intentional brand choices.
- `no-yak-shaving`: Keep implementation direct and proportionate, reject
  speculative abstractions, and add only tests that protect meaningful behavior.
- `project-orientation-sweep`: Map an unfamiliar checkout, classify its scale,
  identify active surfaces, and choose proportionate validation before editing.
- `project-roadmap`: Inspect the current project and write an evidence-backed
  Markdown roadmap with a clear starting point, phased priorities, useful ideas,
  project guidelines, risks, dependencies, and measurable exit criteria.
- `gitty`: Inspect repository changes and generate, copy, commit, or push
  repository-aware commit messages through Codex, Claude Code, or OpenCode.
- `paper-to-gpui`: Inspect selected Paper designs through MCP and translate
  their layout, typography, assets, states, and tokens into faithful native
  Rust/GPUI views with screenshot-driven validation.
- `clean-codebase`: Coordinate eight evidence-first cleanup agents across
  duplication, types, dead code, cycles, error handling, legacy paths, and slop.
- `build-planetscale-landing-pages`: Design and implement technical,
  proof-heavy landing pages with monospace type, ruled grids, editorial copy,
  restrained accents, and responsive production QA.
- `build-gpui-apps`: Build and review stable native Rust/GPUI apps with
  production-ready starter setup, state architecture, Apple-style materials
  and motion, accessible input and IME, clipboard/drag/drop, menus and
  multi-window lifecycle, packaging, async/performance discipline,
  compile-checked examples, tests, CI, and broader Paper-informed app work.
- `minimize-api-responses`: Build and review API endpoints so each caller gets
  only the fields it needs and is authorized to access, backed by explicit
  response schemas and negative contract tests.
- `tcut-terminal-video`: Create polished, repeatable terminal demos with tcut,
  from easy scripted recordings to TUI automation, browser compositing,
  deterministic tests, re-rendering, and guarded S3-compatible publishing.
- `use-goal`: Run persistent, checkpointed goals with explicit completion
  criteria and clear start, resume, pause, replace, status, and delete commands.
- `codex-image-generation`: Generate or edit raster images through Codex CLI's
  built-in image tool, with complete option boundaries, reference-image
  handling, safe workspace output, and artifact validation.
- `the-cloudflare-stack`: Build full-stack TanStack Start applications on
  Cloudflare Workers with Vite 8, Better Auth, Drizzle, the correct D1 or
  Hyperdrive database lane, R2 storage, Tailwind CSS v4, shadcn/ui, and coss ui.
