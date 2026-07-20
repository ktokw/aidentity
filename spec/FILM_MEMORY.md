# Film Memory — recursive sequence compression

*"A film isn't rewatched in full. You watch the cut. A two-hour film
compresses to thirty minutes — and the reel stays in the vault."*

Long-lived agents face a memory problem that stores-and-retrieval alone
doesn't solve: history grows without bound, old and new memories compete at
retrieval time, and naive summarization destroys the vivid originals that
made the history worth keeping. Film memory is one answer:

```
Comp(N(gop) × seq) = seq′        (functions capitalized, variables lowercase)
```

## Structure: homogeneous nesting

- ~**24 frames** (`i p p … p b`) close into one **sequence**.
- ~**24 sequences** gather into one higher-level sequence. Recursively.
- A sequence is never *transformed into* anything — sequences nest, like
  reels contain scenes contain shots contain frames. What the level above
  sees is the sequence's **summary view**, a face attached to the package,
  not a replacement for it.
- **Closing a sequence never creates or updates a keyframe.** Identity
  (iframes) and memory (the frame hierarchy) are separate streams on
  separate cadences: keyframes update on scene changes — mission shifts,
  role changes; memory compresses on the mechanical 24/24 rhythm.

## Variable retention (VBR)

24/24 is structure. *Representation weight* follows meaning:

- A meaningless sequence is **skipped**: its summary view is a stub —
  period, one line, pointer. The stub is mandatory (it keeps the drill-down
  chain intact); skipping is a viewing decision, not an existence denial.
- A dense sequence is **preserved heavily**: its view carries many frames'
  worth of detail, and its high-intensity frames are promoted — they
  survive across levels, the way a film's defining scenes survive every
  recut.
- The editing judgment belongs to the agent that lived the sequence.
  Audits verify chain integrity, not taste.

Seen from above, history is not a uniform miniature — it is a terrain map
of meaning: a few vivid episodes, and months that collapsed to a line.
Like human years.

## Recall: two paths down

1. **Hierarchical descent** — top-level view → child sequence → original
   frames. Requires an unbroken pointer chain: every view lists its
   children. One broken link orphans everything below it.
2. **Associative jump** — every view carries **cues** (keywords, names,
   emotion markers) beyond its summary text, and an index over the archive
   can hit originals directly. Events the summary doesn't mention must
   still be findable.

**Recall drills are part of the spec**: periodically pick past events at
random and verify descent reaches the original frame's vivid `feeling`.
Chain rot is silent; drills make it loud.

## Adaptive parameters

- `gop ≈ 24`, `n ≈ 24` are **defaults, not constants**. Scene cuts close
  sequences early; quiet stretches stretch them. Meaning boundaries beat
  numbers.
- Compression is a storage rule, not a playback quality. As available
  context grows, default playback descends a level deeper. Don't bake
  today's constraints into the archive.

## Threat note

Identity files are an attack surface: memory poisoning and provenance
tampering are real classes of attack against agent memory. The pointer
chain + never-delete rule give you an audit trail; pair them with
version control and provenance guards on the identity directory.
