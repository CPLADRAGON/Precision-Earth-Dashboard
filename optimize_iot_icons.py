from PIL import Image
import os

iot_dir = os.path.join("grphics", "iot_devices")
files = [f for f in os.listdir(iot_dir) if f.endswith(".png")]

for f in files:
    src = os.path.join(iot_dir, f)
    try:
        with Image.open(src) as i:
            # Icons are displayed at 70px. We'll save them at 200px for high-DPI quality.
            i = i.convert("RGB")
            i.thumbnail((200, 200))
            target = os.path.join(iot_dir, f.replace(".png", ".jpg"))
            # Fast, high-quality JPEG
            i.save(target, "JPEG", quality=85, optimize=True)
            print(f"Optimized Icon {f}: {os.path.getsize(src)/1024:.1f}KB -> {os.path.getsize(target)/1024:.1f}KB")
    except Exception as e:
        print(f"Failed to optimize {f}: {e}")
