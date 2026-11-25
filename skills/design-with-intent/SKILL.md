---
name: design-with-intent
description: Design screens, flows and components from purpose instead of copied patterns, so the result serves this product's users rather than the average of every app. Use when designing or reviewing a screen, flow, popover, menu, form, onboarding or navigation structure, when deciding what a UI element should contain, or when a generated UI feels generic, safe or "vibe coded" even though nothing looks broken.
---

# Design with intent

Left alone, a model designs the **average**: the most common shape of a dropdown, a popover, an onboarding flow, a sidebar app. The average copies the *form* of a pattern and drops its *purpose*, so the result looks competent and serves nobody in particular. Every pattern began as someone's answer to a specific problem; reuse the answer only where the problem exists. (Office cubicles lost their angled, comfortable walls once companies squared them to fit more desks: the parts survived, the reason did not.)

This skill works on **structure and behaviour**: what is on the screen, what it does, where it leads. For visual polish use `unslop`; for aesthetic direction use `frontend-design`.

When designing a screen or flow from scratch, read [references/example.md](references/example.md) first: one product taken through every step, with the average version beside the result.

## 1. Write the intent brief

Before building, show the user one **intent brief per screen or flow**, in your reply (or the PR description when there is no conversation). Each surface serves a different moment, so one brief shared across several surfaces fails:

```
Intent brief: <screen or flow>
Why:     the moment and goal that make someone open it
How:     the first action, and the most frequent one
Next:    what they reach for right after
Cut:     what the average version includes that this user does not need
Assumed: any answer above the brief did not give you
```

Fill all five lines. Every line must be specific enough to read wrong on a different product: "manage their account" fails, "go heads-down for client work and silence pings" passes. Fill `Assumed` instead of leaving a line vague; a vague line is where the average leaks in. Then build on the brief without waiting, unless an assumption would change the whole structure, in which case ask first.

## 2. Interrogate every element

For each component, field, label, icon and section you place, name the job it does **here**. Keep it only when the job is real in this product; otherwise cut it or replace it with something that serves `How` or `Next`.

- **Dropdown arrow.** The chevron points down because menus usually open downward. A menu that opens upward, near the bottom of the screen, gets an arrow pointing up. The arrow signals where the menu goes, not what dropdowns look like.
- **Account popover.** Notion shows the email at the top because people run several accounts and need to know which is active. In an app where the login is never in doubt, the email is noise. Fill the popover with what this user actually does there: in a task tracker, set away status, pause notifications, switch workspace.
- **Context.** The same component holds different things in a coding tool, an interior-design tool and a finance app. Derive the contents from the brief, never from the template.

Done when every element on the screen has a named, product-specific job, and your reply lists what you cut or replaced, each with its one-line reason.

## 3. Check the recurring traps

Generated apps fail in these four places most often. Check every one against the design.

Done when your reply has one line per trap saying what the design does about it, or why it does not apply here.

### Complexity goes to the builder (Tesler's law)

Complexity is never removed, only moved. Whoever absorbs it, builder or user, is a choice. The old date picker of three dropdowns (month, day, year) was easy to build and slow to use; the modern picker with a calendar plus typed input is harder to build and easy to use. Take the harder build whenever it saves the user effort on a frequent task: parse free text, infer defaults, accept several input styles.

### Onboarding builds, not explains

A carousel of modal slides describing features is the default, and Nielsen Norman Group found users who saw modal onboarding succeed at about the same rate as those who skipped it. Onboarding that works shapes the product around the user:

- Ask what they are here to do, and configure the product from the answer (Notion and Canva both start this way).
- Walk them through one meaningful first action, such as creating their first real project.
- Make it clear every choice can be changed later.

### Navigation follows the data

The default app is isolated pages joined by a sidebar, so checking who owns a task's project means three page loads. Model navigation on Wikipedia instead: every entity mentioned (task, project, person, customer) links to itself inline, and hovering shows a preview of its core facts without leaving the page. The user moves along relationships, not back through the sidebar.

### Take a position

The brief produces opinions; ship them. A design that tries to suit everyone defaults back to the average. Apple's Magic Mouse put form over function with its charging port underneath: polarising, and unmistakably deliberate. Prefer a clear choice you can defend from the brief over a safe one nobody chose, and name the position in your reply.

## Reviewing an existing design

Write the intent brief for what the design should serve, then run steps 2 and 3 against what exists. For each finding, report the element, the job it is missing or the trap it falls into, and the purposeful replacement. Lead with structural findings (no clear purpose, wrong navigation model, onboarding that explains) before element-level ones.
