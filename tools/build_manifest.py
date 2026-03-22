#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def collect_items(repo_root: Path, lane: str):
    lane_root = repo_root / lane / "maps"
    items = []
    if not lane_root.exists():
        return items
    for meta_path in lane_root.rglob("meta.json"):
        meta = safe_read_json(meta_path)
        if not isinstance(meta, dict):
            continue

        pkg = str(meta.get("package", "")).strip()
        map_id = str(meta.get("map_id", "")).strip()
        submitted_at = str(meta.get("submitted_at", "")).strip()
        stable_at = str(meta.get("stable_at", "")).strip()
        description = str(meta.get("description", "")).strip()

        art = meta.get("artifacts") if isinstance(meta.get("artifacts"), dict) else {}
        map_path = str(art.get("map_path", "")).strip()
        sha256 = str(art.get("sha256", "")).strip()

        if not map_path:
            guess = meta_path.parent / "nav_map.json.gz"
            if guess.exists():
                map_path = guess.relative_to(repo_root).as_posix()

        if not pkg:
            try:
                pkg = meta_path.parent.parent.name
            except Exception:
                pkg = ""
        if not map_id:
            try:
                map_id = meta_path.parent.name
            except Exception:
                map_id = ""

        items.append(
            {
                "lane": lane,
                "package": pkg,
                "map_id": map_id,
                "submitted_at": submitted_at,
                "stable_at": stable_at,
                "description": description,
                "map_path": map_path,
                "meta_path": meta_path.relative_to(repo_root).as_posix(),
                "sha256": sha256,
            }
        )

    def sort_key(x):
        t = x.get("stable_at") or x.get("submitted_at") or ""
        return (x.get("package") or "", t, x.get("map_id") or "")

    items.sort(key=sort_key, reverse=True)
    return items


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--lanes", nargs="*", default=["stable", "candidates"])
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    generated_at = now_iso()

    all_items = []
    for lane in args.lanes:
        items = collect_items(root, lane)
        payload = {
            "schema_version": "lxb.map.manifest.v1",
            "lane": lane,
            "generated_at": generated_at,
            "count": len(items),
            "items": items,
        }
        write_json(root / "manifests" / lane / "latest.json", payload)
        all_items.extend(items)

    write_json(
        root / "manifests" / "all" / "latest.json",
        {
            "schema_version": "lxb.map.manifest.v1",
            "lane": "all",
            "generated_at": generated_at,
            "count": len(all_items),
            "items": all_items,
        },
    )


if __name__ == "__main__":
    main()
