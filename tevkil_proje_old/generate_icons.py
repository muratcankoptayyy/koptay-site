"""
PWA Icon Generator
Generates all required icon sizes for PWA
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Icon sizes needed for PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Create icons directory if not exists
icons_dir = os.path.join('static', 'icons')
os.makedirs(icons_dir, exist_ok=True)

def create_icon(size):
    """Create a simple icon with Tevkil logo"""
    # Create image with blue background
    img = Image.new('RGB', (size, size), color='#3B82F6')
    draw = ImageDraw.Draw(img)
    
    # Calculate sizes
    padding = size // 10
    rect_size = size - (2 * padding)
    
    # Draw white rounded rectangle (simulating logo)
    draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding],
        radius=size // 8,
        fill='white'
    )
    
    # Draw blue "T" in the center
    try:
        # Try to use a font
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "T" letter
    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - padding // 2
    
    draw.text((text_x, text_y), text, fill='#3B82F6', font=font)
    
    # Save icon
    filename = f'icon-{size}x{size}.png'
    filepath = os.path.join(icons_dir, filename)
    img.save(filepath, 'PNG', optimize=True)
    print(f'✅ Created {filename}')

def main():
    print('🎨 PWA Icon Generator')
    print('=' * 50)
    
    for size in ICON_SIZES:
        create_icon(size)
    
    print('=' * 50)
    print(f'✅ Generated {len(ICON_SIZES)} icons successfully!')
    print(f'📁 Location: {os.path.abspath(icons_dir)}')

if __name__ == '__main__':
    main()
