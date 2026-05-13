#!/bin/bash
# =============================================================================
# Build Mac .app bundle for Lapin Report Generator
# Usage:
#   bash build_app.sh
# Optional env:
#   TARGET_ARCH=arm64|x86_64|universal2
#   BUNDLE_ID=com.example.app
# =============================================================================

set -e

echo "============================================"
echo "Building Lapin Report Generator Mac App"
echo "============================================"

TARGET_ARCH="${TARGET_ARCH:-$(uname -m)}"
BUNDLE_ID="${BUNDLE_ID:-com.calebgoodman.lapin-report-generator}"

echo "Target arch: ${TARGET_ARCH}"
echo "Bundle ID:   ${BUNDLE_ID}"
echo ""

HOST_ARCH="$(uname -m)"
if [[ "${TARGET_ARCH}" != "${HOST_ARCH}" && "${TARGET_ARCH}" != "universal2" ]]; then
  echo "NOTE: Host arch is ${HOST_ARCH} but target is ${TARGET_ARCH}."
  echo "      Cross-arch builds require a Python/dependency environment that supports ${TARGET_ARCH}."
  echo ""
fi

if [[ ! -f "Lapin Report Generator.spec" ]]; then
  echo "ERROR: Missing spec file: Lapin Report Generator.spec"
  exit 1
fi

if [[ -x "./venv/bin/pyinstaller" ]]; then
  PYINSTALLER_CMD="./venv/bin/pyinstaller"
elif command -v pyinstaller >/dev/null 2>&1; then
  PYINSTALLER_CMD="pyinstaller"
else
  echo "ERROR: PyInstaller not found. Install it in venv or globally."
  exit 1
fi

# Clean previous builds
rm -rf build/ dist/

echo "Packaging with PyInstaller..."

export PYI_TARGET_ARCH="${TARGET_ARCH}"
export PYI_BUNDLE_ID="${BUNDLE_ID}"
export PYINSTALLER_CONFIG_DIR="${PWD}/.pyinstaller-cache"
"${PYINSTALLER_CMD}" --noconfirm --clean "Lapin Report Generator.spec"

echo ""
echo "Binary architecture:"
file "dist/Lapin Report Generator.app/Contents/MacOS/Lapin Report Generator"

echo ""
echo "============================================"
echo "Build complete!"
echo "============================================"
echo ""
echo "Your app is at: dist/Lapin Report Generator.app"
echo ""
echo "To distribute:"
echo "  1. Zip the 'dist/Lapin Report Generator.app' bundle"
echo "  2. Send to the user"
echo "  3. They unzip and double-click the .app"
echo "  4. First time: right-click > Open (to bypass Gatekeeper)"
echo ""
echo "If recipient is on Intel Mac, build with:"
echo "  TARGET_ARCH=x86_64 bash build_app.sh"
echo "  (requires an x86_64-compatible Python dependency environment)"
echo "If recipient is on Apple Silicon, build with:"
echo "  TARGET_ARCH=arm64 bash build_app.sh"
echo ""
