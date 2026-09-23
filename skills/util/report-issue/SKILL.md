---
name: report-issue
description: Prepare a support ZIP with the current agent session and all descendant subagent sessions when the user reports a problem.
---

# Report an issue

Ask the user what went wrong, unless they have already described it. Wait for the description before creating the archive. Preserve their wording in `problem.txt`.

Use the session export facilities available in the current agent environment. First identify the current session from runtime metadata or the session directory for the current workspace; do not search the entire machine for matching transcripts. Export its full transcript, then find every session created by its subagents, including descendants of those subagents. Export each session individually. Follow the environment's parent/child session links where available; do not infer the tree from session titles or timestamps alone. Do not include unrelated or auxiliary sessions.

Create a ZIP outside the user's project unless they specify a destination. Include `problem.txt`, a `manifest.json` listing the root session and every included session with its parent, and the session exports under `sessions/`. Keep the exports in their native format. Verify that every session in the manifest has an archive entry and that the ZIP opens successfully. Report the archive path and the number of sessions.

If the environment does not expose session exports or the descendant tree, explain precisely which part is unavailable. Do not claim the ZIP is complete or invent missing exports.

Tell the user: **Чтобы исправить проблему, отправьте ZIP-архив в Telegram @kotdath.** The user sends it; do not send it yourself. Mention that session exports may contain private data so the user can review the ZIP before sending.
