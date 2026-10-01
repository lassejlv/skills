# GPUI Kit documentation index

Retrieved 2026-10-01T10:02:28+00:00. All **183 English pages** from the [official index](https://gpui-kit.com/llms.txt) are bundled below. Chinese translations remain discoverable in `llms.txt`; images stay remote.

Read only the pages relevant to the task. These are documentation snapshots, not proof that an API exists in a project's locked version. See `manifest.json` for page sources and SHA-256 hashes.

Credit: [GPUI Kit](https://gpui-kit.com). Prose and original illustrations: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Third-party material retains its terms. Links and attribution are adapted; the guide content is retained.


## Application guides

| Page | Covers |
| --- | --- |

| [Accessibility](docs/accessibility.md) | Build and test accessible GPUI Kit interfaces with AccessKit semantics and actions. |

| [Action](docs/action.md) | Define typed commands and route them through focus, key contexts, and GPUI's dispatch path. |

| [Animation](docs/animation.md) | Choose GPUI element animation, GPUI Base motion, and GPUI Component motion with correct identity, interruption, and reduced-motion behavior. |

| [Auto Update](docs/auto-update.md) | Plan safe update checks, verified downloads, installation, and restart for GPUI Kit desktop apps. |

| [Coding Guides](docs/coding-guides.md) | Architecture and coding conventions for maintainable GPUI Kit applications |

| [Comparison](docs/comparison.md) | Compare GPUI Kit, Iced, egui, Qt 6, and Slint for desktop application architecture and capabilities. |

| [Context](docs/context.md) | Understand how GPUI provides application, Entity, Window, and async access. |

| [Design Guides](docs/design-guides.md) | Product and interaction design guidance for GPUI Kit applications |

| [Element](docs/element.md) | Understand GPUI's element tree and low-level rendering lifecycle. |

| [ElementId](docs/element_id.md) | Give GPUI elements stable identity and understand how keyed state survives frames. |

| [Entity](docs/entity.md) | Create, share, read, update, and observe state with GPUI Entity. |

| [Event](docs/event.md) | Use GPUI Events for typed notifications and connect them to Actions. |

| [Focus](docs/focus.md) | Build keyboard reachable GPUI views with stable focus handles, focus events, and safe focus traps. |

| [Fonts](docs/fonts.md) | System fonts, theme fonts, per-element overrides, and bundling custom fonts. |

| [FPS Monitor](docs/fps.md) | Read the gpui-fps HUD — what MAX FPS is, why it is derived rather than counted, and what each row measures. |

| [Geometry](docs/geometry.md) | Work with GPUI's typed coordinates, layout lengths, and colors in practical UI code. |

| [Getting Started](docs/getting-started.md) | Build your first GPUI Kit desktop application with one dependency and one view. |

| [Global](docs/global.md) | Share application-wide state with GPUI Global, and connect changes to Views and windows. |

| [GPUI Kit](docs.md) | A comprehensive Rust framework for building fantastic, high-performance desktop applications with GPUI. |

| [I18N](docs/i18n.md) | Set up translations, switch locales, and check text behavior in GPUI Kit. |

| [Icons & Assets](docs/assets.md) | Configure bundled icons and custom assets for GPUI Kit applications. |

| [Images](docs/image.md) | How img() and svg() load, decode, size, and cache images, and how to cache remote images over HTTP. |

| [Installation](docs/installation.md) | Install GPUI Kit and the platform dependencies required to build Rust desktop applications on macOS, Windows, and Linux. |

| [KeyBinding](docs/keybinding.md) | Bind GPUI Actions to keys, chords, and focused Key Contexts. |

| [Mobile](docs/mobile.md) | Build an iOS application or embed GPUI Kit in a Swift UIKit container with the experimental gpui-pre-mobile platform. |

| [Multi Window](docs/multi-window.md) | Open multiple GPUI Kit windows, share application state, route work to the right window, and handle closing and restoration. |

| [Native Extensions](docs/native-extension.md) | Integrate native menus and child views with GPUI Kit, including handles, layout, input, lifetime, and platform limits. |

| [Packaging](docs/packaging.md) | Turn a GPUI Kit release build into a macOS app and DMG, a Windows installer, or a Linux tarball and DEB. |

| [Paint](docs/paint.md) | Draw custom geometry in GPUI and understand the boundary between layout, hit testing, and painting. |

| [Render](docs/render.md) | Turn Entity state into an element tree and understand when GPUI rebuilds a View. |

| [RenderOnce](docs/render-once.md) | Build reusable, declarative GPUI components from owned data. |

| [SharedString](docs/shared-string.md) | Choose and use GPUI's immutable, cheaply cloned text for UI state and components. |

| [Style](docs/style.md) | Style GPUI elements with Tailwind CSS–familiar utilities, typed values, and fluent Rust builders. |

| [SystemNotification](docs/system-notification.md) | Send OS notifications with GPUI, handle activation, and understand GPUI Kit's Notification integration and platform limits. |

| [Task](docs/task.md) | Run asynchronous work with GPUI Task, control its lifetime, and return results to the UI. |

| [Testing](docs/test.md) | Test GPUI Kit applications and GPUI behavior with Rust unit tests, TestAppContext, native UI interactions, layout assertions and CI. |

| [TextSystem](docs/text-system.md) | Shape, measure, lay out, and paint text through GPUI's text system and GPUI Kit components. |

| [View Cache](docs/view-cache.md) | Reuse clean GPUI view subtrees and distinguish view caching from element state, geometry caching, and virtualization. |

| [WebAssembly](docs/webassembly.md) | Build and run GPUI Kit applications in a browser with the repository's WebAssembly examples. |

| [WebView](docs/webview.md) | Embed a native Wry WebView in a GPUI Kit window, with the current platform and overlay limitations. |

| [Window](docs/window.md) | Use GPUI Window for window-local input, focus, rendering, and asynchronous work. |


## Styled components

| Page | Covers |
| --- | --- |

| [Accordion](component/accordion.md) | The accordion uses collapse internally to make it collapsible. |

| [Alert](component/alert.md) | Displays a callout for user attention. |

| [AlertDialog](component/alert-dialog.md) | A modal dialog that interrupts the user with important content and expects a response. |

| [Attachment](component/attachment.md) | A composable file and media attachment surface with lifecycle states, previews, and actions. |

| [Avatar](component/avatar.md) | Displays a user avatar image with fallback options. |

| [Badge](component/badge.md) | A red dot that indicates the number of unread messages, status, or other notifications. |

| [Bubble](component/bubble.md) | A composable chat surface for text, rich content, and reaction controls. |

| [Button](component/button.md) | Displays a button or a component that looks like a button. |

| [Calendar](component/calendar.md) | A flexible calendar component for displaying months, navigating dates, and selecting single dates or date ranges. |

| [Carousel](component/carousel.md) | A composable carousel for browsing related content. |

| [Chart](component/chart.md) | Beautiful charts and graphs for data visualization including line, bar, area, pie, radar, candlestick, and sankey charts. |

| [Checkbox](component/checkbox.md) | A control that allows the user to toggle between checked and not checked. |

| [Clipboard](component/clipboard.md) | A button component that helps you copy text or other content to your clipboard. |

| [Collapsible](component/collapsible.md) | An interactive element which expands/collapses. |

| [ColorPicker](component/color-picker.md) | A comprehensive color selection interface with support for multiple color formats, presets, and alpha channel. |

| [Combobox](component/combobox.md) | An autocomplete input paired with a searchable dropdown list. |

| [Command](component/command.md) | A command palette — a filtered list of commands and quick actions. |

| [Components](component.md) | Browse 75+ production-ready Rust UI components and primitives for forms, navigation, data, feedback, editing, and application layouts. |

| [DataTable](component/data-table.md) | High-performance data table with virtual scrolling, sorting, filtering, and column management. |

| [DatePicker](component/date-picker.md) | A date picker component for selecting single dates or date ranges with calendar interface. |

| [DescriptionList](component/description-list.md) | Use to display details with a tidy layout for key-value pairs. |

| [Dialog](component/dialog.md) | A dialog dialog for displaying content in a layer above the app. |

| [Dock](component/dock.md) | Production-ready dock layouts with styled tabs, split panes, edge docks, and persistent state. |

| [DropdownButton](component/dropdown_button.md) | A DropdownButton is a combination of a button and a trigger button. It allows us to display a dropdown menu when the trigger is clicked, but the left Button can still respond to independent events. |

| [Editor](component/editor.md) | Source-code editor with syntax highlighting, gutter, folding, and decorations. |

| [Empty](component/empty.md) | Composable empty states with media, text, actions, and custom content. |

| [Focus Trap](component/focus-trap.md) | A utility element that traps keyboard focus within a container, preventing Tab navigation from escaping. |

| [Form](component/form.md) | Flexible form container with support for field layout, validation, and multi-column layouts. |

| [GroupBox](component/group-box.md) | A styled container element with an optional title to group related content together. |

| [HoverCard](component/hover-card.md) | A floating overlay that displays rich content when hovering over a trigger element. |

| [Icon](component/icon.md) | Display SVG icons with various sizes, colors, and transformations. |

| [Image](component/image.md) | Display embedded, local, and remote images with sizing, loading, and error states. |

| [Input](component/input.md) | Text input component with validation, masking, and various features. |

| [Input Group](component/input-group.md) | Combine inputs and textareas with text, icons, buttons, and toolbars. |

| [Kbd](component/kbd.md) | Displays keyboard shortcuts with platform-specific formatting. |

| [Label](component/label.md) | Text labels for form elements with highlighting and styling options. |

| [List](component/list.md) | A flexible list component that displays a series of items with support for sections, search, selection, and infinite scrolling. |

| [Marker](component/marker.md) | A compact composable row for conversation status, notifications, loading, and separators. |

| [Menu](component/menu.md) | Context menus and popup menus with support for icons, shortcuts, submenus, and various menu item types. |

| [Message](component/message.md) | Compose sender identity, metadata, rich content, and actions into an aligned chat message. |

| [MessageScroller](component/message-scroller.md) | A virtualized message list with tail following, history insertion, unread navigation, and customizable jump controls. |

| [Notification](component/notification.md) | Display toast notifications that appear at the top right of the window with auto-dismiss functionality. |

| [NumberInput](component/number-input.md) | Number input component with increment/decrement controls and numeric formatting. |

| [OtpInput](component/otp-input.md) | One-time password input component with multiple fields, auto-focus, and paste handling. |

| [Pagination](component/pagination.md) | Pagination with page navigation, next and previous links. |

| [Plot](component/plot.md) | A low-level plotting library for creating custom charts and data visualizations. |

| [Popover](component/popover.md) | A floating overlay that displays rich content relative to a trigger element. |

| [Progress](component/progress.md) | Displays an indicator showing the completion progress of a task, typically displayed as a progress bar or circular indicator. |

| [Questionnaire](component/questionnaire.md) | A composable multi-step questionnaire with choice, freeform, validation, and navigation support. |

| [Radio](component/radio.md) | A set of checkable buttons—known as radio buttons—where no more than one of the buttons can be checked at a time. |

| [Rating](component/rating.md) | A simple interactive star rating component. |

| [Resizable](component/resizable.md) | A flexible panel layout system with draggable resize handles and adjustable panels. |

| [Root View](component/root.md) | Use the Root view to enable themes, notifications, dialogs, and other GPUI Component features in a window. |

| [Scrollable](component/scrollable.md) | Scrollable container with custom scrollbars, scroll tracking, and virtualization support. |

| [Select](component/select.md) | Displays a list of options for the user to pick from—triggered by a button. |

| [Settings](component/settings.md) | A settings UI with grouped setting items and pages. |

| [Sheet](component/sheet.md) | A sliding panel that appears from the edges of the screen for displaying content. |

| [Shimmer](component/shimmer.md) | Theme-aware loading text with configurable sweep timing, spread, direction, and reduced-motion behavior. |

| [Sidebar](component/sidebar.md) | A composable, themeable and customizable sidebar component for navigation and content organization. |

| [Skeleton](component/skeleton.md) | Use to show a placeholder while content is loading. |

| [Slider](component/slider.md) | A control that allows the user to select values from a range using a draggable thumb. |

| [Spinner](component/spinner.md) | Displays an animated loading showing the completion progress of a task. |

| [StatusBar](component/status-bar.md) | A horizontal status bar with left, center, and right regions, usually placed at the bottom of a window or pane. |

| [Stepper](component/stepper.md) | A step-by-step progress for users to navigate through a series of steps or stages. |

| [Switch](component/switch.md) | A control that allows the user to toggle between checked and not checked. |

| [Table](component/table.md) | A basic table component for directly rendering tabular data. |

| [Tabs](component/tabs.md) | A set of layered sections of content—known as tab panels—that are displayed one at a time. |

| [Tag](component/tag.md) | A short item that can be used to categorize or label content. |

| [Textarea](component/textarea.md) | Multi-line text input with fixed rows, soft wrapping, and auto-grow. |

| [TextView](component/text-view.md) | Renders Markdown and HTML text with optional custom Markdown plugins. |

| [Theme](component/theme.md) | Customize colors, typography, radii, and light or dark appearance with the GPUI Component theme system. |

| [TimeField](component/time-field.md) | A segmented input for a time of day, on a 24-hour or 12-hour clock. |

| [TitleBar](component/title-bar.md) | A custom window title bar component with window controls and custom content support. |

| [Toggle](component/toggle.md) | A button-style toggle component for binary on/off or selected states. |

| [Toolbar](component/toolbar.md) | A transparent, sizable container for commands in headers, tab panels, and custom surfaces. |

| [Tooltip](component/tooltip.md) | Display helpful information on hover or focus, with support for keyboard shortcuts and custom content. |

| [Tree](component/tree.md) | A hierarchical tree view component for displaying and navigating tree-structured data. |

| [VirtualList](component/virtual-list.md) | High-performance virtualized list component for rendering large datasets with variable item sizes. |


## Base behavior and primitives

| Page | Covers |
| --- | --- |

| [Accordion](base/primitives/accordion.md) | A disclosure group composed from independently styleable header, trigger, and panel parts. |

| [Alert Dialog](base/primitives/alert-dialog.md) | A modal confirmation surface for actions that need an explicit decision. |

| [Avatar](base/primitives/avatar.md) | An image with composable fallback content for a person or entity. |

| [Button](base/primitives/button.md) | An unstyled, accessible pressable with semantic state and keyboard activation. |

| [Calendar](base/primitives/calendar.md) | A state-driven date grid with selection matchers and custom item rendering. |

| [Checkbox](base/primitives/checkbox.md) | A controlled tri-state check control with a separately styled indicator. |

| [Collapsible](base/primitives/collapsible.md) | A composable region that shows or hides content without prescribing its trigger styling. |

| [Color Picker](base/primitives/color-picker.md) | State and interaction foundations for selecting colors in a custom picker UI. |

| [Combobox](base/primitives/combobox.md) | A text input paired with keyboard-navigable suggestions and selection behavior. |

| [Date Picker](base/primitives/date-picker.md) | A focus-aware date input that composes calendar behavior with a popup. |

| [Dialog](base/primitives/dialog.md) | A composable modal surface with focus management, backdrop, title, and close parts. |

| [Dock](base/dock.md) | A dockable workspace — splits, tab groups, and edge docks — whose layout is pure data and whose appearance is entirely yours. |

| [Editor](base/primitives/editor.md) | An unstyled source-code editor with language, gutter, folding, and decoration support. |

| [Getting Started](base/getting-started.md) | Install, initialize, and render your first gpui-base control. |

| [GPUI Base](base.md) | The unstyled behavior and infrastructure foundation of GPUI Kit, the Rust desktop framework. |

| [History](base/history.md) | Browser-style navigation trails and grouped undo/redo transactions for application state. |

| [Hover Card](base/primitives/hover-card.md) | A delayed floating card associated with a pointer or keyboard trigger. |

| [Input](base/primitives/input.md) | An unstyled single-line text input with masking, validation, and number stepping. |

| [Link](base/primitives/link.md) | An accessible link-like control with application-defined styling. |

| [Motion](base/motion.md) | Typed transitions, springs, keyframes, presence, stagger, and reduced-motion behavior in gpui-base. |

| [Nav Stack](base/primitives/nav-stack.md) | A navigation stack of views with push, pop, forward, and replace, and an animatable transition lifecycle. |

| [Number Input](base/primitives/number-input.md) | A numeric input with reusable increment, decrement, and step behavior. |

| [OTP Input](base/primitives/otp-input.md) | A multi-cell one-time-code input driven by a shared text state. |

| [Pagination](base/primitives/pagination.md) | A controlled page navigator with explicit current and total page state. |

| [Plot](base/plot.md) | Unstyled plotting in gpui-base — scales, shapes, axes, the Plot element, and hover tracking — for building charts in any design system. |

| [Popover](base/primitives/popover.md) | An anchored floating surface with controlled or internally managed open state. |

| [Popup](base/primitives/popup.md) | A low-level trigger and anchored floating-content host. |

| [Primitives](base/primitives.md) | The complete catalog of user-facing gpui-base primitives. |

| [Progress](base/primitives/progress.md) | Composable track and indicator parts for reporting task completion. |

| [Radio](base/primitives/radio.md) | A controlled single-choice item with selectable and disabled semantics. |

| [Radio Group](base/primitives/radio-group.md) | Groups radio items and provides keyboard navigation for a single selection. |

| [Resizable](base/primitives/resizable.md) | Panel groups and resize handles for user-adjustable split layouts. |

| [Scrollbar](base/primitives/scrollbar.md) | Add a styled, animated scrollbar to GPUI scroll views, lists, and custom viewports. |

| [Select](base/primitives/select.md) | A button-like selection control backed by an anchored, keyboard-navigable popup. |

| [Sheet](base/primitives/sheet.md) | A modal surface that enters from an edge while managing dismissal and focus. |

| [Slider](base/primitives/slider.md) | A state-driven range input with independently styleable track, indicator, and thumb. |

| [Switch](base/primitives/switch.md) | A controlled on/off control with separately styleable track and thumb. |

| [Table](base/primitives/table.md) | Semantic table primitives for composing headers, bodies, rows, and cells. |

| [Tabs](base/primitives/tabs.md) | A tab list and accessible tab controls with controlled selection. |

| [Text Selection](base/text-selection.md) | Add native window-level text selection to plain text and custom GPUI participants. |

| [Textarea](base/primitives/textarea.md) | An unstyled multi-line text field with fixed rows or auto-grow behavior. |

| [TextView](base/text-view.md) | Render selectable Markdown and HTML directly with gpui-base. |

| [Time Field](base/primitives/time-field.md) | A segmented time-of-day editor with a complete keyboard model and 24- or 12-hour clocks. |

| [Toast](base/primitives/toast.md) | A managed, animated stack of temporary status messages. |

| [Toggle](base/primitives/toggle.md) | A controlled two-state pressable for persistent choices such as formatting. |

| [Toggle Group](base/primitives/toggle-group.md) | Coordinates a set of toggle controls as a single- or multiple-selection group. |

| [Tooltip](base/primitives/tooltip.md) | A delayed, positioned description associated with a trigger element. |

| [Tree](base/primitives/tree.md) | A virtualized hierarchical list with explicit expansion and selection state. |

| [VirtualList](base/virtual-list.md) | Render a hundred thousand differently sized rows by drawing only the ones on screen. |


## Shell and extensions

| Page | Covers |
| --- | --- |

| [API Reference](shell/api.md) | Every name a script can import or reach — the four built-in modules, the cx and window globals, and the element methods that are not styles. |

| [Capabilities](shell/capabilities.md) | The default-deny model, the fs / storage / clipboard / process surface, where storage lives, and what the sandbox withholds. |

| [Dependencies](shell/dependencies.md) | Shell packages — what makes a Git repository one, and how a manifest names, selects, fetches and imports it, down to what an editor sees. |

| [Dock and Panels](shell/dock.md) | A dockable layout drawn entirely by script — panels that survive a restart, chrome you draw yourself, and commands instead of callbacks. |

| [Elements](shell/elements.md) | Constructors, composition with child / children / when, and why an element description can only be used once. |

| [Examples](shell/examples.md) | Complete standalone and embedded applications, including retained state, HostModule registrations, and native motion. |

| [Getting Started](shell/getting-started.md) | Add the runtime to a Rust application, write the script it loads, and check that script without opening a window. |

| [GPUI Shell](shell.md) | Makes a Rust GPUI application extensible in JavaScript, rendered by GPUI itself — no WebView, no DOM. Plugins first, standalone script applications second. |

| [Hosting](shell/hosting.md) | The Rust side in full — runtime lifetime, mounting script Views, refreshing them from host state, metrics, exit requests and hot-reload. |

| [HostModule](shell/host-module.md) | How a host lends its own Rust to a script — registration, the import that reaches it, the plain-data boundary, and the rules a Host function runs under. |

| [Overlays](shell/overlays.md) | Dialogs, the sheet and toasts, their stacking and dismissal order, and why they may only be opened from an event. |

| [Performance](shell/performance.md) | What a script costs once frame rate stops being the variable — invalidation against description size, the View as the boundary that bounds both, and the two failures FPS cannot tell apart. |

| [State and Views](shell/state.md) | Views, init and render, cx.notify(), retained input state, and asynchronous work. |

| [Styling](shell/styling.md) | The fluent style surface, length and colour grammars, semantic theme tokens, and hover / active / focus styles. |

| [The Engine Seam](shell/engine.md) | QuickJS behind one internal interface, why the seam exists, and the three measurements that tell script cost apart from frame cost. |
