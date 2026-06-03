# aidentity — single_agent example

Full identity structure for a single AI agent: iframe + pframes + somatic codebook.

## Quickstart

1. Copy `identity/` into your project
2. Validate: `aidentity validate ./identity/`
3. Check status: `aidentity status ./identity/`
4. Preview boot: `aidentity boot --mode lite ./identity/`

## What's here

| File | Purpose |
|---|---|
| `identity/iframe_v001.yaml` | Full identity snapshot with residual, semantic, and episodic sections |
| `identity/session_001.yaml` | pframe — a single-session delta recording what changed |
| `identity/somatic_codebook.yaml` | 4-dimension codebook for functional state tracking |

## How it works

**iframe** is the stable baseline — updated every `gop_size` sessions (default: 24).
The `gop_counter` field tracks how many sessions since the last iframe.

**pframe** (session delta) records only what changed in a single session.
It references the iframe via `delta_from`. Keep pframes lightweight.

**somatic codebook** defines the dimensions for tracking functional state over time.
You don't need one to get started — add it when you want richer mood tracking.

## Validation

```bash
aidentity validate ./identity/
# ✓ iframe_v001.yaml
# ✓ session_001.yaml
# ✓ somatic_codebook.yaml
```

## Next step

For teams running multiple specialized agents, see `examples/multi_agent/`.
