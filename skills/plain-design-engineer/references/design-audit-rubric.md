# Design Audit Rubric

Use this reference for `review` mode and for redesign work before editing. Score each category from 1 to 5 and explain the concrete issue behind any score under 4.

## Categories

| Category | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Product clarity | The page could describe any SaaS product | Product is understandable after scanning | Product, audience, and claim are obvious in the first viewport |
| Technical credibility | Decorative or fake-looking UI | Some real product evidence appears | Real artifacts, constraints, metrics, or workflows carry the design |
| Visual hierarchy | Everything competes or feels same-sized | Main path is readable but uneven | Type, spacing, rules, and density guide scanning cleanly |
| Plainness | Trendy gradients/cards dominate | Mostly restrained with some generic polish | Neutral, precise, editorial, and unglossy |
| Density and scanability | Sparse marketing bands or clutter | Mixed density | Dense where useful, with clear row/table/grid structure |
| Typography | Weak scale, poor rhythm, inconsistent fonts | Mostly readable | Tight, confident headings and compact readable body text |
| Artifacts | Missing, fake, or decorative | Present but generic | Specific code/data/diagram/table/log/chart proves the claim |
| Mobile behavior | Proof disappears or text overflows | Works with compromises | Hierarchy and technical proof survive small viewports |
| Copy specificity | Vague claims and buzzwords | Some concrete claims | Direct, specific, evidence-led language |
| Implementation fit | Fights local components/tokens | Some fit | Uses existing primitives and conventions cleanly |

## Review Output

For a design review, lead with findings:

```md
## Findings

1. [Severity] Issue title
   Evidence: file/screenshot/section
   Impact: why it hurts clarity or credibility
   Fix: concrete design change

## Scores

| Category | Score | Notes |
```

Severity:

- High: blocks understanding, trust, mobile use, or primary workflow.
- Medium: weakens clarity, hierarchy, artifact quality, or consistency.
- Low: polish issue with local impact.
