# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file — PatOpenCV (macOS + Windows)
# Usage:
#   macOS   → bash build.sh
#   Windows → build.bat

import sys as _sys
from PyInstaller.utils.hooks import collect_dynamic_libs

IS_MACOS   = (_sys.platform == "darwin")
IS_WINDOWS = (_sys.platform == "win32")

# ── Données à bundler ────────────────────────────────────────────────────────
datas = [
    ("patHand.gif",          "."),
    ("ultra_light_320.onnx", "."),
    ("lbfmodel.yaml",        "."),
]

# ── Librairies natives ────────────────────────────────────────────────────────
binaries = collect_dynamic_libs("onnxruntime")

# ── Imports cachés ────────────────────────────────────────────────────────────
hiddenimports = [
    "cv2",
    "cv2.face",
    "onnxruntime",
    "onnxruntime.capi",
    "PIL",
    "PIL.Image",
    "numpy",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
]

# ── Analyse ───────────────────────────────────────────────────────────────────
a = Analysis(
    ["gui.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ── Exécutable ────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PatOpenCV",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Pas de fenêtre terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    # Icône : .ico pour Windows, .icns pour macOS
    icon="icon.ico" if IS_WINDOWS else ("icon.icns" if IS_MACOS else None),
    codesign_identity=None,
    entitlements_file="entitlements.plist" if IS_MACOS else None,
)

# ── Bundle macOS (.app) ───────────────────────────────────────────────────────
if IS_MACOS:
    app = BUNDLE(
        exe,
        name="PatOpenCV.app",
        icon="icon.icns" if __import__("os").path.exists("icon.icns") else None,
        bundle_identifier="com.patopenCV.app",
        info_plist={
            "NSCameraUsageDescription": "PatOpenCV nécessite l'accès à la webcam.",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
        },
    )
