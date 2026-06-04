# -*- mode: python ; coding: utf-8 -*-

import os


excluded_binary_names = {
    # These can be picked up from a global Anaconda installation and conflict
    # with Qt6Core at runtime. Let Qt use the Windows system ICU instead.
    'icudt73.dll',
    'icuin.dll',
    'icuuc.dll',

    # Database-related DLLs can be pulled in by QtSql plugins. This app does
    # not use QtSql, and these add size plus extra dependency risk.
    'comerr64.dll',
    'gssapi64.dll',
    'k5sprt64.dll',
    'krb5_64.dll',
    'libpq.dll',
}

excluded_modules = [
    'PyQt6.QAxContainer',
    'PyQt6.QtBluetooth',
    'PyQt6.QtDBus',
    'PyQt6.QtDesigner',
    'PyQt6.QtHelp',
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtNfc',
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    'PyQt6.QtPdf',
    'PyQt6.QtPdfWidgets',
    'PyQt6.QtPositioning',
    'PyQt6.QtPrintSupport',
    'PyQt6.QtQml',
    'PyQt6.QtQuick',
    'PyQt6.QtQuick3D',
    'PyQt6.QtQuickWidgets',
    'PyQt6.QtRemoteObjects',
    'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    'PyQt6.QtSpatialAudio',
    'PyQt6.QtSql',
    'PyQt6.QtStateMachine',
    'PyQt6.QtSvg',
    'PyQt6.QtSvgWidgets',
    'PyQt6.QtTest',
    'PyQt6.QtTextToSpeech',
    'PyQt6.QtWebChannel',
    'PyQt6.QtWebSockets',
    'PyQt6.QtXml',
    'PyQt6.lupdate',
    'PyQt6.uic',
]


a = Analysis(
    ['main.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('eye_icon.ico', '.'),
        ('eye_settings.json', '.'),
        ('usage_logs', 'usage_logs'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    noarchive=False,
    optimize=0,
)

a.binaries = [
    item for item in a.binaries
    if os.path.basename(item[0]).lower() not in excluded_binary_names
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    [],
    name='Triple 2 Eye Protection',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='eye_icon.ico',
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Triple 2 Eye Protection',
)
