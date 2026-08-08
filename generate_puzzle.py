#!/usr/bin/env python3
"""
Crossword layout generator.

Takes a list of {"word": ..., "clue": ...} entries and produces a puzzle
JSON: a grid of intersecting words, numbered the standard crossword way,
plus across/down clue lists. No external dependencies.

Usage:
    python3 generate_puzzle.py words.json puzzle.json
or import build_puzzle(word_clue_list) directly.
"""

import json
import random
import re
import sys
import hashlib
from collections import Counter


def normalize_word(raw):
    return re.sub(r"[^A-Z]", "", raw.upper())


def can_place(grid, word, row, col, direction):
    """Check if `word` can be placed at (row, col) in `direction`
    ('across' or 'down') without illegally touching other words."""
    dr, dc = (0, 1) if direction == "across" else (1, 0)

    # Cell immediately before the word's start and after its end must be empty,
    # otherwise this word would silently merge into a longer run of letters.
    before = (row - dr, col - dc)
    after = (row + dr * len(word), col + dc * len(word))
    if before in grid or after in grid:
        return False

    crossed = False
    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i
        if (r, c) in grid:
            if grid[(r, c)] != ch:
                return False
            crossed = True
        else:
            # A new letter cell must not be side-by-side with an unrelated
            # word running the other direction (would create an accidental
            # extra "word" of jammed-together letters).
            if direction == "across":
                if (r - 1, c) in grid or (r + 1, c) in grid:
                    return False
            else:
                if (r, c - 1) in grid or (r, c + 1) in grid:
                    return False
    return crossed


def _build_puzzle_once(entries, seed=None, max_words=16):
    """entries: list of {"word": str, "clue": str}. Returns puzzle dict."""
    rng = random.Random(seed)

    cleaned = []
    for e in entries:
        w = normalize_word(e["word"])
        if len(w) >= 3:
            cleaned.append({
                "word": w,
                "clue": e["clue"].strip(),
                "rationale": e.get("rationale", "").strip(),
                "topic": e.get("topic", "NCLEX Review").strip() or "NCLEX Review",
            })
    # longest first tends to build a sturdier scaffold
    cleaned.sort(key=lambda e: (-len(e["word"]), rng.random()))
    cleaned = cleaned[:max_words]

    grid = {}
    placed = []  # list of dicts: word, clue, row, col, direction
    leftover = cleaned[1:]
    first = cleaned[0]

    for i, ch in enumerate(first["word"]):
        grid[(0, i)] = ch
    placed.append({"word": first["word"], "clue": first["clue"], "rationale": first["rationale"], "topic": first["topic"], "row": 0, "col": 0, "direction": "across"})

    def bbox():
        rs = [r for r, c in grid]
        cs = [c for r, c in grid]
        return min(rs), max(rs), min(cs), max(cs)

    def try_place_all(word_list):
        still_left = []
        for entry in word_list:
            word = entry["word"]
            candidates = []
            for (r, c), letter in grid.items():
                for i, ch in enumerate(word):
                    if ch != letter:
                        continue
                    candidates.append((r - i, c, "across"))
                    candidates.append((r, c - i, "down"))
            rng.shuffle(candidates)
            min_r, max_r, min_c, max_c = bbox()
            best = None
            best_score = -1
            for (row, col, direction) in candidates:
                if can_place(grid, word, row, col, direction):
                    dr, dc = (0, 1) if direction == "across" else (1, 0)
                    crossings = sum(1 for i in range(len(word)) if (row + dr * i, col + dc * i) in grid)
                    new_min_r = min(min_r, row)
                    new_max_r = max(max_r, row + dr * (len(word) - 1))
                    new_min_c = min(min_c, col)
                    new_max_c = max(max_c, col + dc * (len(word) - 1))
                    old_area = (max_r - min_r + 1) * (max_c - min_c + 1)
                    new_area = (new_max_r - new_min_r + 1) * (new_max_c - new_min_c + 1)
                    score = crossings * 200 - (new_area - old_area)
                    if score > best_score:
                        best_score = score
                        best = (row, col, direction)
            if best:
                row, col, direction = best
                dr, dc = (0, 1) if direction == "across" else (1, 0)
                for i, ch in enumerate(word):
                    grid[(row + dr * i, col + dc * i)] = ch
                placed.append({"word": word, "clue": entry["clue"], "rationale": entry["rationale"], "topic": entry["topic"], "row": row, "col": col, "direction": direction})
            else:
                still_left.append(entry)
        return still_left

    for _ in range(4):  # multiple passes: newly placed words open up fresh intersections
        if not leftover:
            break
        leftover = try_place_all(leftover)

    if len(placed) < 5:
        raise ValueError(f"Only placed {len(placed)} words — word list needs more shared letters.")

    # Normalize coordinates to start at (0, 0)
    min_r = min(r for r, c in grid)
    min_c = min(c for r, c in grid)
    norm_grid = {(r - min_r, c - min_c): ch for (r, c), ch in grid.items()}
    for p in placed:
        p["row"] -= min_r
        p["col"] -= min_c

    height = max(r for r, c in norm_grid) + 1
    width = max(c for r, c in norm_grid) + 1

    # Standard crossword numbering: scan row-major, number any cell that
    # starts an across and/or down entry.
    numbers = {}
    next_num = 1
    for r in range(height):
        for c in range(width):
            if (r, c) not in norm_grid:
                continue
            starts_across = (r, c - 1) not in norm_grid and (r, c + 1) in norm_grid
            starts_down = (r - 1, c) not in norm_grid and (r + 1, c) in norm_grid
            if starts_across or starts_down:
                numbers[(r, c)] = next_num
                next_num += 1

    entries_out = []
    for p in placed:
        num = numbers[(p["row"], p["col"])]
        entries_out.append({
            "number": num,
            "direction": p["direction"],
            "row": p["row"],
            "col": p["col"],
            "length": len(p["word"]),
            "answer": p["word"],
            "clue": p["clue"],
            "rationale": p["rationale"],
            "topic": p["topic"],
        })
    entries_out.sort(key=lambda e: (e["number"], e["direction"]))

    cells = [[None] * width for _ in range(height)]
    for (r, c), ch in norm_grid.items():
        cells[r][c] = ch

    topic = Counter(e["topic"] for e in entries_out).most_common(1)[0][0]
    puzzle_id_source = "|".join(
        f"{e['answer']}:{e['clue']}:{e['row']}:{e['col']}:{e['direction']}"
        for e in entries_out
    )
    return {
        "id": hashlib.sha256(puzzle_id_source.encode("utf-8")).hexdigest()[:16],
        "topic": topic,
        "width": width,
        "height": height,
        "cells": cells,
        "numbers": {f"{r},{c}": n for (r, c), n in numbers.items()},
        "entries": entries_out,
    }


def _layout_score(puzzle):
    """Favor complete, compact grids with plenty of crossings and balanced directions."""
    entries = puzzle["entries"]
    filled = sum(cell is not None for row in puzzle["cells"] for cell in row)
    area = puzzle["width"] * puzzle["height"]
    across = sum(e["direction"] == "across" for e in entries)
    down = len(entries) - across
    crossings = sum(
        1 for r, row in enumerate(puzzle["cells"])
        for c, cell in enumerate(row)
        if cell is not None and sum(
            e["row"] <= r < e["row"] + (e["length"] if e["direction"] == "down" else 1)
            and e["col"] <= c < e["col"] + (e["length"] if e["direction"] == "across" else 1)
            for e in entries
        ) > 1
    )
    compactness = filled / area if area else 0
    balance = 1 - abs(across - down) / max(1, len(entries))
    return len(entries) * 10000 + crossings * 180 + compactness * 100 + balance * 30


def build_puzzle(entries, seed=None, max_words=16, retries=36):
    """Generate several valid layouts, then keep the most compact, cross-rich one."""
    seed_rng = random.Random(seed)
    best = None
    best_score = float("-inf")
    errors = []
    for _ in range(max(1, retries)):
        attempt_seed = seed_rng.randrange(2**32)
        try:
            candidate = _build_puzzle_once(entries, seed=attempt_seed, max_words=max_words)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        score = _layout_score(candidate)
        if score > best_score:
            best, best_score = candidate, score
    if best is None:
        raise ValueError(errors[-1] if errors else "Could not build a valid crossword layout.")
    best["quality"] = {
        "layout_attempts": max(1, retries),
        "score": round(best_score, 1),
        "placed_entries": len(best["entries"]),
    }
    return best


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "words.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "puzzle.json"
    with open(src) as f:
        word_list = json.load(f)
    puzzle = build_puzzle(word_list)
    with open(dst, "w") as f:
        json.dump(puzzle, f, indent=2)
    placed_words = {e["answer"] for e in puzzle["entries"]}
    skipped = [w["word"] for w in word_list if normalize_word(w["word"]) not in placed_words]
    print(f"Placed {len(puzzle['entries'])} entries in a {puzzle['width']}x{puzzle['height']} grid.")
    if skipped:
        print(f"Skipped (no valid crossing found): {skipped}")
