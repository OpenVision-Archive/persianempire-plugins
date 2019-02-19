SUBDIRS = scripts

installdir = $(sysconfdir)/cron

install_DATA = \
	busybox-cron \
	*.sh

install-data-hook:
	chmod +x $(DESTDIR)$(installdir)/busybox-cron
	chmod +x $(DESTDIR)$(installdir)/*.sh

