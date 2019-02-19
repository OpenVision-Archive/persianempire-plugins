SUBDIRS = Daemons Extra pictures

installdir = $(libdir)/enigma2/python/Plugins/SystemPlugins/PEPanel

install_PYTHON = *.py

install_DATA = \
	*.sh \
	*.xml

install-data-hook:
	chmod +x $(DESTDIR)$(installdir)/cpu.sh
	chmod +x $(DESTDIR)$(installdir)/sundtekinstall.sh

