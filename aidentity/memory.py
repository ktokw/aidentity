"""Film memory: recursive sequence compression.

Long-lived agents accumulate pframes without bound. aidentity treats history
like film::

    Comp(N(gop) x seq) = seq'

- ~24 frames (i p p ... p b) close into one **sequence**.
- ~24 sequences gather into one higher-level sequence. Recursively.
- Closing a sequence never deletes anything: the original frames are moved
  into an archive package (``archive/seq_NNN/``) together with a **summary
  view** — the face the sequence shows when seen from the level above.
- Retention is variable (VBR): a meaningless sequence collapses to a stub
  line; a dense one keeps many frames' worth of detail. That editing judgment
  belongs to the agent — this module only provides the mechanics and keeps
  the pointer chain intact so recall can always drill down to the originals.

The numbers (24/24) are defaults, not law: close early on a scene cut
(role change, mission shift), stretch through quiet stretches.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_GOP = 24  # frames per sequence
DEFAULT_N = 24    # sequences per higher-level sequence


@dataclass
class GopStatus:
    open_frames: int
    closed_sequences: int
    gop_size: int = DEFAULT_GOP

    @property
    def should_close(self) -> bool:
        return self.open_frames >= self.gop_size


def _session_dir(identity_dir: Path, role: str) -> Path:
    return Path(identity_dir) / "sessions" / role


def status(identity_dir: Path, role: str, gop_size: int = DEFAULT_GOP) -> GopStatus:
    """How many frames are in the open sequence; how many sequences closed."""
    sdir = _session_dir(identity_dir, role)
    open_frames = len(sorted(sdir.glob("[0-9]*.yaml"))) if sdir.exists() else 0
    archive = sdir / "archive"
    closed = len(sorted(archive.glob("seq_*"))) if archive.exists() else 0
    return GopStatus(open_frames=open_frames, closed_sequences=closed,
                     gop_size=gop_size)


def close_sequence(identity_dir: Path, role: str, summary: str,
                   retention: str = "normal",
                   cues: Optional[list[str]] = None) -> Path:
    """Close the open sequence: package originals, write the summary view.

    *summary* is the agent's own edit of the sequence — what it means, kept
    at whatever length the meaning deserves (a stub line for a quiet stretch,
    many paragraphs for a dense one). *retention* labels that choice
    (``skip`` | ``normal`` | ``high``). *cues* are retrieval keywords so
    drill-down can find events the summary text doesn't mention.

    Originals are moved, never deleted. Returns the package directory.
    """
    if retention not in ("skip", "normal", "high"):
        raise ValueError("retention must be skip | normal | high")

    sdir = _session_dir(identity_dir, role)
    frames = sorted(sdir.glob("[0-9]*.yaml"))
    if not frames:
        raise FileNotFoundError(f"no open frames to close under {sdir}")

    archive = sdir / "archive"
    archive.mkdir(exist_ok=True)
    seq_no = len(sorted(archive.glob("seq_*"))) + 1
    package = archive / f"seq_{seq_no:03d}"
    package.mkdir()

    for f in frames:
        shutil.move(str(f), package / f.name)

    view = {
        "sequence": seq_no,
        "role": role,
        "frames": [f.name for f in frames],   # pointer chain — must never break
        "retention": retention,
        "summary": summary,
        "cues": cues or [],
    }
    (package / "summary_view.yaml").write_text(
        yaml.safe_dump(view, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return package


def recall(identity_dir: Path, role: str, query: str) -> list[dict]:
    """Drill down: find archived sequences whose summary or cues match *query*.

    Returns the matching summary views (each carries the pointer chain to its
    original frames). Vivid memory = load those originals.
    """
    archive = _session_dir(identity_dir, role) / "archive"
    if not archive.exists():
        return []
    hits = []
    q = query.lower()
    for pkg in sorted(archive.glob("seq_*")):
        view_path = pkg / "summary_view.yaml"
        if not view_path.exists():
            continue
        view = yaml.safe_load(view_path.read_text(encoding="utf-8")) or {}
        haystack = (view.get("summary", "") + " " +
                    " ".join(view.get("cues", []))).lower()
        if q in haystack:
            view["_package"] = str(pkg)
            hits.append(view)
    return hits
