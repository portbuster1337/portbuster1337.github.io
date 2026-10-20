"""Normalize rendered Mermaid SVGs for static, grayscale, no-JS pages.

Run after rendering the .mmd sources:

    python3 postprocess.py

The script sets an intrinsic width and height from the viewBox so the SVG
renders at a predictable size inside an <img>, removes inline max-width and
shadow filters, and leaves only local system fonts.
"""

from pathlib import Path
import math
import re

HERE = Path(__file__).resolve().parent
SVG_DIR = HERE.parent


def normalize(path: Path) -> tuple[int, int]:
    text = path.read_text()

    view_box = re.search(r'viewBox="([^"]+)"', text)
    if not view_box:
        raise ValueError(f"{path.name}: no viewBox")

    values = [float(value) for value in view_box.group(1).split()]
    width = math.ceil(values[2])
    height = math.ceil(values[3])

    start = text.index("<svg")
    end = text.index(">", start) + 1
    tag = text[start:end]
    tag = re.sub(r'\swidth="[^"]*"', "", tag)
    tag = re.sub(r'\sheight="[^"]*"', "", tag)
    tag = re.sub(r'\sstyle="[^"]*"', "", tag)
    tag = tag[:-1] + (
        f' width="{width}" height="{height}" '
        'style="background-color:#ffffff;">'
    )
    text = text[:start] + tag + text[end:]

    # Mermaid emits these even when no node uses a shadow. Remove both.
    text = re.sub(
        r'<defs><filter id="my-svg-drop-shadow[^"]*".*?</filter></defs>',
        "",
        text,
        flags=re.S,
    )
    text = text.replace("filter:none)", "filter:none;")
    path.write_text(text)
    return width, height


if __name__ == "__main__":
    for svg in sorted(SVG_DIR.glob("*.svg")):
        width, height = normalize(svg)
        print(f"{svg.name}: {width}x{height}")
