# Skills

Personal agent skills packaged as a multi-skill repository.

## Install

List available skills from this checkout:

```sh
npx skills add . --list
```

Install every skill:

```sh
npx skills add . --skill '*'
```

Install one skill:

```sh
npx skills add . --skill legal-policy-drafter
npx skills add . --skill plain-design-engineer
```

After this repo is pushed to GitHub, replace `.` with `owner/repo` or the full
GitHub URL:

```sh
npx skills add owner/repo --skill legal-policy-drafter
npx skills add owner/repo --skill plain-design-engineer
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
