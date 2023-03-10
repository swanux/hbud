prefix = /usr
lang = en
language = en_GB

INSTALL = install -Dm755
INSTALL_DATA = install -Dm 644
UNINSTALL = rm -rf


install:
	@# app source
	mkdir -p $(prefix)/bin/
	$(INSTALL) DEV_FILES/source/fpcalc -t $(prefix)/bin/fpcalc
	python3 -m nuitka DEV_FILES/source/hbud.py --remove-output --clean-cache=all --follow-import-to=hbud -o $(prefix)/bin/hbud

	@# desktop file
	$(INSTALL_DATA) DEV_FILES/data/hbud.desktop $(prefix)/share/applications/io.github.swanux.hbud.desktop

	@# metainfo
	$(INSTALL_DATA) DEV_FILES/data/appdata.xml $(prefix)/share/appdata/io.github.swanux.hbud.appdata.xml

	@# icons
	$(INSTALL_DATA) DEV_FILES/data/icons/scalable.svg $(prefix)/share/icons/hicolor/scalable/apps/io.github.swanux.hbud.svg

	@# translations
	$(INSTALL_DATA) DEV_FILES/source/locales/en/LC_MESSAGES/io.github.swanux.hbud.mo $(prefix)/share/hbud/locales/en/LC_MESSAGES/io.github.swanux.hbud.mo
	$(INSTALL_DATA) DEV_FILES/source/locales/hu/LC_MESSAGES/io.github.swanux.hbud.mo $(prefix)/share/hbud/locales/hu/LC_MESSAGES/io.github.swanux.hbud.mo

	@# compiled data files
	$(INSTALL_DATA) DEV_FILES/data/gschema.xml $(prefix)/share/glib-2.0/schemas/io.github.swanux.hbud.gschema.xml
	glib-compile-schemas $(prefix)/share/glib-2.0/schemas
	glib-compile-resources DEV_FILES/data/gresources.xml --target=$(prefix)/share/hbud/io.github.swanux.hbud.gresource


flatpak:
	flatpak-builder --force-clean --repo=repo/ build-dir/ DEV_FILES/data/manifest.yml
	flatpak build-bundle repo/ hbud.flatpak io.github.swanux.hbud
	flatpak install --reinstall --user -y hbud.flatpak
	flatpak run --env=LANG=$(language).UTF-8 io.github.swanux.hbud


test:
	mkdir -p DEV_FILES/schemas
	cp DEV_FILES/data/gschema.xml DEV_FILES/schemas/io.github.swanux.hbud.gschema.xml
	glib-compile-schemas DEV_FILES/schemas/
	glib-compile-resources DEV_FILES/data/gresources.xml --target=DEV_FILES/io.github.swanux.hbud.gresource
	LANG=$(language).UTF-8 HDIR="DEV_FILES/source/" DEV_FILES/source/./hbud.py


uninstall:
	@# app file
	$(UNINSTALL) $(prefix)/bin/hbud

	@# desktop file
	$(UNINSTALL) $(prefix)/share/applications/io.github.swanux.hbud.desktop

	@# appdata
	$(UNINSTALL) $(prefix)/share/appdata/io.github.swanux.hbud.appdata.xml

	@# icons
	$(UNINSTALL) $(prefix)/share/icons/hicolor/*/apps/io.github.swanux.hbud*

	@# translations
	$(UNINSTALL) $(prefix)/share/hbud


translate-new:
	mkdir -p DEV_FILES/source/locales/$(lang)/LC_MESSAGES/
	xgettext --from-code=UTF-8 --keyword=translatable --keyword=_ --sort-output --files-from=DEV_FILES/source/to_translate.txt -o DEV_FILES/source/locales/io.github.swanux.hbud.pot
	msginit --no-translator --locale=$(lang) --input=DEV_FILES/source/locales/io.github.swanux.hbud.pot --output=DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.po


translate-add:
	msgfmt -o DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.mo DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.po


translate-update:
	xgettext --from-code=UTF-8 --keyword=translatable --keyword=_ --sort-output --files-from=DEV_FILES/source/to_translate.txt -o DEV_FILES/source/locales/io.github.swanux.hbud.pot
	msginit --no-translator --locale=$(lang) --input=DEV_FILES/source/locales/io.github.swanux.hbud.pot --output=DEV_FILES/source/locales/$(lang)/LC_MESSAGES/$(lang)_tmp.po
	msgmerge -o DEV_FILES/source/locales/$(lang)/LC_MESSAGES/merged.po DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.po DEV_FILES/source/locales/$(lang)/LC_MESSAGES/$(lang)_tmp.po
	rm DEV_FILES/source/locales/$(lang)/LC_MESSAGES/$(lang)_tmp.po DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.po
	mv DEV_FILES/source/locales/$(lang)/LC_MESSAGES/merged.po DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.po


translate-upgrade:
	msgfmt -o DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.mo DEV_FILES/source/locales/$(lang)/LC_MESSAGES/io.github.swanux.hbud.po


py-module-gen:
	rm -rf hbud-env
	python3 -m venv hbud-env
	hbud-env/bin/python3 -m pip install azapi srt mediafile pydbus pyacoustid musicbrainzngs pyicu ordered-set nuitka
	hbud-env/bin/python3 -m pip freeze > requirements.txt
	tools/flatpak-pip-gen.py --runtime='org.gnome.Sdk//43' -r='requirements.txt' --output pypi-dependencies


clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	rm -rf build-dir
	rm -rf .flatpak-builder
	rm -rf hbud-env
	rm -rf DEV_FILES/*.gresource
	rm -rf DEV_FILES/schemas
	rm -rf repo
	rm -rf hbud.flatpak


setup:
	pip3 install azapi srt mediafile pydbus pyacoustid musicbrainzngs pyicu requirements-parser