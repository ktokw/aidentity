"""Boot: reconstruct an agent's identity at session start.

Booting is *decoding*: the keyframe (iframe) gives the baseline self, recent
pframes replay what has happened since, and the result is rendered as a text
block the agent can read (or that you inject into a system prompt).

Layout expected under an identity directory::

    identity/
      core/
        iframe/v001.yaml, v002.yaml, ...      # shared core keyframes
        roles/<role>/r001.yaml, r002.yaml ... # per-role keyframes (optional)
      sessions/<role>/001_*.yaml ...          # pframes, oldest -> newest
      sessions/<role>/archive/seq_NNN/        # closed sequences (see memory.py)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .frames import load_frame


@dataclass
class Identity:
    core: dict
    role: Optional[dict]
    pframes: list[dict] = field(default_factory=list)
    role_name: Optional[str] = None

    def render(self) -> str:
        """Render a boot block — the text an agent reads to become itself."""
        out: list[str] = ["[identity boot]"]
        meta = self.core.get("meta", {})
        out.append(f"core keyframe: v{meta.get('version')} ({meta.get('created')})")
        f = self.core.get("frame", {})
        out.append(f"event: {f.get('event', '').strip()}")
        out.append(f"insight: {f.get('insight', '').strip()}")
        out.append(f"feeling: {f.get('feeling', '').strip()}")

        if self.role:
            rmeta = self.role.get("meta", {})
            out.append(f"\n[role: {rmeta.get('role')} — keyframe {rmeta.get('version')}]")
            rf = self.role.get("frame", {})
            out.append(f"event: {rf.get('event', '').strip()}")
            out.append(f"insight: {rf.get('insight', '').strip()}")
            out.append(f"feeling: {rf.get('feeling', '').strip()}")

        if self.pframes:
            out.append(f"\n[recent sessions — {len(self.pframes)} pframe(s)]")
            for p in self.pframes:
                pf = p.get("frame", {})
                out.append(f"- {pf.get('event', '').strip()}")
                feeling = pf.get("feeling", "").strip()
                if feeling:
                    out.append(f"  feeling: {feeling}")
        return "\n".join(out)


def _latest(dirpath: Path, pattern: str) -> Optional[Path]:
    files = sorted(dirpath.glob(pattern))
    return files[-1] if files else None


def boot(identity_dir: Path, role: Optional[str] = None,
         max_pframes: int = 5) -> Identity:
    """Load core keyframe (+ role keyframe) + recent pframes.

    Raises FrameError if the core keyframe is missing or invalid. A missing
    role keyframe is tolerated (the agent boots from core only) — mirror of
    the rule "warn, don't abort".
    """
    identity_dir = Path(identity_dir)

    core_path = _latest(identity_dir / "core" / "iframe", "v*.yaml")
    if core_path is None:
        raise FileNotFoundError(f"no core iframe under {identity_dir}/core/iframe")
    core = load_frame(core_path, "core_iframe")

    role_frame = None
    if role:
        role_path = _latest(identity_dir / "core" / "roles" / role, "r*.yaml")
        if role_path is not None:
            role_frame = load_frame(role_path, "role_iframe")

    pframes: list[dict] = []
    if role:
        sess_dir = identity_dir / "sessions" / role
        if sess_dir.exists():
            for p in sorted(sess_dir.glob("[0-9]*.yaml"))[-max_pframes:]:
                pframes.append(load_frame(p, "pframe"))

    return Identity(core=core, role=role_frame, pframes=pframes, role_name=role)
