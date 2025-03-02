"""Create a test image with text for OCR testing."""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def create_test_image(output_dir: Path, filename: str = 'test_image.jpg'):
    """Create a test image with text for OCR testing."""
    # Create an image with white background
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Try to use a built-in font, fall back to default if not available
    try:
        # Try common fonts that might be available
        font_paths = [
            '/Library/Fonts/Arial.ttf',  # macOS
            '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Linux
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
        ]

        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 24)
                break

        if font is None:
            # Use default font if no specific font is available
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Add text to the image
    text = (
        'This is a test image for OCR\n\n'
        'It contains text that should be recognized by the OCR engine.\n\n'
        'The ImageParser should extract this text from the image.\n\n'
        '這是用於中文OCR測試的文字'
    )

    # Add text with black color
    d.text((50, 50), text, fill=(0, 0, 0), font=font)

    # Save the image
    output_path = output_dir / filename
    img.save(output_path)

    print(f'Created test image: {output_path}')
    return output_path


if __name__ == '__main__':
    # Create test image in the sample files directory
    sample_dir = Path(__file__).parents[1] / 'tests' / 'sample_files'
    sample_dir.mkdir(parents=True, exist_ok=True)

    create_test_image(sample_dir)
