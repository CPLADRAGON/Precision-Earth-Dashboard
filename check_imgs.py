from PIL import Image
import os

grphics_dir = os.path.join("c:", "Users", "wangbo", "Desktop", "Work", "EE4409", "CA2", "grphics")
imgs = [f for f in os.listdir(grphics_dir) if f.endswith('.png')]
for img in imgs:
    path = os.path.join(grphics_dir, img)
    try:
        with Image.open(path) as i:
            print(f"{img}: {i.size} ({os.path.getsize(path)/1024/1024:.2f} MB)")
    except:
        pass
