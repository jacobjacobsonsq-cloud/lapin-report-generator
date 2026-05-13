# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

datas = [('app.py', '.'), ('src', 'src'), ('assets', 'assets')]
binaries = []
hiddenimports = ['streamlit', 'streamlit.web.cli', 'streamlit.runtime.scriptrunner', 'pandas', 'openpyxl', 'matplotlib', 'matplotlib.backends.backend_agg', 'pptx', 'pptx.util', 'pptx.dml.color', 'pptx.enum.text', 'PIL', 'numpy']
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

target_arch = os.environ.get("PYI_TARGET_ARCH")
if target_arch == "":
    target_arch = None

bundle_identifier = os.environ.get(
    "PYI_BUNDLE_ID",
    "com.calebgoodman.lapin-report-generator",
)


a = Analysis(
    ['launch.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Lapin Report Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=target_arch,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Lapin Report Generator',
)
app = BUNDLE(
    coll,
    name='Lapin Report Generator.app',
    icon=None,
    bundle_identifier=bundle_identifier,
)
