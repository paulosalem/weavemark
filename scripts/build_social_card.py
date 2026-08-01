"""Generate the 1200x630 social preview used by the public site."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "weavemark_social.png"
WIDTH = 1200
HEIGHT = 630


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for name in names:
        path = Path(name)
        if path.is_file():
            return ImageFont.truetype(path, size)
    raise FileNotFoundError("No supported social-card font is installed.")


def _rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def build() -> None:
    """Render the social card deterministically from checked-in assets."""

    image = Image.new("RGB", (WIDTH, HEIGHT), "#f6fbfa")
    draw = ImageDraw.Draw(image)

    for y in range(0, HEIGHT, 44):
        draw.line((0, y, WIDTH, y), fill="#e8f0ef", width=1)
    for x in range(0, WIDTH, 44):
        draw.line((x, 0, x, HEIGHT), fill="#e8f0ef", width=1)

    draw.ellipse((-220, -240, 570, 550), fill="#dff5f4")
    draw.ellipse((760, 360, 1380, 980), fill="#fff1ed")

    logo = Image.open(ROOT / "docs" / "weavemark_logo.png").convert("RGBA")
    alpha_box = logo.getchannel("A").getbbox()
    if alpha_box is not None:
        logo = logo.crop(alpha_box)
    logo.thumbnail((390, 88), Image.Resampling.LANCZOS)
    image.paste(logo, (64, 46), logo)

    kicker_font = _font(18, bold=True)
    title_font = _font(54, bold=True)
    body_font = _font(25)
    code_font = _font(19)
    code_bold = _font(19, bold=True)

    _rounded(
        draw,
        (64, 164, 662, 212),
        radius=24,
        fill="#dff5f4",
        outline="#a7d9da",
        width=2,
    )
    draw.ellipse((82, 178, 102, 198), fill="#f9735b")
    draw.text(
        (118, 177),
        "READABLE, REUSABLE, AND COMPOSABLE PROMPTS",
        fill="#183060",
        font=kicker_font,
    )

    draw.multiline_text(
        (64, 245),
        "Compose prompts\nlike software.",
        fill="#102033",
        font=title_font,
        spacing=2,
    )
    draw.multiline_text(
        (64, 370),
        "Read them\nlike Markdown.",
        fill="#285e78",
        font=title_font,
        spacing=2,
    )
    draw.text(
        (66, 526),
        "LLM-compiled / semantic imports / strict offline replay",
        fill="#52677d",
        font=body_font,
    )

    _rounded(
        draw,
        (710, 48, 1140, 582),
        radius=32,
        fill="#0e1d36",
        outline="#31547a",
        width=2,
    )
    draw.ellipse((742, 76, 760, 94), fill="#fb7185")
    draw.ellipse((770, 76, 788, 94), fill="#ffb84d")
    draw.ellipse((798, 76, 816, 94), fill="#48b4cc")
    draw.text((842, 74), "market-snapshot.weavemark.md", fill="#93a9c1", font=_font(13))
    draw.line((738, 112, 1112, 112), fill="#27415f", width=2)

    code_lines = (
        ("@use", "#fb8cb4", code_bold),
        ("  weavemark.domains.finance.", "#91a7be", code_font),
        ("  market_research", "#48b4cc", code_bold),
        ("", "#ffffff", code_font),
        ("@execute functional", "#fb8cb4", code_bold),
        ("  scheduler: graph-strict", "#91a7be", code_font),
        ("", "#ffffff", code_font),
        ("# VALE3 Market Snapshot", "#f6fbfa", code_bold),
        ("", "#ffffff", code_font),
        ("@fetch_asset_snapshot", "#fb8cb4", code_bold),
        ("@search_asset_context", "#fb8cb4", code_bold),
    )
    y = 148
    for text, color, font in code_lines:
        draw.text((746, y), text, fill=color, font=font)
        y += 31

    _rounded(
        draw,
        (746, 508, 1106, 552),
        radius=20,
        fill="#173857",
        outline="#3c7884",
    )
    draw.text(
        (774, 520),
        "> offline replay / original run stats",
        fill="#a5f3fc",
        font=_font(16, bold=True),
    )

    image.save(OUTPUT, optimize=True)


if __name__ == "__main__":
    build()
