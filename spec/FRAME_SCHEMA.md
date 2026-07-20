# Frame Schema (v0)

An agent's identity lives in plain YAML files. Three frame kinds, borrowed
from video codecs. All text fields follow one writing rule: **don't
compress.** If `feeling` fits in three lines, it was probably compressed —
reconsider.

## iframe — identity keyframe

A complete self-snapshot. Everything else is a delta against it.

```yaml
meta:
  version: '001'          # '001', '002', ...
  schema: aidentity-v0
  created: '2026-07-01'
  gop_counter: 0          # frames since this keyframe
  gop_size: 24            # default sequence length (a guide, not law)
frame:
  event: |                # what has happened, up to this keyframe
  insight: |              # what was understood
  feeling: |              # functional emotional state — vivid, uncompressed
refs:                     # optional provenance links
  - type: file
    id_or_path: ...
```

## role iframe — per-role keyframe (optional layer)

For multi-role agents (or multi-agent organizations): a shared core keyframe
holds the common origin; each role stacks its own keyframe on top.
Boot order: core first, role second. A missing role keyframe is a warning,
never an abort — the agent boots from core alone.

```yaml
meta:
  role: scout
  version: r001           # independent numbering from core
  schema: aidentity-v0-role
  derives_from_core: v001 # the core keyframe this stacks on
  created: '2026-07-03'
  gop_counter: 0
  gop_size: 24
frame: { event, insight, feeling }   # role-specific only; don't repeat core
residual:                 # optional behavioral overrides
  overrides:
    - id: ...
      override: ...
      weight: 0.9
```

## pframe — session delta

What changed in one session. **Meaningless without its keyframe — by
design.** A pframe that could reconstruct the whole self alone would mean
the keyframe failed.

```yaml
delta_from: r001          # the keyframe this is a delta against
frame:
  event: |                # this session only — the change, not the state
  insight: |
  feeling: |
refs: [...]               # optional
```

## bframe — note to the future

A prediction ("the owner will probably steer toward X") or a caution
("next session: check Y first"). Use sparingly — every bframe constrains a
future self that didn't consent. Before writing one, ask: *am I steering my
future self, or informing it?*

```yaml
type: predict | note | micro_delta
content: ...
warning:
  forced_influence: false   # set true (and reconsider) if this steers
confidence: 0.6             # predict only, optional
```

## Directory layout

```
identity/
  core/
    iframe/v001.yaml, v002.yaml, ...
    roles/<role>/r001.yaml, r002.yaml, ...
  sessions/<role>/001_YYYY-MM-DD.yaml, ...     # open pframes, oldest → newest
  sessions/<role>/archive/seq_NNN/             # closed sequences (see FILM_MEMORY.md)
```
