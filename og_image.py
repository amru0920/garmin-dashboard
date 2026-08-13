"""Generates og-image.png (1200x630) for link-preview cards (WhatsApp, Twitter,
etc.), matching the dashboard's dark theme. Regenerated every dashboard.py run --
cheap enough not to need caching."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 630

PAGE = (13, 13, 13)
SURFACE = (26, 26, 25)
BORDER = (46, 46, 44)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (195, 194, 183)
TEXT_MUTED = (137, 135, 129)
# blue, orange, violet, blue -- same categorical slots as the dashboard's stat tiles
ACCENTS = [(57, 135, 229), (217, 89, 38), (144, 133, 233), (57, 135, 229)]

FONT_DIR = Path(r"C:\Windows\Fonts")
FONT_BOLD = FONT_DIR / "segoeuib.ttf"
FONT_REGULAR = FONT_DIR / "segoeui.ttf"


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _fit_text(
    draw: ImageDraw.ImageDraw, text: str, font_path: Path,
    max_width: int, start_size: int, min_size: int = 28,
) -> tuple[ImageFont.FreeTypeFont, str]:
    """Shrink the font until the text fits max_width; if it still doesn't fit at
    min_size (e.g. an unusually long race name), truncate with an ellipsis --
    the text must never be allowed to run off the card."""
    size = start_size
    while size > min_size:
        font = _font(font_path, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font, text
        size -= 2

    font = _font(font_path, min_size)
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return font, text
    truncated = text
    while truncated and draw.textbbox((0, 0), truncated + "…", font=font)[2] > max_width:
        truncated = truncated[:-1]
    return font, (truncated.rstrip() + "…") if truncated else text[:1]


def _fmt_value(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def generate_og_image(data: dict, output_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), PAGE)
    draw = ImageDraw.Draw(img)

    margin = 48
    card_box = (margin, margin, WIDTH - margin, HEIGHT - margin)
    draw.rounded_rectangle(card_box, radius=28, fill=SURFACE, outline=BORDER, width=2)

    pad_x = card_box[0] + 56
    pad_right = card_box[2] - 56
    content_width = pad_right - pad_x
    y = card_box[1] + 48

    # eyebrow label
    eyebrow_font = _font(FONT_REGULAR, 20)
    draw.text((pad_x, y), " ".join("TRAINING DASHBOARD"), font=eyebrow_font, fill=TEXT_MUTED)
    y += 42

    # race name headline -- shrink to fit, never overflow the card
    race_name = data["race"]["name"]
    headline_font, race_name = _fit_text(draw, race_name, FONT_BOLD, content_width, start_size=54, min_size=32)
    draw.text((pad_x, y), race_name, font=headline_font, fill=TEXT_PRIMARY)
    headline_bbox = draw.textbbox((pad_x, y), race_name, font=headline_font)
    y = headline_bbox[3] + 26

    # countdown: big number + unit baseline-aligned, same hierarchy as .hero-countdown
    days_left = data["race"]["days_left"]
    num_font = _font(FONT_BOLD, 104)
    unit_font = _font(FONT_REGULAR, 28)
    num_text = str(days_left)
    num_bbox = draw.textbbox((pad_x, y), num_text, font=num_font)
    draw.text((pad_x, y), num_text, font=num_font, fill=TEXT_PRIMARY)
    draw.text(
        (num_bbox[2] + 16, num_bbox[3] - 38), "days to go",
        font=unit_font, fill=TEXT_SECONDARY,
    )
    y = num_bbox[3] + 34

    # stat tiles row: Fitness / Fatigue / Form / VO2max
    tiles = [
        ("FITNESS", data["stat_tiles"].get("fitness")),
        ("FATIGUE", data["stat_tiles"].get("fatigue")),
        ("FORM", data["stat_tiles"].get("form")),
        ("VO2 MAX", data["stat_tiles"].get("vo2max")),
    ]
    tile_gap = 28
    tile_width = (content_width - tile_gap * (len(tiles) - 1)) / len(tiles)
    label_font = _font(FONT_REGULAR, 18)
    value_font = _font(FONT_BOLD, 40)

    for i, (label, value) in enumerate(tiles):
        tx = pad_x + i * (tile_width + tile_gap)
        accent = ACCENTS[i % len(ACCENTS)]
        draw.rectangle((tx, y, tx + 44, y + 4), fill=accent)
        draw.text((tx, y + 18), label, font=label_font, fill=TEXT_MUTED)
        draw.text((tx, y + 44), _fmt_value(value), font=value_font, fill=TEXT_PRIMARY)

    img.save(output_path, "PNG")
