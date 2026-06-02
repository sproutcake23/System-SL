import os
import tomllib

# Update this path to point directly to your specific colors.toml file
THEME_FILE_PATH = os.path.expanduser("~/.config/omarchy/current/theme/colors.toml")

def get_system_colors() -> dict:
    """Reads the custom colors.toml and returns a complete palette map."""
    # Defaults in case of parsing errors
    colors = {
        "bg": "#0b0f1a",
        "bg_dark": "#060912",
        "bg_light": "#0e1626",
        "text": "#d6e7ff",
        "text_light": "#b3d4ff",
        "accent": "#00d9ff",
        "accent_light": "#67e8ff",
        "accent_border": "#1f6f99",
        "accent_dim_06": "rgba(0, 217, 255, 0.06)",
        "accent_dim_08": "rgba(0, 217, 255, 0.08)",
        "accent_dim_18": "rgba(0, 217, 255, 0.18)",
        "accent_dim_20": "rgba(0, 217, 255, 0.20)",
        "accent_dim_22": "rgba(0, 217, 255, 0.22)",
        "accent_dim_30": "rgba(0, 217, 255, 0.30)",
        "accent_dim_32": "rgba(0, 217, 255, 0.32)",
    }

    if os.path.exists(THEME_FILE_PATH):
        try:
            with open(THEME_FILE_PATH, "rb") as f:
                toml_data = tomllib.load(f)
            
            theme_data = toml_data.get("colors", toml_data)
            
            # Map core variants directly from TOML keys
            bg = theme_data.get("background", colors["bg"])
            text = theme_data.get("foreground", colors["text"])
            accent = theme_data.get("color4", theme_data.get("primary", colors["accent"]))
            
            colors["bg"] = bg
            colors["text"] = text
            colors["accent"] = accent
            
            # Build light/dark shifts automatically
            colors["bg_dark"] = bg  # Let Qt styles map natively or darken it if desired
            colors["bg_light"] = theme_data.get("color0", colors["bg_light"])
            colors["text_light"] = text
            colors["accent_light"] = theme_data.get("color12", accent)
            colors["accent_border"] = theme_data.get("color8", colors["accent_border"])
            
            # Generate programmatic RGB opacities
            hex_clean = accent.lstrip("#")
            if len(hex_clean) == 6:
                r = int(hex_clean[0:2], 16)
                g = int(hex_clean[2:4], 16)
                b = int(hex_clean[4:6], 16)
                
                colors["accent_dim_06"] = f"rgba({r}, {g}, {b}, 0.06)"
                colors["accent_dim_08"] = f"rgba({r}, {g}, {b}, 0.08)"
                colors["accent_dim_18"] = f"rgba({r}, {g}, {b}, 0.18)"
                colors["accent_dim_20"] = f"rgba({r}, {g}, {b}, 0.20)"
                colors["accent_dim_22"] = f"rgba({r}, {g}, {b}, 0.22)"
                colors["accent_dim_30"] = f"rgba({r}, {g}, {b}, 0.30)"
                colors["accent_dim_32"] = f"rgba({r}, {g}, {b}, 0.32)"
                
        except Exception as e:
            print(f"Error reading colors.toml: {e}")

    return colors