from PIL import Image
import os

grphics_dir = "grphics"
imgs = [f for f in os.listdir(grphics_dir) if f.endswith('.png')]
for img in imgs:
    path = os.path.join(grphics_dir, img)
    try:
        with Image.open(path) as i:
            print(f"{img}: {i.size} ({os.path.getsize(path)/1024/1024:.2f} MB)")
    except Exception as e:
        print(f"Error reading {img}: {e}")
