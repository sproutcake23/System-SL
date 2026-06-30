import os
import io
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

def rgb_to_hex(rgb_tuple):
    r, g, b = [int(x * 255) for x in rgb_tuple]
    return f"#{r:02x}{g:02x}{b:02x}"

# CHANGED: Accept wallpaper_path as an argument!
def generate_dynamic_tokens(wallpaper_path): 
    if not wallpaper_path or not os.path.exists(wallpaper_path):
        return DEFAULT_TOKENS

    try:
        # OPTIMIZATION: Hold the tiny thumbnail in RAM (io.BytesIO) 
        # instead of writing to the hard drive. 100% Cross-platform!
        with Image.open(wallpaper_path) as img:
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