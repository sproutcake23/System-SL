#!/bin/bash
# uninstall.sh - Remove system-sl AppImage and all desktop integration
# Usage: ./uninstall.sh [--keep-data]

set -e

APPIMAGE_NAME="system-sl.AppImage"
EXEC_NAME="system-sl"

INSTALL_DIR="$HOME/.local/bin"
APPMEN_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
CONFIG_DIR="$HOME/.config/system-sl"

# Parse arguments
KEEP_DATA=false
for arg in "$@"; do
    case $arg in
        --keep-data)
            KEEP_DATA=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./uninstall.sh [--keep-data]"
            echo ""
            echo "Options:"
            echo "  --keep-data    Keep configuration data in ~/.config/system-sl/"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
    esac
done

echo "⚔️  THE SYSTEM - Uninstaller"
echo "==========================="
echo ""

# Remove AppImage
if [ -f "$INSTALL_DIR/$APPIMAGE_NAME" ]; then
    echo "🗑  Removing AppImage: $INSTALL_DIR/$APPIMAGE_NAME"
    rm -f "$INSTALL_DIR/$APPIMAGE_NAME"
else
    echo "   AppImage not found at $INSTALL_DIR (skipped)"
fi

# Remove launcher .desktop file
if [ -f "$APPMEN_DIR/$EXEC_NAME.desktop" ]; then
    echo "🗑  Removing launcher: $APPMEN_DIR/$EXEC_NAME.desktop"
    rm -f "$APPMEN_DIR/$EXEC_NAME.desktop"
else
    echo "   Launcher .desktop not found (skipped)"
fi

# Remove autostart .desktop file
if [ -f "$AUTOSTART_DIR/$EXEC_NAME.desktop" ]; then
    echo "🗑  Removing autostart: $AUTOSTART_DIR/$EXEC_NAME.desktop"
    rm -f "$AUTOSTART_DIR/$EXEC_NAME.desktop"
else
    echo "   Autostart .desktop not found (skipped)"
fi

# Remove config directory (optional)
if [ "$KEEP_DATA" = false ] && [ -d "$CONFIG_DIR" ]; then
    echo "🗑  Removing config: $CONFIG_DIR"
    rm -rf "$CONFIG_DIR"
else
    echo "   Config directory kept at $CONFIG_DIR"
fi

echo ""
echo "✅ UNINSTALL COMPLETE"
echo ""
echo "Removed:"
echo "  • AppImage binary"
echo "  • Application launcher shortcut"
echo "  • Autostart entry"
if [ "$KEEP_DATA" = false ]; then
    echo "  • Configuration data"
else
    echo ""
    echo "Note: Configuration data preserved at $CONFIG_DIR"
    echo "To remove manually: rm -rf $CONFIG_DIR"
fi
