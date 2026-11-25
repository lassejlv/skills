# Worked example: Tally

Tally is a task tracker for small agencies (5 to 30 people) running several client projects at once. Below, three surfaces taken through the skill, each with the **average** version a model produces by default beside the intent version.

## Account popover

**Average:** avatar, name, email, then Profile, Settings, Billing, Help, Log out.

```
Intent brief: account popover
Why:     about to go heads-down on client work, or leaving for the day
How:     set a status in one click; most often "Focusing"
Next:    straight back to their task list
Cut:     email (one account per person, login never in doubt), Billing (owners only, lives in Settings)
Assumed: people belong to more than one client workspace
```

**Intent version:**

- Name, with the current status under it: "Focusing until 14:00".
- Status: Available, Focusing, Away, each with duration presets (1 h, until 17:00, until tomorrow).
- Pause notifications: 1 h, until tomorrow.
- Workspaces: each client workspace with its unread count; one click switches.
- Settings and Log out at the bottom.

**Cut:** email (nobody wonders which account they are in), Billing (owners reach it from Settings), Help (lives in the `?` menu), Profile (merged into Settings).

## Onboarding

**Average:** four modal slides ("Welcome to Tally", "Create tasks", "Collaborate", "Track time") and a "Get started" button that lands on an empty dashboard.

```
Intent brief: first-run onboarding
Why:     just signed up to get one client project under control
How:     create that project and get the first tasks into it
Next:    invite the two or three people working on it
Cut:     feature tour, empty dashboard landing
Assumed: most sign-ups arrive with one specific project in mind
```

**Intent version:**

1. "What do you mainly run in Tally?" Client projects, internal sprints, or personal work. The answer sets the default statuses, fields and views (Tesler: the product infers what the user would otherwise configure).
2. "Name your first project." Pre-filled statuses for the chosen kind; the user types three starter tasks inline.
3. "Who works on it?" Up to three emails, skippable.
4. Lands inside the real project with their tasks in it. One quiet line: "You can change all of this in Settings."

## Task detail

**Average:** a task page with the project and assignee shown as plain text and avatars; to learn anything about them, go back to the sidebar and open the Projects or People page.

```
Intent brief: task detail
Why:     check what a task needs and who is on it, then act
How:     update status, reassign, set a due date
Next:    the project's deadline, or whether the assignee has room this week
Cut:     the trip back to the sidebar
Assumed: due dates are set many times a day
```

**Intent version:**

- The project name links to the project; hovering shows client, deadline, owner and progress.
- The assignee links to their profile; hovering shows their status ("Focusing until 14:00", the same status the popover sets) and their open tasks this week.
- The due date accepts typed input ("fri", "next week", "3/12") as well as the calendar.

## Position

Every task in Tally belongs to a client project: there is no orphan inbox. Agencies bill by client, so a task without a client is a task nobody can bill. Some users will want a personal inbox; Tally says no and gives each person a private project instead.
