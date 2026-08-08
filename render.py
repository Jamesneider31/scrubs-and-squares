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
    # AAC copies keep the all-in-one daily page far lighter than the original MP3s.
    music_dir = Path(template_path).parent / "assets" / "music-lite"
    music = [
        {"title": "Sweden", "src": "data:audio/mp4;base64," + base64.b64encode((music_dir / "sweden.m4a").read_bytes()).decode("ascii")},
        {"title": "Subwoofer Lullaby", "src": "data:audio/mp4;base64," + base64.b64encode((music_dir / "subwoofer-lullaby.m4a").read_bytes()).decode("ascii")},
        {"title": "Mice on Venus", "src": "data:audio/mp4;base64," + base64.b64encode((music_dir / "mice-on-venus.m4a").read_bytes()).decode("ascii")},
    ]
    sfx_dir = Path(template_path).parent / "assets" / "sfx"

    def audio_data(path):
        return "data:audio/mpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")

    def folder_sounds(name):
        return [audio_data(path) for path in sorted((sfx_dir / name).glob("*.mp3"))]

    sfx = {
        # Add any new .mp3 to either folder; the game randomly selects one.
        "incorrect": folder_sounds("incorrect"),
        "correct": folder_sounds("correct"),
        "levelUp": audio_data(sfx_dir / "complete-levelup.mp3"),
        "imReady": audio_data(sfx_dir / "complete-im-ready.mp3"),
        # Optional: keep the finale working even while a new completion clip is being swapped in.
        "completion": audio_data(sfx_dir / "untitled_60.mp3") if (sfx_dir / "untitled_60.mp3").exists() else None,
    }
    intro_music = {
        "title": "Game of Thrones",
        "src": audio_data(sfx_dir / "abertura-game-of-thrones.mp3"),
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
    out = out.replace("__INTRO_MUSIC_JSON__", json.dumps(intro_music, separators=(",", ":")))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    render_args = (
        "template.html",
        "puzzle.json",
        "Sunday, July 26",
        'Good morning! Here\'s today\'s puzzle to get the brain warmed up before clinicals. <b>14 terms</b> today.',
        "&mdash; James &quot;Poopy Bear&quot;",
    )
    render(*render_args, "demo.html")
    render(*render_args, "index.html")
    print("Wrote demo.html and index.html")
