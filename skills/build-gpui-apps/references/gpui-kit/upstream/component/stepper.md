---
url: /component/stepper.md
description: A step-by-step progress for users to navigate through a series of steps or stages.
---

# Stepper

A step-by-step progress component that guides users through a series of steps or stages. Supports horizontal and vertical layouts, custom icons, and different sizes.

## Import

```rust
use gpui_kit::component::stepper::{Stepper, StepperItem};
```

## Usage

### Basic Stepper

Use `selected_index` method to set current active step by index (0-based), default is `0`.

```rust
Stepper::new("my-stepper")
    .selected_index(0)
    .items([
        StepperItem::new().child("Step 1"),
        StepperItem::new().child("Step 2"),
        StepperItem::new().child("Step 3"),
    ])
    .on_click(|step, _, _| {
        println!("Clicked step: {}", step);
    })
```

### With Icons

```rust
use gpui_kit::component::IconName;

Stepper::new("icon-stepper")
    .selected_index(0)
    .items([
        StepperItem::new()
            .icon(IconName::Calendar)
            .child("Order Details"),
        StepperItem::new()
            .icon(IconName::Inbox)
            .child("Shipping"),
        StepperItem::new()
            .icon(IconName::Frame)
            .child("Preview"),
        StepperItem::new()
            .icon(IconName::Info)
            .child("Finish"),
    ])
```

### Vertical Layout

```rust
Stepper::new("vertical-stepper")
    .vertical()
    .selected_index(2)
    .items_center()
    .items([
        StepperItem::new()
            .pb_8()
            .icon(IconName::Building2)
            .child(v_flex().child("Step 1").child("Description for step 1.")),
        StepperItem::new()
            .pb_8()
            .icon(IconName::Asterisk)
            .child(v_flex().child("Step 2").child("Description for step 2.")),
        StepperItem::new()
            .pb_8()
            .icon(IconName::Folder)
            .child(v_flex().child("Step 3").child("Description for step 3.")),
        StepperItem::new()
            .icon(IconName::CircleCheck)
            .child(v_flex().child("Step 4").child("Description for step 4.")),
    ])
```

### Text Center

The `text_center` method centers the text within each step item.

```rust
Stepper::new("center-stepper")
    .selected_index(0)
    .text_center(true)
    .items([
        StepperItem::new().child(
            v_flex()
                .items_center()
                .child("Step 1")
                .child("Desc for step 1."),
        ),
        StepperItem::new().child(
            v_flex()
                .items_center()
                .child("Step 2")
                .child("Desc for step 2."),
        ),
        StepperItem::new().child(
            v_flex()
                .items_center()
                .child("Step 3")
                .child("Desc for step 3."),
        ),
    ])
```

### Different Sizes

```rust
use gpui_kit::component::{Sizable as _, Size};

Stepper::new("stepper")
    .xsmall()
    .items([...])

Stepper::new("stepper")
    .small()
    .items([...])

Stepper::new("stepper")
    .large()
    .items([...])
```

### Disabled State

```rust
Stepper::new("disabled-stepper")
    .disabled(true)
    .items([
        StepperItem::new().child("Step 1"),
        StepperItem::new().child("Step 2"),
    ])
```

### Handle Click Events

```rust
Stepper::new("my-stepper")
    .selected_index(current_step)
    .items([
        StepperItem::new().child("Step 1"),
        StepperItem::new().child("Step 2"),
        StepperItem::new().child("Step 3"),
    ])
    .on_click(cx.listener(|this, step, _, cx| {
        this.current_step = *step;
        cx.notify();
    }))
```

## API Reference

- [Stepper]
- [StepperItem]

### Sizing

Implements [Sizable] trait:

- `xsmall()` - Extra small size
- `small()` - Small size
- `medium()` - Medium size (default)
- `large()` - Large size

## Examples

### Multi-step Form

```rust
Stepper::new("form-stepper")
    .w_full()
    .selected_index(form_step)
    .items([
        StepperItem::new()
            .icon(IconName::User)
            .child("Personal Info"),
        StepperItem::new()
            .icon(IconName::CreditCard)
            .child("Payment"),
        StepperItem::new()
            .icon(IconName::CircleCheck)
            .child("Confirmation"),
    ])
    .on_click(cx.listener(|this, step, _, cx| {
        this.form_step = *step;
        cx.notify();
    }))
```

### Disabled Individual Steps

```rust
Stepper::new("stepper")
    .selected_index(0)
    .items([
        StepperItem::new().child("Available"),
        StepperItem::new().disabled(true).child("Locked"),
        StepperItem::new().child("Available"),
    ])
```

[Stepper]: https://docs.rs/gpui-component/latest/gpui_component/stepper/struct.Stepper.html
[StepperItem]: https://docs.rs/gpui-component/latest/gpui_component/stepper/struct.StepperItem.html
[Sizable]: https://docs.rs/gpui-component/latest/gpui_component/trait.Sizable.html

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/component/stepper) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/component/stepper.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
