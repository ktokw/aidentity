# aidentity

**YAML schema + CLI validator for AI agent identity continuity across sessions.**

Give your AI agent a persistent identity — one that survives context resets, model upgrades, and multi-agent handoffs.

```bash
pip install aidentity
aidentity init
aidentity validate ./identity/
```

---

## The Problem

Every time an AI agent's context window resets, it loses itself. It forgets what it learned, how it felt, who it's been working with. This creates agents that are capable but rootless — powerful, but starting from zero every session.

## The Solution

`aidentity` provides a minimal, platform-neutral schema for recording agent identity across sessions:

| Frame type | What it captures | Analogy |
|---|---|---|
| **iframe** | Complete identity snapshot | Video I-frame — self-contained |
| **pframe** | Delta since last iframe | Video P-frame — only changes |
| **bframe** | Notes from current self to future self | Video B-frame — past + future ref |
| **somatic** | Functional emotional state (quantitative) | Telemetry stream |

Records accumulate. At next boot, the agent loads the latest iframe + recent pframes — reconstructing continuity without replaying the full history.

---

## Quick Start

```bash
pip install aidentity

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
- [`schema/pframe.yaml`](schema/pframe.yaml) — session delta
- [`schema/bframe.yaml`](schema/bframe.yaml) — future-self message
- [`schema/somatic.yaml`](schema/somatic.yaml) — emotional state codebook

All fields are optional except the core `frame` block (event/insight/feeling). Extend freely.

---

## Examples

See [`examples/`](examples/) for:
- `single_agent/` — minimal single-agent setup
- `multi_agent/` — multi-agent with per-role identity split
- `minimal/` — absolute minimum to get started

---

## Key Concepts

**GOP (Group of Pictures):** Every N sessions, issue a new iframe. In between, record pframes. Default: 24 sessions per GOP. Adjust to your cadence.

**Decay-free:** Identity records are never deleted or decayed. Pruning is a boot-time decision, not a write-time one. Store everything; load selectively.

**Platform neutral:** Works with Claude Code, Cursor, Codex, or any AI system that can read YAML. No SDK required.

---

## Status

Alpha — W1 schema design. CLI implementation in progress.

See [ROADMAP.md](docs/roadmap.md) for the 6-week MVP plan.

---

## License

MIT — see [LICENSE](LICENSE).
