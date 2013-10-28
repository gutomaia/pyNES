PYTHON_VERSION = 2.7.3
PYWIN32_VERSION = 218
PYINSTALLER_VERSION = 2.0
SETUPTOOLS_VERSION=0.6c11

PYINSTALLER=tools/pyinstaller-${PYINSTALLER_VERSION}/pyinstaller.py
PYWIN32=pywin32-${PYWIN32_VERSION}.win32-py2.7.exe

WINE_PATH=~/.wine/drive_c
DOWNLOAD_PATH=deps

PYTHON_EXE=${WINE_PATH}/Python27/python.exe
EASYINSTALL_EXE=${WINE_PATH}/Python27/Scripts/easy_install.exe
PIP_EXE=${WINE_PATH}/Python27/Scripts/pip.exe

WGET = wget

OK=\033[32m[OK]\033[39m
FAIL=\033[31m[FAIL]\033[39m
CHECK=@if [ $$? -eq 0 ]; then echo "${OK}"; else echo "${FAIL}" ; fi

ifeq "" "$(shell which python)"
default:
	@echo "Please install python"
	exit 1
else
default: test
endif

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
	@cd deps && \
		${WGET} http://sourceforge.net/projects/pyinstaller/files/${PYINSTALLER_VERSION}/pyinstaller-${PYINSTALLER_VERSION}.zip
	@touch $@

deps/python-${PYTHON_VERSION}.msi: deps/.done
	@cd deps && \
		${WGET} http://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}.msi
	@touch $@

deps/${PYWIN32}: deps/.done
	@cd deps && \
		${WGET} http://downloads.sourceforge.net/project/pywin32/pywin32/Build\%20${PYWIN32_VERSION}/${PYWIN32}
	@touch $@

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
	cd deps && \
		${WGET} http://python-distribute.org/distribute_setup.py
	@touch $@

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
		unzip ../deps/pyinstaller-2.0.zip
	@touch $@

tools/env/bin/activate: tools/.done
	virtualenv --no-site-packages --distribute tools/env
	@touch $@

tools/requirements.windows.checked: ${PIP_EXE} requirements.txt
	wine ${PIP_EXE} install -r requirements.txt
	@touch $@

dependencies: tools/requirements.checked \
	tools/requirements_test.checked

dependencies_wine: ${PYTHON_EXE} ${PIP_EXE}


windows_binary_dependencies: ${WINE_PATH}/Python27/Scripts/pywin32_postinstall.py

dist/linux/pynes: ${PYINSTALLER} tools/requirements.windows.checked
	python ${PYINSTALLER} pynes.linux.spec

dist/windows/pynes.exe: ${PYINSTALLER} ${PYTHON_EXE} windows_binary_dependencies tools/requirements.windows.checked
	wine ${PYTHON_EXE} ${PYINSTALLER} --onefile pynes.windows.spec
	@touch $@

linux: dist/linux/pynes

windows: dist/windows/pynes.exe

dist: clean linux windows

clean:
	@rm -rf build
	@rm -rf dist
	@rm -rf reports

purge: clean
	@ rm -rf deps
	@rm -rf tools

test:
	@nosetests --processes=2 -e image_test.py

build: test

ci:
	@nosetests

pep8:
	@pep8 --statistics -qq pynes | sort -rn || echo ''

todo:
	pep8 --first pynes
	find pynes -type f | xargs -I [] grep -H TODO []

search:
	find pynes -regex .*\.py$ | xargs -I [] egrep -H -n 'print|ipdb' [] || echo ''

report:
	coverage run --source=pynes setup.py test

tdd:
	tdaemon --ignore-dirs build,dist,bin,site,pynes.egg-info --custom-args="-e image_test.py --with-growl"

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

.PHONY: clean run report ghpages
