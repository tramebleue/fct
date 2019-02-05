QGIS_USER_DIR=$(HOME)/.local/share/QGIS/QGIS3/profiles/default
PLUGIN_DIR=$(QGIS_USER_DIR)/python/plugins
TARGET=$(PLUGIN_DIR)/FluvialCorridorToolbox

default: install

plugin/resources.py: plugin/resources.qrc
	pyrcc5 -o plugin/resources.py plugin/resources.qrc

install: plugin/resources.py
	mkdir -p $(TARGET)
	cp -R plugin/* $(TARGET)
	echo Installed to $(TARGET)

extensions:
	make -C cython TARGET=$(TARGET) install

uninstall:
	echo Remove directory $(TARGET) ...
	rm -rf $(TARGET)

doc: install clean-doc
	cp README.md docs/index.md
	python3 autodoc.py

clean-doc:
	rm -rf docs/algorithms

clean:
	make -C cython clean