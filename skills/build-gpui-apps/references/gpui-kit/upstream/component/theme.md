---
url: /component/theme.md
description: Customize colors, typography, radii, and light or dark appearance with the GPUI Component theme system.
---

# Theme

All components support theming through the built-in Theme system, the [ActiveTheme] trait provides access to the current theme colors:

```rs
use gpui_kit::component::{ActiveTheme as _};

// Access theme colors in your components
cx.theme().primary
cx.theme().background
cx.theme().foreground
```

So if you want use the colors from the current theme, you should keep your component or view have [App] context.

## Gradient Backgrounds

Theme color values remain backward compatible with the existing string format:

```json
{
  "colors": {
    "button.primary.background": "#4F46E5"
  }
}
```

Background tokens that opt in to gradient rendering can also use CSS-style two-stop linear gradients:

```json
{
  "colors": {
    "button.primary.background": "linear-gradient(135deg, #4F46E5, #06B6D4)",
    "button.primary.hover.background": "linear-gradient(to right, red-500 25%, blue-600 75%)"
  }
}
```

Top-level theme fields, such as `cx.theme().button_primary`, remain solid `Hsla` values for compatibility. Code that needs the full resolved token can use `cx.theme().tokens.button_primary`; its `.color` field is the solid representative color, and its `.background` field contains the configured `Background`, including gradients.

## Theme Registry

There have more than 20 built-in themes available in [themes](https://github.com/longbridge/gpui-kit/tree/main/themes) folder.

https://github.com/longbridge/gpui-kit/tree/main/themes

And we have a [ThemeRegistry] to help us to load themes.

Use the `name` of an entry in the `themes` array, such as `Ayu Light`, when looking up a theme from the registry.

```rs
use std::path::PathBuf;
use gpui_kit::{App, SharedString};
use gpui_kit::component::{Theme, ThemeRegistry};

pub fn init(cx: &mut App) {
    let theme_name = SharedString::from("Ayu Light");
    // Load and watch themes from ./themes directory
    if let Err(err) = ThemeRegistry::watch_dir(PathBuf::from("./themes"), cx, move |cx| {
        if let Some(theme) = ThemeRegistry::global(cx)
            .themes()
            .get(&theme_name)
            .cloned()
        {
            Theme::update(cx, |current| current.apply_config(&theme));
        }
    }) {
        tracing::error!("Failed to watch themes directory: {}", err);
    }
}
```

[ActiveTheme]: https://docs.rs/gpui-component/latest/gpui_component/theme/trait.ActiveTheme.html
[ThemeRegistry]: https://docs.rs/gpui-component/latest/gpui_component/theme/struct.ThemeRegistry.html
[App]: https://docs.rs/gpui/latest/gpui/struct.App.html

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/component/theme) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/component/theme.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
