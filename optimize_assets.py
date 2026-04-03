from PIL import Image
import os
import shutil

grphics_dir = "grphics"
backup_dir = "grphics_backup"

if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

imgs = [f for f in os.listdir(grphics_dir) if f.endswith('.png')]

for img in imgs:
    src = os.path.join(grphics_dir, img)
    backup = os.path.join(backup_dir, img)
    
    # Back up first
    shutil.copy2(src, backup)
    
    try:
        with Image.open(src) as i:
            # We preserve the original PNG format but use Pillow's optimization
            # For backgrounds, we might even convert to RGB if no alpha is needed to save more
            original_size = os.path.getsize(src)
            
            # If it's a large background or crop photo, we can use adaptive quantization
            if i.mode in ("RGBA", "P"):
                i = i.convert("RGBA")
                i.save(src, "PNG", optimize=True)
            else:
                i.save(src, "PNG", optimize=True)
                
            new_size = os.path.getsize(src)
            print(f"Optimized {img}: {original_size/1024:.1f}KB -> {new_size/1024:.1f}KB")
    except Exception as e:
        print(f"Failed to optimize {img}: {e}")
