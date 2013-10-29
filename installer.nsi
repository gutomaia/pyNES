!define APPNAME "pyNES"
!define COMPANYNAME "gUTO.nET"
!define DESCRIPTION "Python Programming for NES"
# These three must be integers
!define VERSIONMAJOR 1
!define VERSIONMINOR 1
!define VERSIONBUILD 1
!define INSTALLSIZE 7233

OutFile "pyNES_installer.exe"

InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"


section "install"

setOutPath $INSTDIR

file "dist\windows\MSVCR90.dll"
file "dist\windows\_hashlib.pyd"
file "dist\windows\bz2.pyd"
file "dist\windows\pynes.exe"
file "dist\windows\pynes.exe.manifest"
file "dist\windows\python27.dll"
file "dist\windows\select.pyd"
file "dist\windows\unicodedata.pyd"

sectionEnd