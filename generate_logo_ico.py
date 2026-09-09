import os
from PIL import Image, ImageDraw

def create_chalkboard_logo(size=256):
    """
    Renders the iconic green chalkboard logo:
    - Green chalkboard background (#1E8E3E)
    - Gold/yellow outer frame (#F9AB00)
    - White chalk student figure outlines
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Frame Outer Gold Border
    margin = 8
    frame_rect = [margin, margin, size - margin, size - margin]
    border_width = 16
    draw.rounded_rectangle(frame_rect, radius=20, fill="#F9AB00")

    # Chalkboard Green Surface Inside Frame
    inner_rect = [
        margin + border_width,
        margin + border_width,
        size - margin - border_width,
        size - margin - border_width
    ]
    draw.rounded_rectangle(inner_rect, radius=10, fill="#1E8E3E")

    # White Chalk People Figures
    cx = size // 2
    cy = size // 2

    # Center Teacher/Student Head (Circle)
    head_r = 22
    draw.ellipse([cx - head_r, cy - 35 - head_r, cx + head_r, cy - 35 + head_r], fill="#FFFFFF")

    # Center Body (Arc/Trapezoid)
    body_left = cx - 36
    body_right = cx + 36
    body_top = cy - 5
    body_bottom = cy + 45
    draw.pieslice([body_left, body_top, body_right, body_bottom + 20], start=180, end=360, fill="#FFFFFF")

    # Left Student Head
    draw.ellipse([cx - 65 - 14, cy - 20 - 14, cx - 65 + 14, cy - 20 + 14], fill=(255, 255, 255, 220))
    # Left Body
    draw.pieslice([cx - 90, cy + 5, cx - 40, cy + 55], start=180, end=360, fill=(255, 255, 255, 220))

    # Right Student Head
    draw.ellipse([cx + 65 - 14, cy - 20 - 14, cx + 65 + 14, cy - 20 + 14], fill=(255, 255, 255, 220))
    # Right Body
    draw.pieslice([cx + 40, cy + 5, cx + 90, cy + 55], start=180, end=360, fill=(255, 255, 255, 220))

    # Chalk Ledge line at bottom right
    draw.rectangle([cx + 25, cy + 60, cx + 70, cy + 66], fill="#FFFFFF")

    return img

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_img_dir = os.path.join(base_dir, "static", "images")
    os.makedirs(static_img_dir, exist_ok=True)

    img = create_chalkboard_logo(256)
    
    png_path = os.path.join(static_img_dir, "logo.png")
    ico_path = os.path.join(static_img_dir, "logo.ico")
    root_ico_path = os.path.join(base_dir, "logo.ico")

    img.save(png_path, format="PNG")
    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    img.save(root_ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    print(f"Generated logo images successfully:\n - {png_path}\n - {ico_path}\n - {root_ico_path}")

if __name__ == "__main__":
    main()
