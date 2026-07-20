"""Frame loading and validation.

aidentity models an agent's identity as a stream of frames, borrowing the
vocabulary of video codecs:

- **iframe**  — identity keyframe. A complete self-snapshot. Everything else
  is a delta against it.
- **pframe**  — predictive frame. What changed since the keyframe: the events,
  insights and feelings of one session. Meaningless without its iframe.
- **bframe**  — bidirectional frame. A prediction or a note addressed to the
  future self. Use sparingly.

Frames are plain YAML files. This module loads them and checks the required
fields; it never mutates them.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml


class FrameError(ValueError):
    """A frame file is missing or structurally invalid."""


REQUIRED: dict[str, list[str]] = {
    # dotted paths that must exist and be non-empty
    "core_iframe": [
        "meta.version", "meta.schema", "meta.created",
        "frame.event", "frame.insight", "frame.feeling",
    ],
    "role_iframe": [
        "meta.role", "meta.version", "meta.schema", "meta.derives_from_core",
        "meta.created",
        "frame.event", "frame.insight", "frame.feeling",
    ],
    "pframe": [
        "delta_from",
        "frame.event", "frame.insight", "frame.feeling",
    ],
    "bframe": [
        "type", "content",
    ],
}


def _get(data: dict, dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def load_yaml(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FrameError(f"no such frame file: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise FrameError(f"invalid YAML in {path}: {e}") from e
    if not isinstance(data, dict):
        raise FrameError(f"frame is not a mapping: {path}")
    return data


def validate(data: dict, kind: str, path: Optional[Path] = None) -> dict:
    """Validate required fields for the given frame kind. Returns the data."""
    if kind not in REQUIRED:
        raise FrameError(f"unknown frame kind: {kind!r}")
    missing = [f for f in REQUIRED[kind] if _get(data, f) in (None, "")]
    if missing:
        where = f" ({path})" if path else ""
        raise FrameError(f"{kind} missing required fields {missing}{where}")
    return data


def load_frame(path: Path, kind: str) -> dict:
    """Load a YAML frame file and validate it as *kind*."""
    return validate(load_yaml(path), kind, path)
