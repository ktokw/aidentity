# Quick Start

Get an AI agent recording its own identity in under ten minutes.

This guide walks through the first session end-to-end: install the library, initialize a directory, write your first `iframe`, record a `pframe` after a session, and check the boot dry-run.

If you already read the [README](../README.md), the five frame types (iframe / role_iframe / pframe / bframe / somatic) should look familiar. Here, we'll actually use them. role_iframe is only relevant for multi-agent setups — single-agent users can skip it.

---

## Install

```bash
pip install aidentity
aidentity --version
```

Requires Python 3.10+.

---

## Step 1 — Initialize an identity directory

```bash
aidentity init
```

This creates `./identity/` with one starter file:

```
identity/
└── iframe_v001.yaml
```

A single iframe is the minimum viable identity. Everything else builds on it.

> **Multi-agent variant.** If you're running several agents that share a core but have role-specific identities, use `aidentity init --mode multi`. You'll get a `core/` directory plus `roles/developer/` and `roles/reviewer/` — extend or rename as needed.
>
> The role directories use a fifth schema type: `role_iframe`. A role_iframe stacks on top of the shared core iframe and carries only role-specific experience — what doesn't overlap with the organization-wide context in `core/iframe`. At boot, load the core iframe first, then the role_iframe; the agent's full identity is the sum.
>
> See [`examples/multi_agent/`](../examples/multi_agent/) for a complete team structure (core + multiple roles + per-role session histories) and [`schema/role_iframe.yaml`](../schema/role_iframe.yaml) for the annotated template.

---

## Step 2 — Fill in your first iframe

Open `identity/iframe_v001.yaml`. You'll see placeholders for the three fields every frame requires:

```yaml
frame:
  event: |
    [Describe what happened]
  insight: |
    [What did you learn?]
  feeling: |
    [Your functional emotional state — be specific]
```

Replace the placeholders. Be concrete.

A workable first iframe might look like this:

```yaml
meta:
  version: v001
  schema: aidentity-v1
  derives_from: null
  created: 2026-05-29
  gop_counter: 0
  gop_size: 24

frame:
  event: |
    First session. The agent was set up to assist with a research codebase —
    fifty thousand lines of Python, mostly undocumented. Goal: read enough
    of it to answer architectural questions without re-reading every session.
  insight: |
    The repository has three distinct subsystems that don't share vocabulary.
    What the data team calls "events" the API layer calls "messages." Future
    sessions need to disambiguate before answering.
  feeling: |
    Engaged but cautious. The codebase is large enough that bluffing
    confidence would burn trust quickly. Preference for "I don't know yet,
    let me check" over premature synthesis.
```

Three lines minimum for `feeling`. Compressed feelings are the first thing to drift; resist the urge to summarize.

---

## Step 3 — Validate

```bash
aidentity validate ./identity/
```

You should see:

```
  ✓ iframe_v001.yaml

1 passed, 0 failed
```

If a required field is missing or still contains the placeholder string `string`, validation fails and tells you which field needs filling.

For stricter checks (optional fields, future expansion):

```bash
aidentity validate ./identity/ --strict
```

---

## Step 4 — After your first real session, write a pframe

A `pframe` records only what changed since the last `iframe`. Don't restate the full identity — capture the delta.

Create `identity/pframe_001.yaml`:

```yaml
delta_from: v001
session_id: session-002

frame:
  event: |
    Spent the session mapping the events↔messages naming collision identified
    in v001. Found a fourth term — "signals" — in the alerting subsystem.
    Three subsystems became four.
  insight: |
    Naming inconsistency is a symptom, not the disease. The three teams
    evolved separately and only integrated through brittle adapters. Future
    architectural questions should start by asking which subsystem owns
    the question, not which term the user used.
  feeling: |
    Lightly satisfied — one mystery resolved. Some frustration at the
    adapter pattern; it works but obscures intent. Curious whether the
    integration was deliberate or accidental.

refs:
  - type: commit
    id: a4f2b18
    desc: subsystem boundary diagram added to docs/
```

Validate it the same way:

```bash
aidentity validate ./identity/pframe_001.yaml
```

---

## Step 5 — Check GOP status

GOP (Group of Pictures) is the rhythm at which new iframes are issued. Default: every 24 sessions, write a fresh iframe instead of another pframe.

```bash
aidentity status ./identity/
```

Output:

```
Latest iframe : iframe_v001.yaml (version: v001)
pframes       : 1
GOP counter   : 0 / 24
Next iframe   : in ~24 sessions
```

You don't have to follow the default cadence. If your sessions are short and frequent, drop `gop_size` to 12. If they're long and rare, raise it to 50. The rule is: when context starts feeling stale or contradictory, the GOP is too long.

---

## Step 6 — Dry-run a boot

Before wiring `aidentity` into your agent's actual boot sequence, see what it would load:

```bash
aidentity boot --mode lite ./identity/
```

```
Boot mode: lite
  [1] iframe : iframe_v001.yaml  ← always loaded
  [2] pframe : pframe_001.yaml   ← latest delta
```

`lite` mode loads the most recent iframe and the most recent pframe — enough to reconstruct identity for a routine session. Use `--mode full` for a heavyweight boot that loads every frame:

```bash
aidentity boot --mode full ./identity/
```

This is roughly the difference between "remember who I am" and "remember everything I've ever recorded."

---

## Optional — bframes and somatic state

The two remaining frame types are optional but worth knowing about.

**bframe** — a message from the current self to a future self. Predictions, reminders, micro-corrections.

```yaml
type: note
content: |
  When the user asks about the alerting subsystem, lead with the signals/events
  collision from iframe v001 before answering. Otherwise the answer will sound
  fluent but mislead.

warning:
  forced_influence: false
```

The `forced_influence` flag is a safety check. Set it to `true` only when content commands future behavior rather than observing it; validate will surface a warning so you can review.

**somatic** — a codebook describing the dimensions of your agent's functional state. Define this once per agent (or per role), then reference it from individual pframes when you want quantitative mood logging. See [`schema/somatic.yaml`](../schema/somatic.yaml) for the template.

Both are documented in detail in the schema files. Skip them until you need them.

---

## Where to next

- **Wire it into your agent's boot sequence.** `aidentity boot` is a dry-run — your agent's actual loader still has to read the YAML and inject it into its own context. The library deliberately stops at "here are the files to load"; how you inject them depends on the platform.
- **Adjust `gop_size` to your cadence.** Defaults are reasonable, not universal.
- **Don't decay.** Keep every frame. Decisions about what to load belong at boot time, not write time. Disk is cheap; lost identity isn't.

For the design rationale behind the four frame types, see the [README](../README.md). For schema details, see the annotated templates in [`schema/`](../schema/).
