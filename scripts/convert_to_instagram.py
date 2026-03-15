#!/usr/bin/env python3
"""
Convert PDFs or Markdown files to Instagram-ready images (1080x1350, 4:5 ratio)

USAGE:
    # Convert PDF
    python convert_to_instagram.py input.pdf

    # Convert Markdown
    python convert_to_instagram.py input.md

    # Convert all PDFs in directory
    python convert_to_instagram.py --dir /path/to/pdfs

    # Specify output directory
    python convert_to_instagram.py input.md --output ./instagram_output

REQUIRES:
    pip install pdf2image Pillow reportlab
"""

import argparse
import re
import sys
from pathlib import Path
from textwrap import wrap

try:
    from PIL import Image, ImageDraw, ImageFont
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install pdf2image Pillow")
    sys.exit(1)

# Instagram dimensions (4:5 portrait ratio)
INSTA_WIDTH = 1080
INSTA_HEIGHT = 1350
MARGIN = 60
INNER_MARGIN = 40

# Colors
BG_COLOR = (250, 248, 245)      # Warm off-white
ACCENT_COLOR = (220, 38, 38)    # Red
TEXT_COLOR = (30, 30, 30)       # Dark gray
MUTED_COLOR = (100, 100, 100)   # Gray

# Font loading with fallbacks
def get_font(size, bold=False):
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Helvetica-Bold.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in font_paths:
        try:
            if bold and "Bold" in path:
                return ImageFont.truetype(path, size)
            elif not bold and "Bold" not in path:
                return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


TITLE_FONT = get_font(48, bold=True)
HEADER_FONT = get_font(36, bold=True)
SUBHEADER_FONT = get_font(28, bold=True)
BODY_FONT = get_font(22, bold=False)
CODE_FONT = get_font(18, bold=False)


def wrap_text_lines(text, font, max_width):
    """Wrap text to fit within max_width pixels"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def create_insta_canvas():
    """Create a blank Instagram-sized canvas"""
    img = Image.new('RGB', (INSTA_WIDTH, INSTA_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Top accent bar
    draw.rectangle([(0, 0), (INSTA_WIDTH, 8)], fill=ACCENT_COLOR)

    return img, draw


def add_footer(draw, page_num=0, total_pages=0):
    """Add footer with page number"""
    y = INSTA_HEIGHT - 60
    draw.rectangle([(MARGIN, y), (INSTA_WIDTH - MARGIN, y + 4)], fill=ACCENT_COLOR)

    if page_num > 0 and total_pages > 0:
        text = f"Page {page_num} of {total_pages}"
        bbox = BODY_FONT.getbbox(text)
        text_width = bbox[2] - bbox[0]
        x = (INSTA_WIDTH - text_width) // 2
        draw.text((x, y + 15), text, fill=MUTED_COLOR, font=BODY_FONT)
    else:
        draw.text((MARGIN, y + 15), "Generated content", fill=MUTED_COLOR, font=BODY_FONT)


def convert_pdf_to_instagram(pdf_path, output_dir, dpi=150):
    """Convert PDF pages to Instagram-sized images"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Converting PDF: {pdf_path.name}")

    try:
        images = convert_from_path(str(pdf_path), dpi=dpi)
        converted = []

        for i, img in enumerate(images, 1):
            orig_width, orig_height = img.size

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Calculate scaling to fit Instagram with padding
            if orig_width > orig_height:
                scale = INSTA_WIDTH / orig_width
                new_width = INSTA_WIDTH
                new_height = int(orig_height * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                padding = (INSTA_HEIGHT - new_height) // 2

                img_bordered = Image.new("RGB", (INSTA_WIDTH, INSTA_HEIGHT), (255, 255, 255))
                img_bordered.paste(img_resized, (0, padding))
            else:
                scale = INSTA_HEIGHT / orig_height
                new_height = INSTA_HEIGHT
                new_width = int(orig_width * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                padding = (INSTA_WIDTH - new_width) // 2

                img_bordered = Image.new("RGB", (INSTA_WIDTH, INSTA_HEIGHT), (255, 255, 255))
                img_bordered.paste(img_resized, (padding, 0))

            output_name = f"{pdf_path.stem}_page_{i:03d}.jpg"
            output_path = output_dir / output_name
            img_bordered.save(output_path, "JPEG", quality=95)

            converted.append(output_path)
            print(f"  -> {output_name} ({orig_width}x{orig_height} -> 1080x1350)")

        return converted

    except Exception as e:
        print(f"Error converting PDF: {e}")
        return []


def parse_markdown_content(md_path):
    """Parse markdown file into structured content blocks"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = []
    lines = content.split('\n')

    current_code_block = []
    in_code_block = False
    in_list = False
    list_items = []

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                blocks.append(('code', '\n'.join(current_code_block)))
                current_code_block = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            current_code_block.append(line)
            continue

        # Headers
        if line.startswith('# '):
            if list_items:
                blocks.append(('list', list_items))
                list_items = []
            blocks.append(('title', line[2:].strip()))
            continue
        elif line.startswith('## '):
            if list_items:
                blocks.append(('list', list_items))
                list_items = []
            blocks.append(('header', line[3:].strip()))
            continue
        elif line.startswith('### '):
            if list_items:
                blocks.append(('list', list_items))
                list_items = []
            blocks.append(('subheader', line[4:].strip()))
            continue

        # Lists
        if line.strip().startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', line.strip()):
            in_list = True
            list_items.append(line.strip())
            continue
        elif in_list and line.strip() == '':
            blocks.append(('list', list_items))
            list_items = []
            in_list = False
            continue
        elif not in_list and list_items:
            blocks.append(('list', list_items))
            list_items = []

        # Blockquotes
        if line.strip().startswith('>'):
            if list_items:
                blocks.append(('list', list_items))
                list_items = []
            blocks.append(('quote', line.strip()[1:].strip()))
            continue

        # Horizontal rules
        if line.strip() in ('---', '***', '___'):
            blocks.append(('divider', ''))
            continue

        # Regular paragraphs
        if line.strip():
            if list_items:
                blocks.append(('list', list_items))
                list_items = []
            blocks.append(('paragraph', line.strip()))

    # Catch remaining list
    if list_items:
        blocks.append(('list', list_items))

    return blocks


def render_markdown_block(block_type, content, img, draw, y_pos):
    """Render a markdown block and return new y position"""
    max_text_width = INSTA_WIDTH - (2 * MARGIN)

    if block_type == 'title':
        lines = wrap_text_lines(content, TITLE_FONT, max_text_width)
        draw.rectangle([(MARGIN, y_pos), (INSTA_WIDTH - MARGIN, y_pos + 4)], fill=ACCENT_COLOR)
        y_pos += 20
        for line in lines:
            draw.text((MARGIN, y_pos), line, fill=TEXT_COLOR, font=TITLE_FONT)
            y_pos += 60
        y_pos += 20

    elif block_type == 'header':
        lines = wrap_text_lines(content, HEADER_FONT, max_text_width)
        draw.rectangle([(MARGIN, y_pos), (INSTA_WIDTH - MARGIN, y_pos + 3)], fill=ACCENT_COLOR)
        y_pos += 15
        for line in lines:
            draw.text((MARGIN, y_pos), line, fill=TEXT_COLOR, font=HEADER_FONT)
            y_pos += 45
        y_pos += 15

    elif block_type == 'subheader':
        lines = wrap_text_lines(content, SUBHEADER_FONT, max_text_width)
        for line in lines:
            draw.text((MARGIN + 10, y_pos), f"▸ {line}", fill=TEXT_COLOR, font=SUBHEADER_FONT)
            y_pos += 35
        y_pos += 10

    elif block_type == 'paragraph':
        lines = wrap_text_lines(content, BODY_FONT, max_text_width)
        for line in lines:
            draw.text((MARGIN, y_pos), line, fill=TEXT_COLOR, font=BODY_FONT)
            y_pos += 28
        y_pos += 15

    elif block_type == 'quote':
        # Quote box
        quote_lines = wrap_text_lines(content, BODY_FONT, max_text_width - 40)
        box_height = len(quote_lines) * 28 + 30
        draw.rectangle([
            (MARGIN + 10, y_pos),
            (INSTA_WIDTH - MARGIN - 10, y_pos + box_height)
        ], fill=(245, 235, 235))
        y_pos += 15
        for line in quote_lines:
            draw.text((MARGIN + 30, y_pos), f'"{line}"', fill=ACCENT_COLOR, font=BODY_FONT)
            y_pos += 28
        y_pos += 15

    elif block_type == 'list':
        for item in content:
            # Remove list marker
            text = re.sub(r'^[\-*+] |\d+\.\s', '', item)
            lines = wrap_text_lines(text, BODY_FONT, max_text_width - 30)
            for line in lines:
                draw.text((MARGIN + 30, y_pos), f"• {line}", fill=TEXT_COLOR, font=BODY_FONT)
                y_pos += 28
        y_pos += 10

    elif block_type == 'code':
        # Code box
        code_lines = content.split('\n')[:8]  # Limit lines
        box_height = len(code_lines) * 22 + 30
        draw.rectangle([
            (MARGIN, y_pos),
            (INSTA_WIDTH - MARGIN, y_pos + box_height)
        ], fill=(40, 40, 45))
        y_pos += 15
        for line in code_lines:
            draw.text((MARGIN + 15, y_pos), line, fill=(200, 200, 200), font=CODE_FONT)
            y_pos += 22
        y_pos += 15

    elif block_type == 'divider':
        y_pos += 10
        draw.rectangle([(MARGIN, y_pos), (INSTA_WIDTH - MARGIN, y_pos + 2)], fill=(200, 200, 200))
        y_pos += 20

    return y_pos


def convert_markdown_to_instagram(md_path, output_dir):
    """Convert markdown file to Instagram-sized images"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"Converting Markdown: {md_path.name}")

    blocks = parse_markdown_content(md_path)

    if not blocks:
        print("  No content found in markdown file")
        return []

    pages = []
    current_blocks = []
    current_page_num = 1

    for block in blocks:
        current_blocks.append(block)

        # Check if we need a new page (simplified check)
        # Estimate height
        estimated_height = sum(estimate_block_height(b) for b in current_blocks) + 100

        if estimated_height > INSTA_HEIGHT - 150:
            # Save current page and start new one
            if current_blocks:
                pages.append(current_blocks.copy())
                current_blocks = [block]

    # Add last page
    if current_blocks:
        pages.append(current_blocks)

    # Render pages
    converted = []
    for i, page_blocks in enumerate(pages, 1):
        img, draw = create_insta_canvas()
        y_pos = 80  # Start after top margin

        for block_type, content in page_blocks:
            y_pos = render_markdown_block(block_type, content, img, draw, y_pos)

            if y_pos > INSTA_HEIGHT - 100:
                # Skip remaining content that doesn't fit
                break

        add_footer(draw, i, len(pages))

        output_name = f"{md_path.stem}_page_{i:03d}.jpg"
        output_path = output_dir / output_name
        img.save(output_path, "JPEG", quality=95)

        converted.append(output_path)
        print(f"  -> {output_name}")

    return converted


def estimate_block_height(block):
    """Estimate height needed for a block"""
    block_type, content = block

    if block_type == 'title':
        return 80
    elif block_type == 'header':
        return 60
    elif block_type == 'subheader':
        return 45
    elif block_type == 'paragraph':
        lines = wrap_text_lines(content, BODY_FONT, INSTA_WIDTH - 2 * MARGIN)
        return len(lines) * 28 + 15
    elif block_type == 'quote':
        return 80
    elif block_type == 'list':
        return len(content) * 28 + 10
    elif block_type == 'code':
        return min(len(content.split('\n')) * 22 + 30, 200)
    elif block_type == 'divider':
        return 30
    return 50


def main():
    parser = argparse.ArgumentParser(
        description='Convert PDF or Markdown files to Instagram-ready images'
    )
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', '-o', default='./instagram_output',
                        help='Output directory (default: ./instagram_output)')
    parser.add_argument('--dir', '-d', action='store_true',
                        help='Treat input as directory')
    parser.add_argument('--dpi', type=int, default=150,
                        help='DPI for PDF conversion (default: 150)')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)

    all_converted = []

    if args.dir or input_path.is_dir():
        # Process directory
        for file_path in input_path.glob('*'):
            if file_path.suffix.lower() == '.pdf':
                all_converted.extend(convert_pdf_to_instagram(file_path, output_dir, args.dpi))
            elif file_path.suffix.lower() in ('.md', '.markdown'):
                all_converted.extend(convert_markdown_to_instagram(file_path, output_dir))

    elif input_path.suffix.lower() == '.pdf':
        all_converted.extend(convert_pdf_to_instagram(input_path, output_dir, args.dpi))

    elif input_path.suffix.lower() in ('.md', '.markdown'):
        all_converted.extend(convert_markdown_to_instagram(input_path, output_dir))

    else:
        print(f"Error: Unsupported file type: {input_path.suffix}")
        print("Supported types: .pdf, .md, .markdown")
        sys.exit(1)

    print(f"\nComplete! {len(all_converted)} images saved to {output_dir}")


if __name__ == '__main__':
    main()
