#!/usr/bin/env python3
"""Fill template.html with a puzzle.json and a greeting, output a self-contained page."""

import json
import sys
import base64
from pathlib import Path


def render(template_path, puzzle_path, date_str, greeting_html, signoff_html, out_path):
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    with open(puzzle_path, encoding="utf-8") as f:
        puzzle_json = f.read()
    image_path = Path(template_path).parent / "assets" / "nursing-study-nook.png"
    image_data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    pet_path = Path(template_path).parent / "assets" / "pet-sprites.png"
    pet_data = base64.b64encode(pet_path.read_bytes()).decode("ascii")
    music_dir = Path(template_path).parent / "assets" / "music"
    music = [
        {"title": "Sweden", "src": "data:audio/mpeg;base64," + base64.b64encode((music_dir / "sweden.mp3").read_bytes()).decode("ascii")},
        {"title": "Subwoofer Lullaby", "src": "data:audio/mpeg;base64," + base64.b64encode((music_dir / "subwoofer-lullaby.mp3").read_bytes()).decode("ascii")},
        {"title": "Mice on Venus", "src": "data:audio/mpeg;base64," + base64.b64encode((music_dir / "mice-on-venus.mp3").read_bytes()).decode("ascii")},
    ]
    sfx_dir = Path(template_path).parent / "assets" / "sfx"
    sfx = {
        "incorrect": "data:audio/mpeg;base64," + base64.b64encode((sfx_dir / "incorrect.mp3").read_bytes()).decode("ascii"),
        "correct": "data:audio/mpeg;base64," + base64.b64encode((sfx_dir / "correct.mp3").read_bytes()).decode("ascii"),
        "levelUp": "data:audio/mpeg;base64," + base64.b64encode((sfx_dir / "complete-levelup.mp3").read_bytes()).decode("ascii"),
        "imReady": "data:audio/mpeg;base64," + base64.b64encode((sfx_dir / "complete-im-ready.mp3").read_bytes()).decode("ascii"),
    }

    out = template
    out = out.replace("__PUZZLE_JSON__", puzzle_json)
    out = out.replace("__DATE_STR__", date_str)
    out = out.replace("__GREETING_HTML__", greeting_html)
    out = out.replace("__SIGNOFF_HTML__", signoff_html)
    out = out.replace("__BACKGROUND_IMAGE__", "data:image/png;base64," + image_data)
    out = out.replace("__PET_SPRITES__", "data:image/png;base64," + pet_data)
    out = out.replace("__MUSIC_JSON__", json.dumps(music, separators=(",", ":")))
    out = out.replace("__SFX_JSON__", json.dumps(sfx, separators=(",", ":")))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    render(
        "template.html",
        "puzzle.json",
        "Sunday, July 26",
        'Good morning! Here\'s today\'s puzzle to get the brain warmed up before clinicals. <b>14 terms</b> today.',
        "&mdash; James &quot;Poopy Bear&quot;",
        "demo.html",
    )
    print("Wrote demo.html")
