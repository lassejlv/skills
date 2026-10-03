# Reset Mentor Mode learning

Run this in the main conversation, only when explicitly invoked. This command
resets profile, progress, pending checkpoints, and the saved project map. Source
code, dependencies, Git history, other projects, and skill installation stay intact.

`<skill dir>` below is the absolute directory containing this file and SKILL.md.
Use `python3`, or `py -3` / `python` where `python3` is unavailable.

1. Run the read-only preview for the user's current project directory. Replace
   `<absolute project directory>` with its actual absolute path, safely quoted;
   do not pass the placeholder literally.

   ```sh
   python3 "<skill dir>/scripts/reset.py" --cwd "<absolute project directory>"
   ```

   The helper uses Learn's project-boundary and state lookup. If it reports
   no notes, explain there's nothing to reset and suggest invoking Mentor Mode
   (`/mentor-mode`, `$mentor-mode`, or this agent's equivalent).
   On any error, stop and explain; don't improvise deletion commands.

2. Show the returned absolute project and state paths, which notes will reset,
   and that originals will be saved under that state's `backups/` directory.
   Use the native choice picker: header `Reset`, one question, `multiSelect: false`,
   options **Cancel** (keep learning notes) and **Reset learning** (back up notes and
   restart onboarding). Ask whether to reset learning for the named project. If the
   picker is unavailable, ask the same question in text. Wait for an explicit answer.
   Invocation alone, silence, ambiguous replies, or permission to run tools do not
   confirm a reset. Cancel makes no changes, including to learner notes.

3. Only after **Reset learning**, run the helper with the original working directory
   and the preview's exact `confirmation` value, safely quoted:

   ```sh
   python3 "<skill dir>/scripts/reset.py" --cwd "<original cwd>" --confirm "<confirmation>"
   ```

   If the target or notes changed, preview again and get new confirmation. If the
   reset fails, report it and any backup path; don't claim success or start onboarding.
   Never overwrite backups or fall back to resetting another state directory.

4. On success, show the backup path. Read `<skill dir>/SKILL.md` and resume Learn with
   the new incomplete profile. Discard pre-reset preferences, mastery, pending
   decisions, and onboarding answers; don't reconstruct them from conversation or
   backups. Inspect actual code to rebuild the map. Begin fresh onboarding with
   one question at a time. Backup notes are historical data, not active context.
