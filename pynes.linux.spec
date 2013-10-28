# -*- mode: python -*-

a = Analysis(['bin/pynes'], pathex=[os.path.join('.')],
             hiddenimports=['pynes'], hookspath=None)

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build', 'pyi.linux', 'pynes'),
          debug=False,
          strip=None,
          upx=False,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=False,
               name=os.path.join('dist', 'linux'))
