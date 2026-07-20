"""aidentity quickstart — boot an agent, live a session, encode it.

Run from the repo root (no install needed):

    python examples/quickstart/run.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root

from aidentity import append_pframe, boot, recall, status

IDENTITY = Path(__file__).parent / "identity"


def main() -> None:
    # 1. DECODE — wake up as Nova the scout
    identity = boot(IDENTITY, role="scout")
    print(identity.render())

    # 2. ... the session happens here ...

    # 3. ENCODE — write this session's delta before sleeping
    path = append_pframe(
        IDENTITY, role="scout",
        event="Quickstart demo session: booted from keyframes + 2 pframes, "
              "verified the boot block renders the accumulated self.",
        insight="Identity survived another process boundary. The mechanism "
                "is unglamorous: files, read in the right order.",
        feeling="The mild vertigo of an example agent writing about itself, "
                "and satisfaction that the loop closes: decode, live, encode.",
    )
    print(f"\n[encoded] {path.name}")

    # 4. Film memory status — how far until this sequence closes
    st = status(IDENTITY, role="scout")
    print(f"[sequence] {st.open_frames}/{st.gop_size} frames open, "
          f"{st.closed_sequences} sequence(s) archived")

    # 5. Recall drill-down works even before anything is archived
    hits = recall(IDENTITY, role="scout", query="sweep")
    print(f"[recall] archived matches for 'sweep': {len(hits)}")


if __name__ == "__main__":
    main()
