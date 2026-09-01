# Codex image option reference

This reference covers Codex CLI's built-in image generation path, not the
separate OpenAI Image API.

Codex CLI evolves. Before relying on session flags, compare this reference with:

```bash
codex --version
codex exec --help
codex features list
```

Authoritative upstream references:

- [Codex CLI reference](https://developers.openai.com/codex/cli/reference)
- [Built-in image tool schema and implementation](https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/src/tool.rs)
- [Built-in image tool instructions](https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/imagegen_description.md)
- [Official imagegen skill](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md)

## Complete built-in `image_gen` schema

The built-in tool accepts exactly three fields. Unknown fields are rejected.

### `prompt`

- Type: string.
- Required.
- Used for both new generation and editing.
- Put subject, composition, style, exact text, constraints, preservation
  invariants, orientation, and transparency requirements here.

### `referenced_image_paths`

- Type: array of absolute local image paths.
- Optional.
- Length: one to five paths when present.
- Supplying it changes the request from generation to editing/reference-based
  generation.
- Use it when every target image has a stable local path.
- In a parent agent's `codex exec` command, attach those files with
  repeatable `--image` flags and explain every image's role in the prompt. The
  child Codex agent maps visible local inputs to its internal tool call.

### `num_last_images_to_include`

- Type: integer.
- Optional.
- Range: 1 through 5.
- Includes that many recent conversation images in an edit.
- Use only inside a continuing Codex conversation when at least one target
  image has no local path.
- Do not use in the normal one-shot `codex exec` workflow; prefer local paths
  and `--image`.

`referenced_image_paths` and `num_last_images_to_include` are mutually
exclusive. Omit both for a brand-new image.

## Fixed built-in request behavior

The built-in implementation currently sends:

- Image model: `gpt-image-2`.
- Size: `auto`.
- Quality: `auto`.
- Background: `auto`.
- Count: the request leaves `n` unset and returns one image.
- Saved artifact format: PNG.
- Maximum edit/reference images: five.

These are implementation behavior, not user-settable built-in tool fields.
`--model` on `codex exec` selects the Codex reasoning model; it does not select
the image model.

Transparency, aspect ratio, orientation, and desired dimensions can be
requested in `prompt`, but they are not hard parameter guarantees. Validate the
result rather than reporting them as configured API values.

## Dedicated Codex configuration

There is one current image-specific Codex feature switch:

```toml
[features]
image_generation = true
```

Equivalent one-run CLI forms:

```bash
codex exec --enable image_generation ...
codex exec -c features.image_generation=true ...
```

The feature is normally stable and enabled by default. Prefer the default;
override it only when runtime inspection shows it disabled. Use
`--strict-config` when testing hand-written configuration so unknown keys fail
instead of being ignored.

## `codex exec` flags relevant to image work

These configure the Codex session around the built-in image tool. They are not
image-rendering parameters.

### Inputs and workspace

- `-i, --image <FILE>...`: attach local input or reference images. Repeat for
  multiple files; keep the total used by `image_gen` at five or fewer.
- `-C, --cd <DIR>`: set the child agent's working root.
- `--add-dir <DIR>`: make an additional directory writable. Prefer keeping
  final output inside `--cd`.
- `-s, --sandbox workspace-write`: allow the child to copy the generated
  artifact into the workspace without granting full machine access.
- `--skip-git-repo-check`: allow a working root outside Git. Omit it in a known
  repository.

### Authentication-independent session selection

- `-m, --model <MODEL>`: select the Codex reasoning model. This does not change
  `gpt-image-2`, the built-in image backend.
- `-p, --profile <PROFILE>`: layer a Codex configuration profile.
- `-c, --config <key=value>`: override a Codex config value for one run.
- `--enable <FEATURE>` / `--disable <FEATURE>`: change a feature switch for
  one run.
- `--strict-config`: reject unknown config keys.
- `--ignore-user-config`: ignore user config for the run. Authentication still
  comes from `CODEX_HOME`; avoid this when the user's profile supplies required
  provider settings.
- `--ignore-rules`: skip user or project exec-policy rule files. Do not use it
  merely to bypass a legitimate policy failure.

### Approval and lifecycle

- `-a, --ask-for-approval never`: avoid an unattended child process waiting for
  approval while retaining the sandbox.
- `--approve-for-me`: route approval requests through automatic review. Use
  instead of `never` only when the workflow needs commands that merit review.
- `--ephemeral`: do not persist the child session. Generated artifacts still
  need to be copied to the requested workspace destination.

Never use `--dangerously-bypass-approvals-and-sandbox` for this workflow.

### Machine-readable agent output

- `--json`: stream Codex events as JSONL.
- `-o, --output-last-message <FILE>`: save the child agent's final text
  message.
- `--output-schema <FILE>`: constrain the final text response with JSON
  Schema.
- `--color <always|never|auto>`: control terminal color.

These flags capture agent events or text, not image bytes. The generated PNG is
a file side effect and must be verified separately.

### Unsupported providers

`--oss` and `--local-provider` select local/open-source providers. They do not
provide Codex's built-in image backend. Do not use them for this workflow.

## Options Codex built-in image generation does not expose

Do not pass or claim any of these as `codex` image flags:

- `--size`
- `--quality`
- `--background`
- `--output-format`
- `--output-compression`
- `--n`
- `--seed`
- `--moderation`
- `--input-fidelity`
- `--mask`
- `--out` or `--output`

There is no `codex image`, `codex images generate`, or
`codex exec --output-image` command.

Some similarly named options exist in the separate OpenAI Image API or in the
official imagegen skill's API fallback script. That path requires an
`OPENAI_API_KEY`, uses API billing, and is not equivalent to built-in Codex
image generation. If a user needs deterministic API controls, explain the
difference and get explicit approval before changing paths.

## Availability and failure meanings

The tool is exposed only when all of these are true:

- `features.image_generation` is enabled.
- The active provider supports Codex image generation and namespace tools.
- The selected Codex reasoning model accepts image input.
- Codex is using a compatible ChatGPT/Codex backend authentication path.
- The account plan supports the built-in image tool. ChatGPT Free does not
  currently expose it.

Diagnose failures in this order:

1. Confirm `codex login status` reports a ChatGPT login.
2. Confirm `codex features list` shows `image_generation` enabled.
3. Retry with the default Codex model and no custom provider/profile.
4. Confirm each reference path exists and no more than five are attached.
5. Confirm `referenced_image_paths` and recent-conversation images are not
   being mixed.
6. Check whether the plan reports an image-generation usage limit.

Do not respond to a missing built-in tool by silently calling a paid API.
