include $(top_srcdir)/Rules-cpp.mak

plugindir = $(libdir)/enigma2/python/Plugins/Extensions/AirPlayer

plugin_LTLIBRARIES = zeroconf.la

zeroconf_la_SOURCES = \
	zeroconf.c

zeroconf_la_LDFLAGS = \
	$(PLUGIN_LIBTOOL_FLAGS)

zeroconf_la_LIBADD = \
	@LIBCRYPTO_LIBS@
