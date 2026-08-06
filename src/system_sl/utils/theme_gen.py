import os
import io
import re
import colorsys
from colorthief import ColorThief
from PIL import Image

DEFAULT_TOKENS = {
    "sys_color_background": "#060912",
    "sys_color_surface": "#0b0f1a",
    "sys_color_surface_raised": "#0e1626",
    "sys_color_border": "#1f6f99",
    "sys_color_border_muted": "#1a2638",
    "sys_color_primary": "#00d9ff",
    "sys_color_primary_light": "#67e8ff",
    "sys_color_primary_dim": "rgba(0, 217, 255, 0.08)",
    "sys_color_primary_hover": "rgba(0, 217, 255, 0.18)",
    "sys_color_primary_pressed": "rgba(0, 217, 255, 0.30)",
    "sys_color_text_main": "#d6e7ff",
    "sys_color_text_secondary": "#b3d4ff",
    "sys_color_text_highlight": "#b6f1ff",
    "sys_color_text_muted": "#3d4d68"
}

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif",
              ".tif", ".tiff", ".avif", ".jxl")

def rgb_to_hex(rgb_tuple):
    r, g, b = [int(x * 255) for x in rgb_tuple]
    return f"#{r:02x}{g:02x}{b:02x}"

def _pick_largest(files):
    """Return the highest-resolution file based on the WxH in its name."""
    best, best_area = None, -1
    for f in files:
        area = 0
        m = re.search(r"(\d+)[xX](\d+)", os.path.splitext(os.path.basename(f))[0])
        if m:
            area = int(m.group(1)) * int(m.group(2))
        if area > best_area:
            best, best_area = f, area
    return best if best is not None else (files[0] if files else None)

def resolve_wallpaper_path(path):
    """Turn a wallpaper path (file or KDE collection directory) into an image file."""
    if not path:
        return None
    path = os.path.expanduser(path)
    if os.path.isfile(path):
        return path
    if not os.path.isdir(path):
        return None
    # KDE wallpaper package layout: contents/images or contents/images_dark
    for sub in ("contents/images_dark", "contents/images"):
        d = os.path.join(path, sub)
        if os.path.isdir(d):
            candidates = [os.path.join(d, n) for n in sorted(os.listdir(d))
                          if n.lower().endswith(IMAGE_EXTS)]
            if candidates:
                return _pick_largest(candidates)
    candidates = []
    for root, _, files in os.walk(path):
        for n in sorted(files):
            if n.lower().endswith(IMAGE_EXTS):
                candidates.append(os.path.join(root, n))
    return _pick_largest(candidates) if candidates else None

def _open_image(path):
    """Open an image, decoding JPEG XL (Fedora stock wallpapers) via imagecodecs."""
    try:
        return Image.open(path)
    except Exception:
        if path.lower().endswith(".jxl"):
            from imagecodecs import jpegxl_decode
            with open(path, "rb") as f:
                arr = jpegxl_decode(f.read())
            if arr.ndim == 3 and arr.shape[2] == 4:
                return Image.fromarray(arr, "RGBA")
            if arr.ndim == 3 and arr.shape[2] == 3:
                return Image.fromarray(arr, "RGB")
            return Image.fromarray(arr)
        raise

# CHANGED: Accept wallpaper_path as an argument!
def generate_dynamic_tokens(wallpaper_path): 
    resolved = resolve_wallpaper_path(wallpaper_path)
    if not resolved:
        return DEFAULT_TOKENS

    try:
        # OPTIMIZATION: Hold the tiny thumbnail in RAM (io.BytesIO) 
        # instead of writing to the hard drive. 100% Cross-platform!
        with _open_image(resolved) as img:
            img.thumbnail((150, 150))
            img = img.convert("RGB")
            
            # Save to memory buffer
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)

        # 1. Extract the dominant color from the memory buffer
        color_thief = ColorThief(img_byte_arr)
        r_raw, g_raw, b_raw = color_thief.get_color(quality=1)
        
        # 2. Convert raw RGB to HSV space for manipulation
        h, s, v = colorsys.rgb_to_hsv(r_raw / 255.0, g_raw / 255.0, b_raw / 255.0)
        
        # 3. MATHEMATICAL CLAMPING (Enforcing the dark aesthetic)
        accent_rgb = colorsys.hsv_to_rgb(h, max(s, 0.8), 1.0)
        accent_light_rgb = colorsys.hsv_to_rgb(h, max(s, 0.6), 1.0)
        bg_rgb = colorsys.hsv_to_rgb(h, 0.20, 0.04)
        surface_rgb = colorsys.hsv_to_rgb(h, 0.25, 0.08)
        surface_raised_rgb = colorsys.hsv_to_rgb(h, 0.25, 0.09)
        border_rgb = colorsys.hsv_to_rgb(h, 0.60, 0.40)
        
        r_int, g_int, b_int = [int(x * 255) for x in accent_rgb]

        return {
            "sys_color_background": rgb_to_hex(bg_rgb),
            "sys_color_surface": rgb_to_hex(surface_rgb),
            "sys_color_surface_raised": rgb_to_hex(surface_raised_rgb),
            "sys_color_border": rgb_to_hex(border_rgb),
            "sys_color_border_muted": rgb_to_hex(colorsys.hsv_to_rgb(h, 0.20, 0.15)),
            "sys_color_primary": rgb_to_hex(accent_rgb),
            "sys_color_primary_light": rgb_to_hex(accent_light_rgb),
            "sys_color_primary_dim": f"rgba({r_int}, {g_int}, {b_int}, 0.08)",
            "sys_color_primary_hover": f"rgba({r_int}, {g_int}, {b_int}, 0.18)",
            "sys_color_primary_pressed": f"rgba({r_int}, {g_int}, {b_int}, 0.30)",
            "sys_color_text_main": "#ffffff",
            "sys_color_text_secondary": "#b3d4ff",
            "sys_color_text_highlight": "#ffffff",
            "sys_color_text_muted": "#6a7b9c"
        }
    except Exception as e:
        print(f"Theme extraction failed: {e}")
        return DEFAULT_TOKENS
