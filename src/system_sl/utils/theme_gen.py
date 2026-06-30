import os
import colorsys
from system_sl.utils import get_wallpaper_path
from colorthief import ColorThief
from PIL import Image

DEFAULT_TOKENS = {
    "sys_color_background":"#060912",
    "sys_color_surface": "#0b0f1a",
    "sys_color_primary": "#00d9ff",
    "sys_color_text_main": "#d6e7ff",
    "sys_color_border": "#1f6f99"
}

def rgb_to_hex(rgb_tuple):
    r,g,b = [int(x * 255) for x in rgb_tuple]
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_dynamic_tokens():
    wallpaper_path = get_wallpaper_path
    if not wallpaper_path or not os.path.exists(wallpaper_path):
        return DEFAULT_TOKENS

    try:
        # OPTIMIZATION: Don't run ColorThief on a 4K image. 
        # Downscale it to a tiny thumbnail first so it processes in milliseconds.
        temp_thumb = "/tmp/system_sl_thumb.jpg"
        with Image.open(wallpaper_path) as img:
            img.thumbnail((150, 150))
            img.convert("RGB").save(temp_thumb)

        # 1. Extract the dominant color
        color_thief = ColorThief(temp_thumb)
        r_raw, g_raw, b_raw = color_thief.get_color(quality=1)
        
        # 2. Convert raw RGB to HSV space for manipulation
        h, s, v = colorsys.rgb_to_hsv(r_raw / 255.0, g_raw / 255.0, b_raw / 255.0)
        
        # 3. MATHEMATICAL CLAMPING (Enforcing the dark aesthetic)
        # Accent: Keep the hue, but force max brightness (1.0) and high saturation (0.8)
        accent_rgb = colorsys.hsv_to_rgb(h, max(s, 0.8), 1.0)
        
        # Background: Keep the hue, but force it to be extremely dark (0.04 brightness)
        bg_rgb = colorsys.hsv_to_rgb(h, 0.20, 0.04)
        
        # Surface (Panels/Lists): Slightly lighter than the background
        surface_rgb = colorsys.hsv_to_rgb(h, 0.25, 0.08)
        
        # Border: Mid-tone of the same hue
        border_rgb = colorsys.hsv_to_rgb(h, 0.60, 0.40)

        return {
            "sys_color_background": rgb_to_hex(bg_rgb),
            "sys_color_surface": rgb_to_hex(surface_rgb),
            "sys_color_primary": rgb_to_hex(accent_rgb),
            "sys_color_text_main": "#ffffff", # Always white for contrast
            "sys_color_border": rgb_to_hex(border_rgb)
        }
    except Exception as e:
        print(f"Theme extraction failed: {e}")
        return DEFAULT_TOKENS