SUBDIRS = Applications buttons ddbuttons icons images infobuttons nbuttons panelbuttons PurePrestigeAddOnsManager rssicons scripts Stools

installdir = $(libdir)/enigma2/python/Plugins/Extensions/PurePrestige

install_PYTHON = *.py

install_DATA = \
	pyo2xml \
	*.png \
	*.xml

install-data-hook:
	chmod +x $(DESTDIR)$(installdir)/pyo2xml

