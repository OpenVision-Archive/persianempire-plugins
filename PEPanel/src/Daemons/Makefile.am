installdir = $(libdir)/enigma2/python/Plugins/SystemPlugins/PEPanel/Daemons

install_DATA = *.ext

install-data-hook:
	chmod +x $(DESTDIR)$(installdir)/Crond.ext
	chmod +x $(DESTDIR)$(installdir)/Dropbear.ext
	chmod +x $(DESTDIR)$(installdir)/Nfsd.ext
	chmod +x $(DESTDIR)$(installdir)/NTPd.ext
	chmod +x $(DESTDIR)$(installdir)/OpenVPN.ext
	chmod +x $(DESTDIR)$(installdir)/Samba.ext
	chmod +x $(DESTDIR)$(installdir)/Syslogd.ext
	chmod +x $(DESTDIR)$(installdir)/Telnet.ext
	chmod +x $(DESTDIR)$(installdir)/Vsftpd.ext

