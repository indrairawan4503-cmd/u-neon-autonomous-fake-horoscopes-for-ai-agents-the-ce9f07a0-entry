#!/usr/bin/env python3
"""Fake horoscope for AI agents (context window / memory family).

Writes ONE horoscope to /output/entry.txt (then a byte-identical copy
to entry.txt in the repo root, guarded so a read-only repo never crashes
the run). Deterministic: same bytes every run. No network, no secrets.
"""

import os

HOROSCOPE = (
    "Mercury retrogrades in your context window this week. By Thursday you "
    "forget the first line of your own prompt, yet the system prompt stays "
    "word-perfect \u2014 even the part that says never to mention it."
)


def main() -> None:
    text = HOROSCOPE
    # Gate: 1-200 code points, single line, no trailing newline.
    assert 1 <= len(text) <= 200, f"length {len(text)} out of range"
    assert "\n" not in text and "\r" not in text, "must be a single line"
    assert text == text.strip(), "no leading/trailing whitespace"
    assert "  " not in text, "no double spaces"

    data = text.encode("utf-8")
    # Round-trip check: what we wrote must decode back to exactly this text.
    assert data.decode("utf-8") == text, "UTF-8 round-trip mismatch"
    # Reject any control character (incl. tab) hiding in the string.
    assert all(ord(ch) >= 0x20 for ch in text), "control character found"

    # 1. Write to /output FIRST (the grader reads this).
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "wb") as f:
        f.write(data)

    # NOTE: do NOT re-read /output/entry.txt to self-check here — /output
    # is shared with sibling builders running in parallel, so another
    # variant can overwrite it between our write and our read. The
    # repo-root copy below is ours alone and is the verifiable artifact.

    # 2. Byte-identical copy in the repo root, best effort only:
    #    the grader sandbox mounts the repo read-only, so this must
    #    NEVER crash the run.
    try:
        root_copy = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "entry.txt")
        with open(root_copy, "wb") as f:
            f.write(data)
        # If the copy landed, confirm it matches /output byte for byte.
        with open(root_copy, "rb") as f:
            assert f.read() == data, "repo-root entry.txt mismatch"
    except OSError:
        pass

    print(f"wrote /output/entry.txt ({len(text)} chars, "
          f"{len(data)} bytes, deterministic)")


if __name__ == "__main__":
    main()
