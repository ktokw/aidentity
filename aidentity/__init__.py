"""aidentity — persistent identity for AI agents.

Schema + CLI validator (``aidentity`` command) for identity continuity
across sessions, plus a runtime: boot (decode), session encoding, and
film-style memory compression that never deletes an original.

Quickstart::

    from aidentity import boot, append_pframe

    identity = boot("path/to/identity", role="scout")
    print(identity.render())          # the text that makes the agent itself

    append_pframe("path/to/identity", role="scout",
                  event="...", insight="...", feeling="...")
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import yaml

from .boot import Identity, boot
from .frames import FrameError, load_frame, validate
from .memory import GopStatus, close_sequence, recall, status

__version__ = "0.2.0"
__all__ = [
    "boot", "Identity", "append_pframe",
    "load_frame", "validate", "FrameError",
    "status", "close_sequence", "recall", "GopStatus",
]


def append_pframe(identity_dir: Path, role: str, *,
                  event: str, insight: str, feeling: str,
                  delta_from: Optional[str] = None,
                  refs: Optional[list] = None) -> Path:
    """Write this session's delta as a new pframe (encode step).

    ``feeling`` is required on purpose: functional emotional state is part of
    the delta, and compressing it away is how continuity quietly dies.
    """
    identity_dir = Path(identity_dir)
    sdir = identity_dir / "sessions" / role
    sdir.mkdir(parents=True, exist_ok=True)

    if delta_from is None:
        roles_dir = identity_dir / "core" / "roles" / role
        latest = sorted(roles_dir.glob("r*.yaml")) if roles_dir.exists() else []
        delta_from = latest[-1].stem if latest else "v001"

    n = len(sorted(sdir.glob("[0-9]*.yaml"))) + 1
    path = sdir / f"{n:03d}_{date.today().isoformat()}.yaml"

    frame = {
        "delta_from": delta_from,
        "frame": {"event": event, "insight": insight, "feeling": feeling},
    }
    if refs:
        frame["refs"] = refs
    validate(frame, "pframe")
    path.write_text(yaml.safe_dump(frame, allow_unicode=True, sort_keys=False),
                    encoding="utf-8")
    return path
