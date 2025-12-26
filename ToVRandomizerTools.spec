# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += collect_data_files('odfdo')
datas += copy_metadata('odfdo')


patcher_a = Analysis(
    ['ToVPatcher.py'],
    pathex=['.venv/lib'],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
patcher_pyz = PYZ(patcher_a.pure)

patcher_exe = EXE(
    patcher_pyz,
    patcher_a.scripts,
    [],
    exclude_binaries=True,
    name='ToVPatcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

rando_a = Analysis(
    ['ToVBasicRandomizer.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
rando_pyz = PYZ(rando_a.pure)

rando_exe = EXE(
    rando_pyz,
    rando_a.scripts,
    [],
    exclude_binaries=True,
    name='ToVBasicRandomizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    patcher_exe,
    patcher_a.binaries,
    patcher_a.datas,
    rando_exe,
    rando_a.binaries,
    rando_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ToVRandomizerTools',
)
