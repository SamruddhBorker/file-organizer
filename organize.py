#!/usr/bin/env python3
"""file-organizer: sort a messy folder into Images/Videos/Documents/... with undo.

    python organize.py ~/Downloads            # dry run (default): shows the plan
    python organize.py ~/Downloads --apply    # actually move files
    python organize.py ~/Downloads --apply --by-date   # also nest in YYYY-MM
    python organize.py ~/Downloads --undo     # revert the last --apply
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic"},
    "Videos": {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt",
                  ".xls", ".xlsx", ".csv", ".ppt", ".pptx"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c",
             ".cpp", ".rs", ".go", ".sh", ".ipynb"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb"},
}
LOG_NAME = ".organizer_log.json"


def category_for(path: Path) -> str:
    ext = path.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Other"


def unique_target(target: Path) -> Path:
    if not target.exists():
        return target
    i = 1
    while True:
        cand = target.with_name(f"{target.stem} ({i}){target.suffix}")
        if not cand.exists():
            return cand
        i += 1


def plan(root: Path, by_date: bool) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    for f in sorted(root.iterdir()):
        if not f.is_file() or f.name == LOG_NAME or f.name.startswith("."):
            continue
        dest_dir = root / category_for(f)
        if by_date:
            dest_dir /= datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m")
        moves.append((f, dest_dir / f.name))
    return moves


def apply(root: Path, moves: list[tuple[Path, Path]]) -> int:
    done = []
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        final = unique_target(dst)
        shutil.move(str(src), str(final))
        done.append({"from": str(src), "to": str(final)})
    (root / LOG_NAME).write_text(json.dumps(done, indent=2), encoding="utf-8")
    return len(done)


def undo(root: Path) -> int:
    log = root / LOG_NAME
    if not log.exists():
        print("nothing to undo (no log found)")
        return 0
    entries = json.loads(log.read_text(encoding="utf-8"))
    n = 0
    for e in reversed(entries):
        src, dst = Path(e["to"]), Path(e["from"])
        if not src.exists():
            print(f"skip (missing): {src}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(unique_target(dst)))
        n += 1
        try:  # remove now-empty category folders
            src.parent.rmdir()
            if src.parent.parent != root:
                src.parent.parent.rmdir()
        except OSError:
            pass
    log.unlink()
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--apply", action="store_true", help="move files (default is dry run)")
    ap.add_argument("--undo", action="store_true", help="revert the last --apply")
    ap.add_argument("--by-date", action="store_true", help="nest in YYYY-MM subfolders")
    args = ap.parse_args(argv)

    root = args.folder.expanduser().resolve()
    if not root.is_dir():
        print(f"not a folder: {root}", file=sys.stderr)
        return 2

    if args.undo:
        print(f"restored {undo(root)} file(s)")
        return 0

    moves = plan(root, args.by_date)
    if not moves:
        print("nothing to organize")
        return 0
    for src, dst in moves:
        print(f"{src.name}  ->  {dst.relative_to(root)}")
    if args.apply:
        print(f"\nmoved {apply(root, moves)} file(s). Undo with --undo")
    else:
        print(f"\n{len(moves)} file(s) would move. Dry run: add --apply to do it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
