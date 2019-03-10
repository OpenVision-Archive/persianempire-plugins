SUBDIRS = 720x576 1024x576 1280x720 lib mediabackends

installdir = $(libdir)/enigma2/python/Plugins/Extensions/AirPlayer

install_PYTHON = *.py

install_DATA = *.png

if MIPSEL
dist_install_DATA = atproxy proxy libairtunes.so.0

install-data-hook:
	chmod +x $(DESTDIR)$(installdir)/atproxy
	chmod +x $(DESTDIR)$(installdir)/proxy
	chmod +x $(DESTDIR)$(installdir)/libairtunes.so.0
endif
