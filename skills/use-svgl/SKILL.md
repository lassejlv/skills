---
name: use-svgl
description: Find and add brand and technology SVG logos (GitHub, Stripe, Vercel, React, Postgres, OpenAI and ~1000 more) from svgl.app through its free public API. Use when a UI, landing page, README, docs site, integrations grid, "built with" or "sign in with" section, footer or slide needs the official logo or wordmark of a company, product, framework, language or service, including light and dark variants. Not for generic UI icons (arrows, settings, trash, menu); use the project's icon library for those.
---

# Use SVGL

[SVGL](https://svgl.app) is a curated library of brand and technology logos. Its API is free, needs no key, and returns clean, svgo-optimized SVG code. Use it instead of drawing a logo by hand, guessing paths from memory, or hotlinking a random image from a search result.

SVGL has logos only. For generic interface icons, use the icon set the project already uses (Lucide, Heroicons, Phosphor, Hugeicons and so on).

## Workflow

1. **Search** for each brand by name.
2. **Pick** the right entry and variant: icon or wordmark, light or dark.
3. **Fetch** the SVG code and save it into the project as a local asset or component.
4. **Wire it up** so it follows the app's theme, sizes from the container and has an accessible name.
5. **Check** it renders on the backgrounds it will sit on.

`scripts/svgl.py` (next to this file, Python 3 standard library only) does steps 1–3:

```sh
python3 <skill dir>/scripts/svgl.py search stripe            # list matches with every variant URL
python3 <skill dir>/scripts/svgl.py search postgres --json   # raw API JSON
python3 <skill dir>/scripts/svgl.py category database        # browse a category
python3 <skill dir>/scripts/svgl.py categories               # all categories with counts
python3 <skill dir>/scripts/svgl.py get github --out src/assets/logos
python3 <skill dir>/scripts/svgl.py get mongodb --wordmark --out public/logos
```

`get` saves the best title match. With light/dark variants it saves both (`github-light.svg`, `github-dark.svg`); pass `--variant light` or `--variant dark` for one. Pass `--id <n>` when the search has several close matches, and `--no-optimize` for the original, unoptimized file. Without `--out` it prints the SVG to stdout.

curl works too; see [API reference](#api-reference).

## Picking the right logo

- **Match the exact product.** `search=git` returns Git, GitHub, GitLab, GitHub Copilot and Digital Ocean. Read the titles and pick the one the user means. Searching a short or generic word returns noise, so search with the full brand name.
- **Icon vs wordmark.** `route` is the symbol (square-ish mark). `wordmark`, when present, is the logo with the name spelled out. Use the icon in tight spaces (buttons, avatars, grids of many logos, favicons) and the wordmark where the name should be read (hero "trusted by" rows, partner sections). Not every entry has a wordmark.
- **Light vs dark.** When `route` or `wordmark` is an object, `light` is the version **for a light background** (usually dark ink) and `dark` is the version **for a dark background**. Ship both when the app has a dark mode. A single string means one version for every background; check it has enough contrast on both.
- **Brand guidelines.** If the entry has `brandUrl`, the brand publishes usage rules. Follow them when the logo carries the brand's identity (partner pages, "sign in with" buttons): no recoloring, stretching or cropping unless the guide allows it.
- **Nothing found.** The API answers `404 {"error": "... SVG not found"}`. Try another spelling, the parent company, or browse the category. If it is still missing, tell the user and ask for an official asset or the brand's press kit. Do not invent a logo path from memory.

## Adding it to the project

Save the SVG into the repo. Do not hotlink `svgl.app` URLs from production code: the library's file names can change, and the user's site should not depend on someone else's server.

Follow the project's existing pattern for icons and images. If there is none:

- **React/Vue/Svelte:** make a small component per logo, or one `BrandLogo` component that maps names to inline SVG. Keep the original `viewBox`. Remove fixed `width`/`height` attributes so CSS sizes it, and spread props such as `className` onto the `<svg>`.
- **Plain HTML or static sites:** keep `.svg` files in the assets folder and use `<img src="..." alt="Stripe">`.
- **Light/dark pairs:** swap with the app's theme mechanism, for example two elements with `dark:hidden` / `hidden dark:block`, or `<picture>` with `prefers-color-scheme`. For single-color marks that should follow text color, replace the fill with `currentColor` only when brand rules allow it.
- **Accessibility:** a logo that stands alone needs a name (`role="img"` plus `aria-label`, or `<title>`, or `alt` on `<img>`). A logo next to visible text with the same name gets `aria-hidden="true"`.
- **Inline SVG ids:** svgo-optimized files can still carry `id`s (`clipPath`, gradients). When several inline logos share a page, make the ids unique so they don't collide.

## Etiquette

- The API is rate limited. Search once per brand, reuse what you fetched, and never request in a loop over the full catalogue. Avoid `https://api.svgl.app` without `search`, `limit` or a category; it returns everything.
- SVGL asks that the API is not used to rebuild SVGL itself. Fetching logos for the user's own project is the intended use.
- Logos are trademarks of their owners. Using them to refer to a product is normal; implying endorsement is not. Mention it to the user when a page looks like it claims partnerships.

## API reference

Base URL `https://api.svgl.app`. No authentication.

| Request | Returns |
| --- | --- |
| `GET /?search=<title>` | Entries whose title matches |
| `GET /?limit=<n>` | First `n` entries |
| `GET /category/<category>` | Entries in one category (lowercase, e.g. `database`, `ai`) |
| `GET /categories` | `[{ "category": "Software", "total": 288 }, ...]` |
| `GET /svg/<file>.svg` | SVG code, optimized with svgo |
| `GET /svg/<file>.svg?no-optimize` | Original SVG code |

`<file>` is the last path segment of a `route` or `wordmark` URL: `https://svgl.app/library/github_light.svg` → `/svg/github_light.svg`.

Entry shape:

```ts
type ThemeOptions = { light: string; dark: string };

interface SVG {
  id: number;
  title: string;
  category: string | string[];
  route: string | ThemeOptions;      // icon
  wordmark?: string | ThemeOptions;  // logo with name
  url: string;                       // brand website
  brandUrl?: string;                 // brand guidelines
}
```

```sh
curl -s "https://api.svgl.app?search=stripe"
curl -s "https://api.svgl.app/svg/stripe.svg" -o stripe.svg
```
