installdir = $(libdir)/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup/bin

install_DATA = \
	buildimage \
	mkfs.jffs2 \
	*.sh

install-data-hook:
	chmod +x $(DESTDIR)$(installdir)/buildimage
	chmod +x $(DESTDIR)$(installdir)/mkfs.jffs2
	chmod +x $(DESTDIR)$(installdir)/*.sh

