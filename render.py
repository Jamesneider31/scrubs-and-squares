#!/usr/bin/env python3
"""Fill template.html with a puzzle.json and a greeting, output a self-contained page."""

import json
import sys


def render(template_path, puzzle_path, date_str, greeting_html, signoff_html, out_path):
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    with open(puzzle_path, encoding="utf-8") as f:
        puzzle_json = f.read()

    out = template
    out = out.replace("__PUZZLE_JSON__", puzzle_json)
    out = out.replace("__DATE_STR__", date_str)
    out = out.replace("__GREETING_HTML__", greeting_html)
    out = out.replace("__SIGNOFF_HTML__", signoff_html)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    render(
        "template.html",
        "puzzle.json",
        "Sunday, July 26",
        'Good morning! Here\'s today\'s puzzle to get the brain warmed up before clinicals. <b>14 terms</b> today.',
        "&mdash; James “Poopy Bear”",
        "demo.html",
    )
    print("Wrote demo.html")
