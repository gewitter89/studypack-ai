# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import customtkinter
ctk_path = customtkinter.__path__[0]

datas = [
    ('config', 'config'),
    ('prompts', 'prompts'),
    ('templates_library', 'templates_library'),
    ('examples', 'examples'),
    (ctk_path, 'customtkinter'),
]

hiddenimports = [
    'customtkinter',
    'PIL._tkinter_finder',
    'dotenv',
    'requests',
    'openai',
    'fitz',
    'google.genai',
    'pydantic',
    'pydantic_core',
    'reportlab',
    'reportlab.lib.pagesizes',
    'reportlab.lib.units',
    'reportlab.lib.styles',
    'reportlab.lib.enums',
    'reportlab.lib.colors',
    'reportlab.platypus',
    'reportlab.pdfbase',
    'reportlab.pdfbase.ttfonts',
    'reportlab.pdfgen',
    'reportlab.graphics.shapes',
    'reportlab.graphics',
]

excludes = [
    'torch', 'torchvision', 'tensorflow',
    'transformers', 'sklearn', 'scipy',
    'pandas', 'numpy', 'matplotlib',
    'cv2', 'av', 'yt_dlp',
    'Crypto', 'onnxruntime',
    'uvicorn', 'fastapi',
    'lxml', 'sentry_sdk',
    'numba',
    'jsonschema', 'grpc',
    'sqlalchemy', 'sqlite3',
    'psutil', 'bcrypt',
    'httplib2', 'opentelemetry',
    'pytest', 'tqdm',
    'bs4', 'selenium', 'playwright',
    'PySide2', 'PyQt5', 'PySide6', 'PyQt6',
    'shiboken2', 'shiboken6', 'pyqtgraph.canvas',
    'PySimpleGUI', 'gi', 'wx',
    'google.api_core', 'googleapiclient',
    'google.auth', 'google.oauth2',
    'google.protobuf', 'google.longrunning',
    'google.ai.generativelanguage_v1beta',
    'proto', 'google.cloud',
    'google.generativeai',
    'google_auth_httplib2', 'google_auth_oauthlib',
    'google_auth', 'oauth2client',
    'grpc_status', 'grpc_gcp',
    'sounddevice', 'IPython',
    'cryptography', 'pycparser',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='StudyPack AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime140.dll'],
    console=False,
    icon='app/icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
