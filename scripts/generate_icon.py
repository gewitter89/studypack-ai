import os
from PIL import Image

def generate_ico():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    png_path = os.path.join(current_dir, "assets", "logo.png")
    ico_path = os.path.join(current_dir, "assets", "icon.ico")
    
    if not os.path.exists(png_path):
        print(f"Error: logo.png not found at {png_path}")
        return False
        
    print(f"Converting {png_path} to multi-resolution Windows ICO...")
    try:
        img = Image.open(png_path)
        # Standard sizes for Windows executable icons
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        img.save(ico_path, format="ICO", sizes=sizes)
        print(f"Successfully generated icon at {ico_path}")
        return True
    except Exception as e:
        print(f"Failed to generate icon: {e}")
        return False

if __name__ == "__main__":
    generate_ico()
