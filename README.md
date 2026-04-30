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
npx skills add lassejlv/skills --skill legal-policy-drafter
npx skills add lassejlv/skills --skill plain-design-engineer
```

You can also install from the full GitHub URL:

```sh
npx skills add https://github.com/lassejlv/skills --skill legal-policy-drafter
npx skills add https://github.com/lassejlv/skills --skill plain-design-engineer
```

For local development from this checkout:

```sh
npx skills add . --list
npx skills add . --skill plain-design-engineer
```

## Layout

Each skill lives in its own directory under `skills/` and must include a
`SKILL.md` file with YAML frontmatter:

```text
skills/
  legal-policy-drafter/
    SKILL.md
    references/
    agents/
  plain-design-engineer/
    SKILL.md
    agents/
```

## Skills

- `legal-policy-drafter`: Draft professional Terms of Service and Privacy Policy
  markdown files from a real codebase.
- `plain-design-engineer`: Create, restyle, or review frontend interfaces with a
  plain infrastructure-product visual direction.
