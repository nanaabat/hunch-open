"""Mock hunch worker: read a building snapshot JSON and write a labelled mock result.

This is the public stand-in. It does not run the hunch engine, extract features,
or score a space with trained weights. Hosts (the blender panel, a rhino command)
can call the same command the engine worker uses:

    python -m hunch_adapter.worker --input snap.json --output result.json
        [--report report.png] [--progress progress.json]

If a real engine is installed separately, point the host at that environment
instead. This module always returns a mock result, clearly marked as mock.
"""
from __future__ import annotations

import argparse
import json
import os
import traceback


def _write(path: str | None, obj) -> None:
    if not path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
        f.write("\n")
    os.replace(tmp, path)


def mock_result(snap: dict) -> dict:
    target = str((snap or {}).get("target") or "calm")[:40]
    rooms_in = (snap or {}).get("rooms") or []
    if not rooms_in and (snap or {}).get("focus_room"):
        rooms_in = [{"name": snap.get("focus_room")}]
    if not rooms_in:
        rooms_in = [{"name": "space"}]
    rooms = []
    for r in rooms_in:
        name = r.get("name") if isinstance(r, dict) else str(r)
        rooms.append({
            "name": str(name or "space")[:80],
            "atmosphere": {
                "predicted_feel": target,
                "breakdown": "mock read from the target feel only.",
                "mock": True,
            },
        })
    focus_name = str((snap or {}).get("focus_room") or "")
    focus = next((r for r in rooms if r["name"] == focus_name), rooms[0])
    site = (snap or {}).get("site") or ""
    out = {
        "summary": "mock hunch provider. this package does not include the hunch engine.",
        "focus": focus,
        "rooms": rooms,
        "mock": True,
        "target": target,
        "provider": {"name": "hunch-mock", "mock": True},
    }
    if site:
        out["site"] = str(site)[:80]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="mock hunch worker for a host-extracted building snapshot")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--report")
    ap.add_argument("--progress")
    ap.add_argument("--hunch-root")
    a = ap.parse_args(argv)

    def progress(pct, text):
        _write(a.progress, {"progress": float(pct), "status": text, "mock": True})

    try:
        with open(a.input, encoding="utf-8") as f:
            snap = json.load(f)
        progress(0.2, "mock read")
        result = mock_result(snap)
        if a.report:
            # no rendered report image in the mock; leave the path unset
            result["report_image"] = None
        _write(a.output, {"ok": True, "result": result})
        progress(1.0, "done")
        return 0
    except Exception as exc:
        err = {"ok": False, "error": str(exc), "traceback": traceback.format_exc()}
        _write(a.output, err)
        _write(a.progress, {"progress": 1.0, "status": f"failed: {exc}", "mock": True})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
