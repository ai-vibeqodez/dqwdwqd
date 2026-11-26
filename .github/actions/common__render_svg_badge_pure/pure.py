"""Pure function: generate SVG badge with dynamic width calculation."""

import os
import json
import sys
from pathlib import Path


def render_svg_badge(
    width: int,
    height: int,
    text_left: str,
    text_right: str,
    bg_color_left: str,
    bg_color_right: str,
    text_color: str,
) -> str:
    """Render SVG badge with two-segment layout.
    
    Dynamic calculation:
      HALF_WIDTH = width / 2
      QUARTER_WIDTH = width / 4
      THREE_QUARTERS = 3 * width / 4
    """
    half_width = width / 2
    quarter_width = width / 4
    three_quarters = 3 * width / 4
    
    # Approximate character width (monospace baseline)
    char_width = 6
    text_left_x = int(quarter_width - len(text_left) * char_width / 2)
    text_right_x = int(three_quarters - len(text_right) * char_width / 2)
    text_y = int(height / 2 + 3)  # Vertical center + baseline adjustment
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{width}" height="{height}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{half_width}" height="{height}" fill="{bg_color_left}"/>
    <rect x="{half_width}" width="{half_width}" height="{height}" fill="{bg_color_right}"/>
    <rect width="{width}" height="{height}" fill="url(#b)"/>
  </g>
  <g fill="{text_color}" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text aria-hidden="true" x="{text_left_x}" y="{text_y}" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(len(text_left) * char_width - 10) * 10}">{text_left}</text>
    <text x="{text_left_x}" y="{text_y - 1}" transform="scale(.1)" fill="{text_color}" textLength="{(len(text_left) * char_width - 10) * 10}">{text_left}</text>
    <text aria-hidden="true" x="{text_right_x}" y="{text_y}" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(len(text_right) * char_width - 10) * 10}">{text_right}</text>
    <text x="{text_right_x}" y="{text_y - 1}" transform="scale(.1)" fill="{text_color}" textLength="{(len(text_right) * char_width - 10) * 10}">{text_right}</text>
  </g>
</svg>'''
    
    return svg


def main():
    width = int(os.environ.get('INPUT_WIDTH', '120'))
    height = int(os.environ.get('INPUT_HEIGHT', '20'))
    text_left = os.environ.get('INPUT_TEXT_LEFT', 'coverage')
    text_right = os.environ.get('INPUT_TEXT_RIGHT', '80%')
    bg_color_left = os.environ.get('INPUT_BG_COLOR_LEFT', '#555')
    bg_color_right = os.environ.get('INPUT_BG_COLOR_RIGHT', '#44cc11')
    text_color = os.environ.get('INPUT_TEXT_COLOR', '#fff')
    filename = os.environ.get('INPUT_FILENAME', 'badge.svg')
    
    # Render SVG
    svg_content = render_svg_badge(
        width=width,
        height=height,
        text_left=text_left,
        text_right=text_right,
        bg_color_left=bg_color_left,
        bg_color_right=bg_color_right,
        text_color=text_color,
    )
    
    # Write to file (use relative path, not absolute)
    badge_path = Path(filename)
    badge_path.parent.mkdir(parents=True, exist_ok=True)
    with open(badge_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    output = {
        'badge_path': str(badge_path),
        'svg': svg_content,
    }
    
    # Write to GITHUB_OUTPUT
    gh_out = os.environ.get('GITHUB_OUTPUT')
    if gh_out:
        with open(gh_out, 'a', encoding='utf-8') as f:
            f.write(f"json_output={json.dumps(output, ensure_ascii=False)}\n")
    else:
        print("ERROR: GITHUB_OUTPUT not set", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
