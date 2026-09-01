---
name: codex-image-generation
description: Generate or edit raster images through the Codex CLI and its built-in image generation tool, using the existing ChatGPT login instead of an OpenAI API key. Use when an agent without a native image tool must create project assets with `codex exec`, when the user explicitly asks for Codex CLI image generation, or when configuring prompts, references, output handling, and supported Codex image controls.
---

# Codex Image Generation

Generate images through Codex's built-in `image_gen` tool. Do not invent a
`codex image` subcommand: Codex image generation is agentic and is invoked
through `codex` or `codex exec`.

## Choose the execution path

1. If this agent already has the built-in `image_gen` tool, use it directly.
   Do not recursively start another Codex session.
2. Otherwise, invoke `codex exec` and explicitly tell the child agent to use
   its built-in `imagegen` skill and `image_gen` tool.

Both paths use Codex's ChatGPT authentication and do not require
`OPENAI_API_KEY`. Never silently switch to the Image API, the `openai` CLI, or
an SDK script.

## Preflight for `codex exec`

Run:

```bash
codex --version
codex login status
codex features list
```

Require:

- A current Codex CLI installation.
- A ChatGPT login. If Codex is not logged in, ask the user to run
  `codex login` and choose ChatGPT authentication.
- `image_generation` enabled. It is normally enabled by default; if it is
  disabled, add `--enable image_generation` to the invocation.
- A Codex plan, provider, and selected reasoning model that expose image
  generation. The built-in tool may be unavailable on unsupported plans,
  including ChatGPT Free.

Do not print or inspect authentication files or tokens.

## Generate with `codex exec`

Resolve the workspace and destination to absolute paths before composing the
request. Create the destination's parent directory, then run:

```bash
codex exec \
  --cd "/absolute/path/to/workspace" \
  --sandbox workspace-write \
  --ask-for-approval never \
  --ephemeral \
  --skip-git-repo-check \
  - <<'CODEX_IMAGE_REQUEST'
Use your built-in `imagegen` skill and built-in `image_gen` tool.
Do not use the Image API fallback, `OPENAI_API_KEY`, `openai` CLI, Python SDK,
SVG, HTML, or a placeholder.

Intent: Generate one new raster image.
Use case: product-mockup
Prompt: A matte black ceramic coffee mug on a pale limestone surface.
Composition: Wide editorial product shot; mug in the right third; clean
negative space on the left.
Lighting: Soft overcast window light with natural contact shadows.
Palette: Warm off-white, charcoal, and muted stone.
Exact text: No text.
Constraints: No logo, watermark, border, frame, or extra objects.
Destination: /absolute/path/to/workspace/assets/mug-hero.png

After generation, copy the selected generated PNG to Destination, leaving the
Codex-generated original in place. Do not overwrite an existing destination.
Verify that Destination exists and is non-empty. Finish with the destination
path and the final prompt.
CODEX_IMAGE_REQUEST
```

Use a quoted heredoc delimiter so shell syntax in the image prompt is not
evaluated. Replace the example values before running the command.

Keep `--sandbox workspace-write`; never use
`--dangerously-bypass-approvals-and-sandbox` for image generation. Omit
`--skip-git-repo-check` when repository membership is already guaranteed.

## Edit or use references

Attach each local image with `--image`. State whether each image is an edit
target or a visual reference:

```bash
codex exec \
  --cd "/absolute/path/to/workspace" \
  --sandbox workspace-write \
  --ask-for-approval never \
  --ephemeral \
  --skip-git-repo-check \
  --image "/absolute/path/to/workspace/input/product.png" \
  --image "/absolute/path/to/workspace/input/style-reference.png" \
  - <<'CODEX_IMAGE_REQUEST'
Use your built-in `imagegen` skill and built-in `image_gen` tool.
Do not use the Image API fallback or create an SDK script.

Intent: Edit the first attached image.
Image roles:
- product.png: edit target.
- style-reference.png: lighting and color reference only.
Change: Replace only the background with a warm limestone studio surface.
Preserve: Product identity, shape, proportions, label, camera angle, crop, and
all readable text.
Constraints: Do not redesign the product or add props.
Destination: /absolute/path/to/workspace/assets/product-edited.png

After generation, copy the selected generated PNG to Destination, leaving the
Codex-generated original in place. Do not overwrite an existing destination.
Verify that Destination exists and is non-empty.
CODEX_IMAGE_REQUEST
```

Use at most five attached images. For edits, repeat preservation invariants in
the prompt. A mask, exact pixel boundary, or direct image-model parameter is
not part of the built-in Codex image control surface.

## Prompt contract

Include only fields that improve the request:

- `Intent`: generate or edit.
- `Use case`: the intended asset type.
- `Prompt` or `Change`: the subject and requested outcome.
- `Image roles`: edit target versus style, composition, or content reference.
- `Composition`: framing, viewpoint, subject placement, and negative space.
- `Style`: medium and visual treatment.
- `Lighting`, `Palette`, and `Materials`: concrete visual properties.
- `Exact text`: copy verbatim, or explicitly say no text.
- `Preserve`: edit invariants.
- `Constraints`: omissions and hard negatives.
- `Transparency`: request an actual transparent background when needed.
- `Destination`: an absolute `.png` path inside a writable workspace.

Treat aspect ratio, orientation, dimensions, and transparency as prompt
requirements, not deterministic CLI flags. Preserve a detailed user prompt;
augment a vague prompt only enough to make the requested asset actionable.

For multiple distinct assets, request one `image_gen` call per asset. For
variants, describe each intended variation explicitly. The built-in tool does
not expose `n`.

## Output and validation

Codex first saves built-in results below
`$CODEX_HOME/generated_images/<session>/<call>.png`. There is no built-in
destination-path argument. The child agent must copy the selected image into
the workspace and leave the generated original in place.

After `codex exec` exits:

1. Confirm every destination exists and is non-empty.
2. Inspect each image with the host agent's image-viewing tool when available.
3. Check subject, composition, exact text, edit invariants, constraints, and
   alpha when transparency was requested.
4. If validation fails, make one targeted prompt change and regenerate to a
   versioned filename. Never overwrite unless the user requested replacement.
5. Report the final path and prompt. Do not claim success from Codex's text
   response when the expected file is missing.

## Complete option reference

Read [references/options.md](references/options.md) before adding flags,
changing models, attaching images, or promising exact quality, dimensions,
format, count, background, or seed controls. It separates the complete
built-in image schema from Codex session flags and unsupported Image API
parameters.
