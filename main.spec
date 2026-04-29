# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('view/main_screen.kv', 'view'),
        ('assets', 'assets'),
        ('models', 'models'),
        (
            r'C:\Users\Win11\AppData\Roaming\Python\Python313\site-packages\clip\bpe_simple_vocab_16e6.txt.gz',
            'clip'
        ),
        (
            r'C:\Users\Win11\AppData\Roaming\Python\Python313\site-packages\en_core_web_sm\en_core_web_sm-3.8.0',
            'en_core_web_sm'
        ),
        (
            r'C:\Users\Win11\AppData\Roaming\nltk_data',
            'nltk_data'
        )
    ],
    hiddenimports=['win32timezone'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
