# -*- mode: python -*-
a = Analysis(['bin/pynes', os.path.join(HOMEPATH, 'support\\_mountzlib.py'),
              os.path.join(HOMEPATH, 'support\\useUnicode.py')],
             pathex=[os.path.join('.')],
             hiddenimports=['pynes'
             ], hookspath=None)

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.zipfiles,
          a.datas,
          exclude_binaries=1,
          name=os.path.join('build', 'pyi.win32', 'pynes.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'windows'))

app = BUNDLE(coll,
             name=os.path.join('bundle', 'windows', 'pynes'))
