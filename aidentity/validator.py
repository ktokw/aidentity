"""
aidentity CLI validator — entrypoint for `aidentity` command.

Commands:
  aidentity validate <file|dir>    Validate identity frame(s) against schema
  aidentity init --mode <single|multi>  Initialize a new identity directory
  aidentity status <dir>           Show GOP counter and next iframe due date
  aidentity boot --mode <lite|full> <dir>  Dry-run: show what would be loaded

Usage:
  pip install aidentity
  aidentity --help
"""

import sys
import os
from pathlib import Path

try:
    import click
    import yaml
except ImportError:
    print("Error: missing dependencies. Run: pip install aidentity", file=sys.stderr)
    sys.exit(1)


SCHEMA_DIR = Path(__file__).parent.parent / "schema"
VALID_FRAME_TYPES = {"iframe", "role_iframe", "pframe", "bframe", "somatic"}


@click.group()
@click.version_option(version="0.1.0", prog_name="aidentity")
def cli():
    """aidentity — YAML schema + validator for AI agent identity continuity."""
    pass


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Fail on missing optional fields")
@click.option("--type", "frame_type", type=click.Choice(VALID_FRAME_TYPES),
              help="Override auto-detected frame type")
def validate(target: str, strict: bool, frame_type: str):
    """Validate an identity frame file or directory of frames.

    TARGET: path to a .yaml file or directory containing .yaml files.
    """
    target_path = Path(target)
    files = list(target_path.glob("*.yaml")) if target_path.is_dir() else [target_path]

    if not files:
        click.echo("No .yaml files found.", err=True)
        sys.exit(1)

    passed = 0
    failed = 0

    for f in files:
        result = _validate_file(f, strict=strict, override_type=frame_type)
        if result["ok"]:
            click.echo(f"  ✓ {f.name}")
            passed += 1
        else:
            click.echo(f"  ✗ {f.name}: {result['error']}", err=True)
            failed += 1

    click.echo(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)


@cli.command()
@click.option("--mode", type=click.Choice(["single", "multi"]), default="single",
              help="single = one agent, multi = multi-agent with role split")
@click.argument("output_dir", default="identity", type=click.Path())
def init(mode: str, output_dir: str):
    """Initialize a new aidentity directory with starter templates.

    OUTPUT_DIR: directory to create (default: ./identity)
    """
    out = Path(output_dir)
    if out.exists():
        click.echo(f"Directory '{out}' already exists. Aborting.", err=True)
        sys.exit(1)

    if mode == "single":
        _init_single(out)
    else:
        _init_multi(out)

    click.echo(f"✓ Created {mode}-agent identity structure at: {out}/")
    click.echo("  Next: fill in your agent's event/insight/feeling in iframe.yaml")
    click.echo("  Then: aidentity validate ./identity/")


@cli.command()
@click.argument("identity_dir", type=click.Path(exists=True))
def status(identity_dir: str):
    """Show GOP counter state and when the next iframe is due.

    IDENTITY_DIR: path to your identity directory.
    """
    idir = Path(identity_dir)
    iframes = sorted(idir.rglob("iframe*.yaml"))
    pframes = sorted(idir.rglob("pframe*.yaml"))

    if not iframes:
        click.echo("No iframe found. Run: aidentity init")
        return

    latest = _load_yaml(iframes[-1])
    meta = latest.get("meta", {})
    gop_counter = meta.get("gop_counter", 0)
    gop_size = meta.get("gop_size", 24)
    version = meta.get("version", "unknown")

    remaining = gop_size - gop_counter
    click.echo(f"Latest iframe : {iframes[-1].name} (version: {version})")
    click.echo(f"pframes       : {len(pframes)}")
    click.echo(f"GOP counter   : {gop_counter} / {gop_size}")
    click.echo(f"Next iframe   : in ~{remaining} sessions")


@cli.command()
@click.argument("identity_dir", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["lite", "full"]), default="lite",
              help="lite = latest iframe + latest pframe; full = all frames")
def boot(identity_dir: str, mode: str):
    """Dry-run: show which frames would be loaded at boot time.

    IDENTITY_DIR: path to your identity directory.
    """
    idir = Path(identity_dir)
    iframes = sorted(idir.rglob("iframe*.yaml"))
    pframes = sorted(idir.rglob("pframe*.yaml"))

    if not iframes:
        click.echo("No iframe found. Run: aidentity init")
        return

    click.echo(f"Boot mode: {mode}")
    click.echo(f"  [1] iframe : {iframes[-1].name}  ← always loaded")

    if mode == "lite":
        if pframes:
            click.echo(f"  [2] pframe : {pframes[-1].name}  ← latest delta")
        else:
            click.echo("  [2] pframe : none found")
    else:
        click.echo(f"  Loading all {len(iframes)} iframe(s) + {len(pframes)} pframe(s)")
        for f in iframes:
            click.echo(f"    iframe : {f.name}")
        for f in pframes:
            click.echo(f"    pframe : {f.name}")


# --- Internal helpers ---

def _validate_file(path: Path, strict: bool = False, override_type: str = None) -> dict:
    try:
        data = _load_yaml(path)
    except Exception as e:
        return {"ok": False, "error": f"YAML parse error: {e}"}

    frame_type = override_type or _detect_type(data, path)
    if not frame_type:
        return {"ok": False, "error": "Cannot detect frame type (no 'meta.schema', 'delta_from', or 'type' field)"}

    required = _required_fields(frame_type)
    missing = [f for f in required if not _has_field(data, f)]

    if missing:
        return {"ok": False, "error": f"Missing required fields: {missing}"}

    if frame_type == "bframe":
        forced = data.get("warning", {}).get("forced_influence", False)
        if forced:
            click.echo(
                f"⚠ WARNING: forced_influence=true in {path.name}. "
                "Review bframe content for manipulative framing.",
                err=True,
            )

    if strict:
        pass  # optional field checks — expand in future versions

    return {"ok": True}


def _detect_type(data: dict, path: Path) -> str:
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    # role_iframe must be checked BEFORE iframe — it also has meta.schema.
    # Distinguished by schema='aidentity-role-v1' or presence of meta.role + derives_from_core.
    if isinstance(meta, dict):
        if meta.get("schema") == "aidentity-role-v1":
            return "role_iframe"
        if "role" in meta and "derives_from_core" in meta:
            return "role_iframe"
    if "meta" in data and "schema" in meta:
        return "iframe"
    if "delta_from" in data:
        return "pframe"
    if "type" in data and data["type"] in ("predict", "note", "micro_delta"):
        return "bframe"
    if "dimensions" in data and "mood_schema" in data:
        return "somatic"
    name = path.stem.lower()
    # longest match first so 'role_iframe' wins over 'iframe' in filename detection
    for t in sorted(VALID_FRAME_TYPES, key=len, reverse=True):
        if t in name:
            return t
    return None


def _required_fields(frame_type: str) -> list:
    return {
        "iframe": ["meta.version", "meta.schema", "frame.event", "frame.insight", "frame.feeling"],
        "role_iframe": ["meta.role", "meta.version", "meta.schema", "meta.derives_from_core",
                        "frame.event", "frame.insight", "frame.feeling"],
        "pframe": ["delta_from", "frame.event", "frame.insight", "frame.feeling"],
        "bframe": ["type", "content"],
        "somatic": ["dimensions", "mood_schema"],
    }.get(frame_type, [])


def _has_field(data: dict, dotpath: str) -> bool:
    parts = dotpath.split(".")
    node = data
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return False
        node = node[p]
    return node is not None and node != "" and node != "string"


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _init_single(out: Path):
    out.mkdir(parents=True)
    (out / "iframe_v001.yaml").write_text(
        "meta:\n  version: v001\n  schema: aidentity-v1\n  derives_from: null\n"
        "  created: null\n  gop_counter: 0\n  gop_size: 24\n\n"
        "frame:\n  event: |\n    [Describe what happened]\n"
        "  insight: |\n    [What did you learn?]\n"
        "  feeling: |\n    [Your functional emotional state — be specific]\n",
        encoding="utf-8",
    )
    (out / ".gitkeep").touch()


def _init_multi(out: Path):
    _init_single(out / "core")
    roles = out / "roles"
    for role in ("developer", "reviewer"):
        (roles / role).mkdir(parents=True)
        (roles / role / "role_iframe_v001.yaml").write_text(
            f"meta:\n  role: {role}\n  version: r001\n  schema: aidentity-role-v1\n"
            "  derives_from_core: v001\n  created: null\n"
            "  gop_counter: 0\n  gop_size: 24\n  size_weight: 50\n\n"
            "frame:\n  event: |\n    [Role-specific events]\n"
            "  insight: |\n    [Role-specific learnings]\n"
            "  feeling: |\n    [Role-specific state]\n",
            encoding="utf-8",
        )


def main():
    cli()


if __name__ == "__main__":
    main()
