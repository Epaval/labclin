# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = (
    collect_submodules('apps')
    + collect_submodules('config')
    + collect_submodules('django.contrib.admin')
    + collect_submodules('django.contrib.auth')
    + collect_submodules('django.contrib.contenttypes')
    + collect_submodules('django.contrib.sessions')
    + collect_submodules('django.contrib.messages')
    + collect_submodules('django.contrib.staticfiles')
    + collect_submodules('django.middleware')
    + collect_submodules('django.db.backends.sqlite3')
    + collect_submodules('django.core.management.commands')
    + collect_submodules('axes')
    + collect_submodules('simple_history')
    + collect_submodules('whitenoise')
    + collect_submodules('waitress')
    + collect_submodules('xhtml2pdf')
    + collect_submodules('reportlab')
    + [
        'django.contrib.auth.backends.ModelBackend',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.core.cache.backends.locmem.LocMemCache',
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.template.context_processors.auth',
        'django.template.context_processors.messages',
        'html5lib', 'pypdf', 'PIL', 'svglib', 'tinycss2', 'cssselect2', 'argon2',
    ]
)

datas = [
    ('templates', 'templates'),
    ('staticfiles', 'staticfiles'),
]
datas += collect_data_files('reportlab')
datas += collect_data_files('xhtml2pdf')

a = Analysis(
    ['desktop/launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'pytest', 'jinja2'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LabClinico',
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
    # icon='icono.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='LabClinico',
)
