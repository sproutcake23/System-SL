#!/bin/bash
# install.sh - Install system-sl AppImage with desktop integration and autostart
# Usage: ./install.sh [--no-autostart]

set -e

APPIMAGE_NAME="system-sl.AppImage"
DISPLAY_NAME="THE SYSTEM"
EXEC_NAME="system-sl"
BG_FLAG="--bg"

INSTALL_DIR="$HOME/.local/bin"
APPMEN_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
ICON_NAME="utilities-terminal"

# Parse arguments
DISABLE_AUTOSTART=false
for arg in "$@"; do
    case $arg in
        --no-autostart)
            DISABLE_AUTOSTART=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./install.sh [--no-autostart]"
            echo ""
            echo "Options:"
            echo "  --no-autostart    Skip creating autostart entry"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
    esac
done

echo "⚔️  THE SYSTEM - Installer"
echo "========================="
echo ""

# Find the AppImage
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPIMAGE_PATH=""

# Search locations in order
SEARCH_DIRS=(
    "$SCRIPT_DIR"
    "$(pwd)"
    "$HOME/Downloads"
    "$HOME/Desktop"
)

for dir in "${SEARCH_DIRS[@]}"; do
    if [ -f "$dir/$APPIMAGE_NAME" ]; then
        APPIMAGE_PATH="$dir/$APPIMAGE_NAME"
        break
    fi
done

if [ -z "$APPIMAGE_PATH" ]; then
    echo "❌ Error: $APPIMAGE_NAME not found!"
    echo ""
    echo "Searched in:"
    for dir in "${SEARCH_DIRS[@]}"; do
        echo "  - $dir"
    done
    echo ""
    echo "Please place $APPIMAGE_NAME in one of these locations and run this script again."
    exit 1
fi

echo "📦 Found AppImage: $APPIMAGE_PATH"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$APPMEN_DIR"
mkdir -p "$AUTOSTART_DIR"

# Copy AppImage to install location
echo "🚚 Installing to $INSTALL_DIR/$APPIMAGE_NAME..."
cp "$APPIMAGE_PATH" "$INSTALL_DIR/$APPIMAGE_NAME"
chmod +x "$INSTALL_DIR/$APPIMAGE_NAME"

# Create .desktop file for app launcher
echo "🔗 Creating launcher shortcut..."
DESKTOP_FILE="$APPMEN_DIR/$EXEC_NAME.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=$DISPLAY_NAME
Exec=$INSTALL_DIR/$APPIMAGE_NAME
Path=$INSTALL_DIR
Terminal=false
Icon=$ICON_NAME
Categories=Utility;Development;
Comment=A Solo Leveling-inspired task management system.
StartupNotify=true
EOF
chmod +x "$DESKTOP_FILE"

# Create autostart .desktop file
if [ "$DISABLE_AUTOSTART" = false ]; then
    echo "🔄 Creating autostart entry..."
    AUTOSTART_FILE="$AUTOSTART_DIR/$EXEC_NAME.desktop"
    cat > "$AUTOSTART_FILE" << EOF
[Desktop Entry]
Type=Application
Name=$DISPLAY_NAME
Exec=/bin/sh -c 'DISPLAY=\${DISPLAY:-:0} DBUS_SESSION_BUS_ADDRESS=\${DBUS_SESSION_BUS_ADDRESS:-} $INSTALL_DIR/$APPIMAGE_NAME $BG_FLAG'
Path=$INSTALL_DIR
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=A Solo Leveling-inspired task management system.
EOF
    chmod +x "$AUTOSTART_FILE"
    echo "   ✓ Autostart enabled (runs on login with --bg flag)"
else
    echo "   ⏭ Skipping autostart (--no-autostart flag provided)"
fi

echo ""
echo "✅ INSTALLATION COMPLETE"
echo ""
echo "You can now:"
echo "  • Find '$DISPLAY_NAME' in your application menu"
echo "  • Run directly: $INSTALL_DIR/$APPIMAGE_NAME"
if [ "$DISABLE_AUTOSTART" = false ]; then
    echo "  • App will start automatically on login"
fi
echo ""
echo "To uninstall: ./uninstall.sh"
