# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Arquivos de dados que precisam ser incluídos
added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('data', 'data'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask',
        'flask.app',
        'flask.helpers',
        'flask.json',
        'flask.templating',
        'flask.wrappers',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.utils',
        'jinja2',
        'jinja2.ext',
        'markupsafe',
        'openpyxl',
        'openpyxl.workbook',
        'openpyxl.styles',
        'openpyxl.utils',
        'docx',
        'docx.document',
        'docx.enum.text',
        'docx.shared',
        'tkinter',
        'tkinter.messagebox',
        'tkinter.ttk',
        '_tkinter',
        'webbrowser',
        'database',
        'sqlite3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Gerente_de_Pacientes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Não mostrar console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)