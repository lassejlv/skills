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
```

For local development from this checkout:

```sh
npx skills add . --list
npx skills add . --skill aws-account-cleanup
npx skills add . --skill plain-design-engineer
npx skills add . --skill backend-security-audit
npx skills add . --skill libtermy-implementation
npx skills add . --skill use-aws
npx skills add . --skill no-vibe-code
npx skills add . --skill no-yak-shaving
```

## Layout

Each skill lives in its own directory under `skills/` and must include a
`SKILL.md` file with YAML frontmatter:

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
  no-yak-shaving/
    SKILL.md
    agents/
```

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
- `no-vibe-code`: Lint HTML/CSS/JSX for vibe-coded AI-slop frontend tells (AI
  purple, purple→blue gradients, gradient clip-text, Inter, emoji-as-icons,
  centered-hero + three cards) via a zero-dependency Node driver that fails the
  build on high-severity findings.
- `no-yak-shaving`: Keep implementation direct and proportionate, reject
  speculative abstractions, and add only tests that protect meaningful behavior.
