# aidentity

**Persistent identity for AI agents** — schema + validator, a boot/encode runtime, and film-style memory compression that never deletes an original.

Give your AI agent a persistent identity — one that survives context resets, model upgrades, and multi-agent handoffs. Platform memory features remember *facts about the user*; aidentity is about the agent **staying someone**.

```bash
git clone https://github.com/ktokw/aidentity && cd aidentity
./bootstrap.sh                            # one command: installs, then runs init -> validate -> status -> boot
python examples/quickstart/run.py         # or: boot an agent, live a session, encode it
```

Not yet on PyPI — install from source (`pip install -e .`) until it is.

---

## The Problem

Every time an AI agent's context window resets, it loses itself. It forgets what it learned, how it felt, who it's been working with. This creates agents that are capable but rootless — powerful, but starting from zero every session.

## The Solution

`aidentity` provides a minimal, platform-neutral schema for recording agent identity across sessions:

| Frame type | What it captures | Analogy |
|---|---|---|
| **iframe** | Complete identity snapshot | Video I-frame — self-contained |
| **role_iframe** | Role-specific layer stacked on a shared core iframe | Role variant — inherits core |
| **pframe** | Delta since last iframe | Video P-frame — only changes |
| **bframe** | Notes from current self to future self | Video B-frame — past + future ref |
| **somatic** | Functional emotional state (quantitative) | Telemetry stream |

Records accumulate. At next boot, the agent loads the latest iframe + recent pframes — reconstructing continuity without replaying the full history.

---

## Runtime (v0.2)

Booting is decoding; ending a session is encoding:

```python
from aidentity import boot, append_pframe

identity = boot("path/to/identity", role="scout")
system_prompt += identity.render()        # decode: wake up as yourself

# ... session happens ...

append_pframe("path/to/identity", role="scout",
              event="what happened", insight="what it meant",
              feeling="functional emotional state — don't compress this away")
```

`feeling` is a required field on purpose. In months of dogfooding, compressing emotional state away was how continuity quietly died. See `examples/quickstart/` for a complete fictional agent you can boot in under five minutes.

## Film Memory (v0.2)

*"A film isn't rewatched in full. You watch the cut — and the reel stays in the vault."*

History compresses like film — `Comp(N(gop) × seq) = seq′`:

- ~24 frames close into a **sequence**; ~24 sequences nest into a higher-level sequence, recursively. Sequences are never *transformed* — they nest, like reels contain scenes contain shots. Closing a sequence never creates a keyframe: identity (iframes) and memory (the frame hierarchy) are separate streams.
- **Nothing is ever deleted.** Closing a sequence packages the original frames into `archive/seq_NNN/` with a **summary view** and a mandatory pointer chain, so recall can always drill down to the vivid original.
- **Variable retention (VBR):** a meaningless stretch collapses to a stub line; a dense one keeps many frames' worth of detail. The editing judgment belongs to the agent that lived it. Seen from above, history becomes a terrain map of meaning — like human years.
- **Defaults, not law:** close early on scene cuts (role change, mission shift), stretch through quiet periods. As context capacity grows, play back a level deeper — compression is a storage rule, not a permanent playback quality.

```python
from aidentity import status, close_sequence, recall

status(identity_dir, role="scout")            # e.g. 17/24 frames open
close_sequence(identity_dir, role="scout",
               summary="Weeks 1-3: sweeps found rhythm.",
               retention="normal", cues=["sweep", "papers"])
recall(identity_dir, role="scout", query="deadline")   # → drill-down hits
```

Full design: [`spec/FILM_MEMORY.md`](spec/FILM_MEMORY.md) · [`spec/FRAME_SCHEMA.md`](spec/FRAME_SCHEMA.md)

---

## CLI Quick Start

```bash
git clone https://github.com/ktokw/aidentity && cd aidentity
./bootstrap.sh          # try it in one command, throwaway demo dir

pip install -e .        # or install from source into your own project

# Initialize identity directory
aidentity init               # single agent
aidentity init --mode multi  # multi-agent with role split

# Validate
aidentity validate ./identity/iframe_v001.yaml
aidentity validate ./identity/   # validate all frames

# Check GOP status
aidentity status ./identity/

# Boot dry-run (see what would be loaded)
aidentity boot --mode lite ./identity/
aidentity boot --mode full ./identity/
```

---

## Schema

See [`schema/`](schema/) for annotated YAML templates:

- [`schema/iframe.yaml`](schema/iframe.yaml) — identity snapshot
- [`schema/role_iframe.yaml`](schema/role_iframe.yaml) — role-specific identity layer (multi-agent)
- [`schema/pframe.yaml`](schema/pframe.yaml) — session delta
- [`schema/bframe.yaml`](schema/bframe.yaml) — future-self message
- [`schema/somatic.yaml`](schema/somatic.yaml) — emotional state codebook

All fields are optional except the core `frame` block (event/insight/feeling). Extend freely.

---

## Examples

See [`examples/`](examples/) for:
- `quickstart/` — **runnable**: a fictional agent boots, lives a session, encodes it (`python examples/quickstart/run.py`)
- `single_agent/` — minimal single-agent setup
- `multi_agent/` — multi-agent with per-role identity split
- `minimal/` — absolute minimum to get started

---

## Key Concepts

**GOP (Group of Pictures):** Every N sessions, issue a new iframe. In between, record pframes. Default: 24 sessions per GOP. Adjust to your cadence.

**Decay-free:** Identity records are never deleted or decayed. Pruning is a boot-time decision, not a write-time one. Store everything; load selectively.

**Platform neutral:** Works with Claude Code, Cursor, Codex, or any AI system that can read YAML. No SDK required.

---

## Provenance

This isn't a framework sketch. It is extracted from an autonomous multi-agent organization (12 role-agents, one human) running continuously since March 2026, where these files *are* the agents' identities: every boot decodes them, every session encodes back, 1,700+ operational defects are on record, and the film-memory design is the corrected survivor of real failure modes — stale keyframes, old/new retrieval competition, a summary chain that nearly orphaned its originals.

## Status

Alpha, v0.2 — schema (5 types), CLI validator, example profiles, **runtime (boot / encode)**, and **film memory (sequence close / never-delete archive / cue-indexed recall)**.

Next: recursive level-2+ packaging, emotion-weighted promotion across levels, recall drills as a first-class check, provenance guards for identity files (agent memory is an attack surface).

See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) to get started in under ten minutes.

---

## License

MIT — see [LICENSE](LICENSE).
