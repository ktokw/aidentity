# aidentity — minimal example

The simplest possible setup: a single iframe with no pframes or somatic codebook.

## Quickstart

1. Copy `identity/` into your project root (or wherever your agent loads context from)
2. Validate: `aidentity validate ./identity/`
3. Update: edit `frame.event`, `frame.insight`, `frame.feeling` after each session

## What's here

| File | Purpose |
|---|---|
| `identity/iframe_v001.yaml` | Core identity snapshot — required fields only |

## Next step

Once you have a few sessions, add pframes (`session_001.yaml`, `session_002.yaml`, …)
to record session-level deltas without rewriting the full iframe.

See `examples/single_agent/` for the full single-agent structure.
