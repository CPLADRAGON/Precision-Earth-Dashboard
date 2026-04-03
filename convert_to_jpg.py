from PIL import Image
import os

grphics_dir = "grphics"
# Large photos to convert to JPEG (photos/backgrounds)
to_convert = [
    "bg_day.png", "bg_night.png", "enter_overlay.png",
    "healthy_crop.png", "dry_corp.png", "dryingtodie_crop.png",
    "pH Imbalance.png", "salty_stressed.png"
]

for img_name in to_convert:
    src = os.path.join(grphics_dir, img_name)
    if os.path.exists(src):
        try:
            with Image.open(src) as i:
                # Convert RGBA to RGB (strip transparency for backgrounds/photos)
                rgb_img = i.convert("RGB")
                target_name = img_name.replace(".png", ".jpg")
                target_path = os.path.join(grphics_dir, target_name)
                # High quality (85) gives great results with tiny file sizes
                rgb_img.save(target_path, "JPEG", quality=85, optimize=True)
                
                old_size = os.path.getsize(src)
                new_size = os.path.getsize(target_path)
                print(f"Converted {img_name} to JPEG: {old_size/1024:.1f}KB -> {new_size/1024:.1f}KB")
        except Exception as e:
            print(f"Failed to convert {img_name}: {e}")
