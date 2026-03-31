#!/bin/bash
# Build PatOpenCV → PatOpenCV.app (macOS)
set -e

echo "=== PatOpenCV Build (macOS) ==="

pip install pyinstaller --quiet
rm -rf build/ dist/

pyinstaller PatOpenCV.spec

echo ""
echo "✓ dist/PatOpenCV.app  → double-clic pour lancer"
echo "  Pour distribuer : zip -r PatOpenCV-mac.zip dist/PatOpenCV.app"
