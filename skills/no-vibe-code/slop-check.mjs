#!/usr/bin/env node
// slop-check.mjs — static detector for "vibe-coded" / AI-slop frontend tells.
//
// Scans HTML / CSS / JSX / TSX / Vue / Svelte for the specific visual
// fingerprints that mark a UI as generated-by-default rather than designed:
// AI purple, purple→blue gradients, gradient clip-text, Inter everywhere,
// glassmorphism, emoji-as-icons, centered-hero+3-cards, colored left-border
// cards, badge-above-H1, 01/02/03 step boxes, stat banners, forced dark mode,
// untouched shadcn defaults, neon glows, all-caps labels.
//
// No dependencies. Node >= 18.
//
// Usage:
//   node slop-check.mjs <file-or-dir> [more...]     # default: fail on HIGH
//   node slop-check.mjs src --strict                # also fail on MEDIUM
//   node slop-check.mjs src --json                  # machine-readable
//   node slop-check.mjs src --quiet                 # summary line only
//
// Exit codes: 0 clean(-enough) · 1 tells found at failing severity · 2 bad args.

import fs from "node:fs";
import path from "node:path";

const SCAN_EXT = new Set([".html", ".htm", ".css", ".scss", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro"]);
const SKIP_DIR = new Set(["node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "coverage", ".svelte-kit"]);

// ---------- color math: catch "AI purple" by computed hue, not a fixed list ----------
function hexToHsl(hex) {
  let h = hex.replace("#", "");
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (h.length !== 6) return null;
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
  let hue = 0;
  if (d !== 0) {
    if (max === r) hue = ((g - b) / d) % 6;
    else if (max === g) hue = (b - r) / d + 2;
    else hue = (r - g) / d + 4;
    hue *= 60;
    if (hue < 0) hue += 360;
  }
  const l = (max + min) / 2;
  const s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));
  return { h: hue, s, l };
}
// "VibeCode purple": violet/indigo hue, saturated enough to read as an accent, mid lightness.
function isAiPurple(hex) {
  const c = hexToHsl(hex);
  return !!c && c.h >= 252 && c.h <= 288 && c.s >= 0.35 && c.l >= 0.35 && c.l <= 0.82;
}

// ---------- per-line rules ----------
// Each: {id, sev, test(line)->matchString|null, msg, fix}. Keep regexes anchored to real markup.
const RULES = [
  {
    id: "ai-purple-hex",
    sev: "high",
    test: (line) => {
      for (const m of line.matchAll(/#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g)) if (isAiPurple(m[0])) return m[0];
      return null;
    },
    msg: "AI-purple accent (violet/indigo hue) — the #1 tell of a generated UI.",
    fix: "Pick a palette from the subject's own world before coding. Dump lavender.",
  },
  {
    id: "ai-purple-class",
    sev: "high",
    test: (line) => (/\b(bg|text|from|via|to|border|ring|shadow|fill|stroke)-(purple|violet|indigo|fuchsia)-[0-9]{2,3}\b/.exec(line) || [])[0] || null,
    msg: "Tailwind purple/violet/indigo utility used as accent.",
    fix: "Replace the hue with a chosen brand color; earth tones or one strong opinion.",
  },
  {
    id: "purple-blue-gradient",
    sev: "high",
    test: (line) => {
      if (/\b(from|via)-(purple|violet|indigo|fuchsia)-[0-9]{2,3}\b/.test(line) && /\b(to|via)-(blue|sky|cyan|indigo)-[0-9]{2,3}\b/.test(line)) return "from-purple…to-blue";
      if (/\b(from|via)-(blue|sky|cyan|indigo)-[0-9]{2,3}\b/.test(line) && /\b(to|via)-(purple|violet|indigo|fuchsia)-[0-9]{2,3}\b/.test(line)) return "from-blue…to-purple";
      if (/linear-gradient\([^)]*\)/i.test(line)) {
        const g = line.match(/linear-gradient\([^)]*\)/i)[0];
        const hasPurple = [...g.matchAll(/#[0-9a-fA-F]{3,6}\b/g)].some((m) => isAiPurple(m[0])) || /\b(purple|violet|indigo|blueviolet|rebeccapurple)\b/i.test(g);
        const hasBlue = /\b(blue|dodgerblue|royalblue|#[0-9a-fA-F]*)\b/i.test(g) && [...g.matchAll(/#[0-9a-fA-F]{6}\b/g)].some((m) => { const c = hexToHsl(m[0]); return c && c.h >= 200 && c.h <= 250; });
        if (hasPurple && (hasBlue || /\bblue\b/i.test(g))) return g.slice(0, 48);
      }
      return null;
    },
    msg: "Purple→blue gradient — the signature generated-landing-page fill.",
    fix: "One intentional gradient max, in brand hues — or a solid color.",
  },
  {
    id: "gradient-cliptext",
    sev: "high",
    test: (line) => {
      if (/bg-clip-text/.test(line) && /text-transparent/.test(line) && /\bbg-gradient|from-/.test(line)) return "bg-clip-text gradient";
      if (/background-clip:\s*text/i.test(line) || /-webkit-background-clip:\s*text/i.test(line)) return "background-clip:text";
      return null;
    },
    msg: "Gradient clip-text headline — high-ranked slop tell.",
    fix: "Solid, high-contrast headline. Let type + copy carry the hero, not a gradient.",
  },
  {
    id: "inter-font",
    sev: "high",
    test: (line) => {
      if (/font-family:[^;}]*\bInter\b/i.test(line)) return "font-family: Inter";
      if (/family=Inter\b/.test(line)) return "Google Fonts Inter";
      if (/["'`]--font-inter|\bnext\/font[^)]*Inter\b/.test(line)) return "next/font Inter";
      return null;
    },
    msg: "Inter — the Helvetica of the LLM era; the default nobody chose.",
    fix: "Choose a display+body pair for THIS brief (e.g. not Inter/Geist/Space Grotesk).",
  },
  {
    id: "overused-typepair",
    sev: "low",
    test: (line) => (/font-family:[^;}]*\b(Space Grotesk|Instrument Serif|Geist)\b/i.exec(line) || /family=(Space\+Grotesk|Instrument\+Serif|Geist)\b/.exec(line) || [])[0] || null,
    msg: "Space Grotesk / Instrument Serif / Geist — the current default 'tasteful' pairing.",
    fix: "Fine occasionally, but it's the new median. Justify it or pick something specific.",
  },
  {
    id: "glassmorphism",
    sev: "medium",
    test: (line) => (/backdrop-filter:\s*blur|(?:^|["\s])backdrop-blur(?:-|["\s])/i.exec(line) || [])[0] || null,
    msg: "Glassmorphism (backdrop blur) — peaked in 2022, now a generated-default.",
    fix: "Solid or subtly-varied backgrounds. Reserve blur for a real depth reason.",
  },
  {
    id: "neon-glow",
    sev: "medium",
    test: (line) => {
      const m = line.match(/box-shadow:\s*([^;}]+)/i);
      if (m && /\b0\s+0\s+\d{2,}px/.test(m[1]) && /(rgba?\(|#[0-9a-fA-F]{3,6}|hsl)/i.test(m[1]) && !/rgba\([^)]*,\s*0?\.[01]?\d?\s*\)/i.test(m[1])) return "glow box-shadow";
      if (/shadow-(purple|violet|indigo|blue|cyan|pink|fuchsia)-/.test(line)) return "colored shadow util";
      if (/drop-shadow-\[0_0_/.test(line)) return "drop-shadow glow";
      return null;
    },
    msg: "Neon glow / large colored shadow — unprompted bloom, reads as AI.",
    fix: "Subtle single-color shadow: 0 2px 8px rgba(0,0,0,.08). Drop colored glows.",
  },
  {
    id: "colored-left-border-card",
    sev: "high",
    test: (line) => {
      if (/\bborder-l-(4|\[\d+px\])\b/.test(line) && /\b(border|from|bg)-(purple|violet|indigo|blue|cyan|emerald|red|amber)-/.test(line)) return "border-l-4 + color";
      if (/border-left:\s*[34]px\s+solid/i.test(line)) return "border-left:3/4px solid";
      return null;
    },
    msg: "Colored left-border card — the 3–4px accent stripe, a distinctive tell.",
    fix: "Drop the stripe. Use a subtle outline, background tint, or real shadow.",
  },
  {
    id: "emoji-as-icon",
    sev: "high",
    test: (line) => (/[🚀⚡🎯✨🔥💡🎨📈📊🛡️🔒✅🌟💪🙌👉⭐️🌈💎🧠⭐]/u.exec(line) || [])[0] || null,
    msg: "Emoji used as iconography — instant giveaway.",
    fix: "Custom or a single consistent SVG icon set (lucide/heroicons themed), or none.",
  },
  {
    id: "grid-cols-3-cards",
    sev: "medium",
    test: (line) => (/\b(sm:|md:|lg:)?grid-cols-3\b/.exec(line) || [])[0] || null,
    msg: "Three-column card grid — half of the 'centered hero + 3 cards' homepage.",
    fix: "Vary the layout: asymmetry, differing card sizes/roles, editorial structure.",
  },
  {
    id: "step-number-boxes",
    sev: "low",
    test: (line) => (/>\s*0[1-9]\s*<|>\s*(01|02|03)\b|\bstep-(1|2|3)\b/.exec(line) || [])[0] || null,
    msg: "01 / 02 / 03 numbered step boxes — only justified if order truly matters.",
    fix: "Number only real sequences. Otherwise use a timeline or connected flow.",
  },
  {
    id: "stat-banner",
    sev: "low",
    test: (line) => (/\b\d{1,3}(\.\d)?[KMB]\+|\b99(\.9+)?%|\b\d{1,3}x\b\s*(faster|better|more)?/i.exec(line) || [])[0] || null,
    msg: "Stat-banner metric (10K+ / 99.9% / 3x) — generic trust-badge filler.",
    fix: "Weave real numbers into narrative copy, or drop unverifiable vanity stats.",
  },
  {
    id: "all-caps-label",
    sev: "low",
    test: (line) => (/text-transform:\s*uppercase|(?:^|["\s])uppercase(?:["\s])/i.exec(line) || [])[0] || null,
    msg: "All-caps labels/headings — the generated eyebrow-label look.",
    fix: "Sentence case. Reserve caps for one deliberate brand moment.",
  },
  {
    id: "forced-dark",
    sev: "low",
    test: (line) => (/<(html|body)[^>]*\bclass=["'][^"']*\bdark\b|bg-(black|slate-950|gray-950|zinc-950|neutral-950)\b/.exec(line) || [])[0] || null,
    msg: "Hard-forced dark theme — the default permanent-dark generated look.",
    fix: "Make light/dark a real choice for the brief; if dark, hit WCAG AA on body text.",
  },
  {
    id: "shadcn-default-radius",
    sev: "low",
    test: (line) => (/--radius:\s*0\.5rem\b/.exec(line) || [])[0] || null,
    msg: "Untouched shadcn default (--radius: 0.5rem) — components shipped as-installed.",
    fix: "Customize tokens: radius, shadows, primary. Don't ship the library default.",
  },
];

// ---------- scan ----------
function collectFiles(target, acc) {
  let st;
  try { st = fs.statSync(target); } catch { return; }
  if (st.isDirectory()) {
    if (SKIP_DIR.has(path.basename(target))) return;
    for (const e of fs.readdirSync(target)) collectFiles(path.join(target, e), acc);
  } else if (SCAN_EXT.has(path.extname(target).toLowerCase())) {
    acc.push(target);
  }
}

function scanFile(file) {
  const findings = [];
  const text = fs.readFileSync(file, "utf8");
  const lines = text.split(/\r?\n/);

  // per-line rules
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const r of RULES) {
      const hit = r.test(line);
      if (hit) findings.push({ file, line: i + 1, id: r.id, sev: r.sev, snippet: String(hit).trim().slice(0, 60), msg: r.msg, fix: r.fix });
    }
  }

  const lineAt = (idx) => text.slice(0, idx).split(/\r?\n/).length;

  // whole-file rule: "gradients everywhere" — count fills, flag if piled on
  const gradCount = (text.match(/linear-gradient\(|\bbg-gradient-to-[trbl]{1,2}\b/gi) || []).length;
  if (gradCount >= 4) findings.push({ file, line: 0, id: "gradients-everywhere", sev: "medium", snippet: `${gradCount} gradients`, msg: `Gradients piled on (${gradCount}× in one file).`, fix: "One or two intentional gradients per view, max." });

  // whole-file rule: "badge above H1" — a rounded-full pill shortly before a hero <h1> (spans lines)
  const badge = /<(span|div|a|p)\b[^>]*\brounded-full\b[^>]*>[\s\S]{0,140}?<h1\b/i.exec(text);
  if (badge) findings.push({ file, line: lineAt(badge.index), id: "badge-above-h1", sev: "medium", snippet: "pill → h1", msg: "Little pill/badge stacked directly above the H1 — canonical hero cliché.", fix: "Cut the badge or fold its info into the headline. Don't stack badge→H1." });

  return findings;
}

// ---------- cli ----------
const args = process.argv.slice(2);
const flags = new Set(args.filter((a) => a.startsWith("--")));
const targets = args.filter((a) => !a.startsWith("--"));
if (targets.length === 0) {
  console.error("usage: node slop-check.mjs <file-or-dir> [more...] [--strict] [--json] [--quiet]");
  process.exit(2);
}

const files = [];
for (const t of targets) collectFiles(t, files);
const findings = files.flatMap(scanFile);

const SEV_ORDER = { high: 0, medium: 1, low: 2 };
findings.sort((a, b) => SEV_ORDER[a.sev] - SEV_ORDER[b.sev] || a.file.localeCompare(b.file) || a.line - b.line);

const counts = { high: 0, medium: 0, low: 0 };
for (const f of findings) counts[f.sev]++;

const useColor = process.stdout.isTTY && !flags.has("--json");
const C = useColor
  ? { high: "\x1b[91m", medium: "\x1b[93m", low: "\x1b[90m", dim: "\x1b[2m", bold: "\x1b[1m", reset: "\x1b[0m", green: "\x1b[92m" }
  : { high: "", medium: "", low: "", dim: "", bold: "", reset: "", green: "" };

const failOn = flags.has("--strict") ? ["high", "medium"] : ["high"];
const failCount = failOn.reduce((n, s) => n + counts[s], 0);

if (flags.has("--json")) {
  console.log(JSON.stringify({ files: files.length, counts, findings, failing: failCount }, null, 2));
  process.exit(failCount > 0 ? 1 : 0);
}

if (!flags.has("--quiet")) {
  for (const f of findings) {
    const tag = f.sev.toUpperCase().padEnd(6);
    const loc = f.line ? `${f.file}:${f.line}` : f.file;
    console.log(`${C[f.sev]}${tag}${C.reset} ${C.bold}${f.id}${C.reset} ${C.dim}${loc}${C.reset}`);
    console.log(`       ${f.msg}`);
    if (f.snippet) console.log(`       ${C.dim}match:${C.reset} ${f.snippet}`);
    console.log(`       ${C.green}fix:${C.reset}   ${f.fix}`);
    console.log("");
  }
}

const summary = `${files.length} file(s) scanned · ${C.high}${counts.high} high${C.reset} · ${C.medium}${counts.medium} medium${C.reset} · ${C.low}${counts.low} low${C.reset}`;
console.log(summary);
if (failCount > 0) {
  console.log(`${C.high}${C.bold}FAIL${C.reset}: ${failCount} tell(s) at failing severity (${failOn.join("/")}).`);
  process.exit(1);
} else {
  console.log(`${C.green}${C.bold}PASS${C.reset}: no tells at failing severity.`);
  process.exit(0);
}
