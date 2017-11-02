PLATFORM = $(shell uname)

PYTHON_VERSION = 2.7.3
PYWIN32_VERSION = 218
PYINSTALLER_VERSION = 2.0
SETUPTOOLS_VERSION=0.6c11

MSVCP90 = ${WINE_PATH}/Python27/msvcp90.dll
PYINSTALLER=tools/pyinstaller-${PYINSTALLER_VERSION}/pyinstaller.py
PYWIN32=pywin32-${PYWIN32_VERSION}.win32-py2.7.exe

WINE_PATH=~/.wine/drive_c

NSIS_PATH = ${WINE_PATH}/NSIS

MAKENSIS_EXE = ${NSIS_PATH}/makensis.exe

DOWNLOAD_PATH=deps

PYTHON_MODULES=pynes

PYTHON_EXE=${WINE_PATH}/Python27/python.exe
EASYINSTALL_EXE=${WINE_PATH}/Python27/Scripts/easy_install.exe
PIP_EXE=${WINE_PATH}/Python27/Scripts/pip.exe

WGET = wget -q 

OK=\033[32m[OK]\033[39m
FAIL=\033[31m[FAIL]\033[39m
CHECK=@if [ $$? -eq 0 ]; then echo "${OK}"; else echo "${FAIL}" ; fi

default: python.mk
	@$(MAKE) -C . test

ifeq "true" "${shell test -f python.mk && echo true}"
include python.mk
endif

python.mk:
	@${WGET} https://raw.githubusercontent.com/gutomaia/makery/master/python.mk && \
		touch $@

clean: python_clean

purge: python_purge
	@rm python.mk

build: python_build

test: python_build ${REQUIREMENTS_TEST}
	${VIRTUALENV} nosetests --processes=2 -e image_test.py

ci:
ifeq "true" "${TRAVIS}"
	CI=1 nosetests -v --with-timer --timer-top-n 0 --with-coverage --cover-xml --cover-package=${PYTHON_MODULES} ${PYTHON_MODULES}
else
	${VIRTUALENV} CI=1 nosetests -v --with-timer --timer-top-n 0 --with-coverage --cover-xml --cover-package=${PYTHON_MODULES} ${PYTHON_MODULES}
endif

pep8: ${REQUIREMENTS_TEST}
	${VIRTUALENV} pep8 --statistics -qq pynes | sort -rn || echo ''

todo:
	${VIRTUALENV} pep8 --first pynes
	find pynes -type f | xargs -I [] grep -H TODO []

search:
	find pynes -regex .*\.py$ | xargs -I [] egrep -H -n 'print|ipdb' [] || echo ''

report:
	coverage run --source=pynes setup.py test

tdd:
	${VIRTUALENV} tdaemon --ignore-dirs="build,dist,bin,site,pynes.egg-info,venv" --custom-args="-e image_test.py --with-notify --no-start-message"

deps/.done:
	@echo "Creating dependencies dir: \c"
	@mkdir -p deps
	@touch $@
	${CHECK}

tools/.done:
	@echo "Creating tools dir: \c"
	@mkdir -p tools
	@touch $@
	${CHECK}

deps/pyinstaller-${PYINSTALLER_VERSION}.zip: deps/.done
	@echo "Downloading pyinstaller-${PYINSTALLER_VERSION}.zip: \c"
	@cd deps && \
		${WGET} http://sourceforge.net/projects/pyinstaller/files/${PYINSTALLER_VERSION}/pyinstaller-${PYINSTALLER_VERSION}.zip && \
		cd .. && touch $@
	${CHECK}

deps/python-${PYTHON_VERSION}.msi: deps/.done
	@echo "Downloading python-${PYTHON_VERSION}.msi: \c"
	@cd deps && \
		${WGET} http://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.msi && \
		cd .. && touch $@
	${CHECK}

deps/${PYWIN32}: deps/.done
	@echo "Downloading python-${PYTHON_VERSION}.msi: \c"
	@cd deps && \
		${WGET} http://downloads.sourceforge.net/project/pywin32/pywin32/Build\%20${PYWIN32_VERSION}/${PYWIN32} && \
		touch ${PYWIN32}
	${CHECK}


${PYTHON_EXE}: deps/python-${PYTHON_VERSION}.msi
	@cd deps && \
		msiexec /i python-2.7.3.msi /qb
	@touch $@

${WINE_PATH}/Python27/msvcp90.dll: ${WINE_PATH}/windows/system32/msvcp90.dll
	@cp $< $@

${WINE_PATH}/Python27/Scripts/pywin32_postinstall.py: ${PYTHON_EXE} deps/${PYWIN32}
	@cd deps && \
		echo wine deps/${PYWIN32}
	@touch $@

deps/distribute_setup.py:
	@echo "Downloading distribute_setup.py: \c"
	@cd deps && \
		${WGET} http://python-distribute.org/distribute_setup.py && \
		cd .. && touch $@
	${CHECK}

${EASYINSTALL_EXE}: ${PYTHON_EXE} deps/distribute_setup.py
	cd deps && \
		wine ${PYTHON_EXE} distribute_setup.py
	@touch $@

${PIP_EXE}: ${PYTHON_EXE} ${EASYINSTALL_EXE}
	wine ${EASYINSTALL_EXE} pip
	@touch $@

${PYINSTALLER}: tools/.done deps/pyinstaller-2.0.zip
	@echo "Unzipping PyInstaller ${PYINSTALLER_VERSION}: \c"
	@cd tools && \
		unzip -qq ../deps/pyinstaller-2.0.zip && \
		cd .. && touch $@
	${CHECK}

tools/env/bin/activate: tools/.done
	virtualenv --no-site-packages --distribute tools/env
	@touch $@

tools/requirements.windows.check: ${PIP_EXE} requirements.txt
	wine ${PIP_EXE} install -r requirements.txt
	@touch $@

dependencies_wine: ${PYTHON_EXE} ${PIP_EXE}


windows_binary_dependencies: ${WINE_PATH}/Python27/Scripts/pywin32_postinstall.py

dist/linux/pynes: build ${PYINSTALLER} tools/requirements.windows.check
	@rm -rf build/pyi.linux
	@rm -rf build/pyi.linux2
	@rm -rf dist/linux
	python ${PYINSTALLER} pynes.linux.spec
	@touch $@

dist/windows/pynes.exe: ${PYINSTALLER} ${PYTHON_EXE} windows_binary_dependencies tools/requirements.windows.check
	@rm -rf build/pyi.win32
	@rm -rf dist/windows
	wine ${PYTHON_EXE} ${PYINSTALLER} --onefile pynes.windows.spec
	@touch $@

linux: dist/linux/pynes

windows: dist/windows/pynes.exe

dist: linux windows

deps/nsis-3.0a1-setup.exe:
	@echo "Downloading NSIS \c"
	@cd deps && \
		${WGET} http://downloads.sourceforge.net/project/nsis/NSIS%203%20Pre-release/3.0a1/nsis-3.0a1-setup.exe
	@touch "$@"
	${CHECK}

${MAKENSIS_EXE}: deps/nsis-3.0a1-setup.exe
	@echo "Installing NSIS \c"
	@wine deps/nsis-3.0a1-setup.exe /S /D=C:\\NSIS
	@touch "$@"
	${CHECK}

nsis: ${MAKENSIS_EXE}
	@wine ${MAKENSIS_EXE} installer.nsi

installer: nsis

ghpages: deploy download_deps
	rm -rf /tmp/ghpages
	mkdir -p /tmp/ghpages
	cp -Rv static/* /tmp/ghpages
	cp -Rv external/* /tmp/ghpages
	cp -Rv lib/*.js /tmp/ghpages

	cd /tmp/ghpages && \
		git init && \
		git add . && \
		git commit -q -m "Automatic gh-pages"
	cd /tmp/ghpages && \
		git remote add remote git@github.com:gutomaia/nodeNES.git && \
		git push --force remote +master:gh-pages
	rm -rf /tmp/ghpages

.PHONY: clean linux windows dist nsis installer run report ghpages
