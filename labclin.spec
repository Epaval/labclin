# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = (
    # Terceros usados en apps/config (archivos fuente, no se analizan solos)
    ['environ', 'django_environ']
    # Django completo (apps/config son fuente y cargan módulos dinámicamente)
    + collect_submodules('django')
    # Nuestros paquetes de terceros
    + collect_submodules('axes')
    + collect_submodules('simple_history')
    + collect_submodules('whitenoise')
    + collect_submodules('waitress')
    + collect_submodules('xhtml2pdf')
    + collect_submodules('reportlab')
    + collect_submodules('html5lib')
    + collect_submodules('pypdf')
    + collect_submodules('svglib')
    + collect_submodules('tinycss2')
    + collect_submodules('cssselect2')
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
        'argon2.exceptions', 'argon2.low_level',
    ]
)

datas = [
    ('templates', 'templates'),
    ('staticfiles', 'staticfiles'),
    # TU CÓDIGO VA COMO ARCHIVOS (no congelado): se importa en runtime
    ('apps', 'apps'),
    ('config', 'config'),
]
datas += collect_data_files('reportlab')
datas += collect_data_files('xhtml2pdf')

a = Analysis(
    ['desktop/launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'pytest'],
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
    icon="icono.ico",
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
    name='LabClinico',
)
