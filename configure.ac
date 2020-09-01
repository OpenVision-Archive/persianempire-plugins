AC_INIT([enigma2-persianempire-plugins],[1.0])
AM_INIT_AUTOMAKE([dist-bzip2 foreign no-define tar-pax])
AC_CONFIG_HEADERS([enigma2-plugins-config.h])

# Silent rules are available since 1.11, but older versions
# are still in use. So don't use them unconditionally.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_USE_SYSTEM_EXTENSIONS
AC_SYS_LARGEFILE

AC_PROG_CC
AC_PROG_CXX
m4_ifdef([LT_INIT], [LT_INIT], [AC_PROG_LIBTOOL])
AC_CONFIG_MACRO_DIR([m4])

AC_PATH_PROG(MSGFMT, msgfmt, AC_MSG_ERROR(Could not find msgfmt))
AC_PATH_PROG(MSGINIT, msginit, AC_MSG_ERROR(Could not find msginit))
AC_PATH_PROG(MSGMERGE, msgmerge, AC_MSG_ERROR(Could not find msgmerge))
AC_PATH_PROG(MSGUNIQ, msguniq, AC_MSG_ERROR(Could not find msguniq))
AC_PATH_PROG(XGETTEXT, xgettext, AC_MSG_ERROR(Could not find xgettext))

AM_PATH_PYTHON
AX_PYTHON_DEVEL
AX_PTHREAD

AC_ARG_WITH(po,
	AS_HELP_STRING([--with-po],[enable updating of po files]),
	[with_po="$withval"],[with_po="no"])
if test "$with_po" = "yes"; then
	AC_PATH_PROG(MSGINIT, msginit)
	AC_PATH_PROG(MSGMERGE, msgmerge)
	AC_PATH_PROG(MSGUNIQ, msguniq)
	AC_PATH_PROG(XGETTEXT, xgettext)
	if test -z "$MSGINIT" -o -z "$MSGMERGE" -o -z "$MSGUNIQ" -o -z "$XGETTEXT"; then
		AC_MSG_ERROR([Could not find required gettext tools])
	fi
fi
AM_CONDITIONAL(UPDATE_PO, test "$with_po" = "yes")

AC_ARG_WITH(arch,
	AS_HELP_STRING([--with-arch],[build for ARCH, $withval]),
	[ARCH="$withval"],[ARCH=""])
AC_SUBST(ARCH)
AC_DEFINE_UNQUOTED(ARCH,"$ARCH",[box architecture])

AM_CONDITIONAL(SH4, test `echo "$ARCH" | cut -b 1-3` == "sh4")
AM_CONDITIONAL(MIPSEL, test `echo "$ARCH" | cut -b 1-6` == "mipsel")
AM_CONDITIONAL(ARM, test `echo "$ARCH" | cut -b 1-3` == "arm")

AC_ARG_WITH(boxtype,
	AS_HELP_STRING([--with-boxtype],[build for BOXTYPE, $withval]),
	[BOXTYPE="$withval"],[BOXTYPE=""])
AC_SUBST(BOXTYPE)
AC_DEFINE_UNQUOTED(BOXTYPE,"$BOXTYPE",[box type])

AC_ARG_WITH(boxbrand,
	AS_HELP_STRING([--with-boxbrand],[build for BOXBRAND, $withval]),
	[BOXBRAND="$withval"],[BOXBRAND=""])
AC_SUBST(BOXBRAND)
AC_DEFINE_UNQUOTED(BOXBRAND,"$BOXBRAND",[box brand])

AC_ARG_WITH(stbplatform,
	AS_HELP_STRING([--with-stbplatform],[build for STBPLATFORM, $withval]),
	[STBPLATFORM="$withval"],[STBPLATFORM=""])
AC_SUBST(STBPLATFORM)
AC_DEFINE_UNQUOTED(STBPLATFORM,"$STBPLATFORM",[stb platform])

AC_CONFIG_FILES([
Makefile

AirPlayer/Makefile
AirPlayer/po/Makefile
AirPlayer/src/Makefile
AirPlayer/src/720x576/Makefile
AirPlayer/src/1024x576/Makefile
AirPlayer/src/1280x720/Makefile
AirPlayer/src/1920x1080/Makefile
AirPlayer/src/lib/Makefile
AirPlayer/src/lib/biplist/Makefile
AirPlayer/src/mediabackends/Makefile

BlockContent/Makefile
BlockContent/po/Makefile
BlockContent/src/Makefile

BouquetProtection/Makefile
BouquetProtection/po/Makefile
BouquetProtection/src/Makefile

CamRestart/Makefile
CamRestart/po/Makefile
CamRestart/src/Makefile
CamRestart/src/images/Makefile

DeviceInfo/Makefile
DeviceInfo/po/Makefile
DeviceInfo/src/Makefile
DeviceInfo/src/images/Makefile

FontMagnifier/Makefile
FontMagnifier/po/Makefile
FontMagnifier/src/Makefile

LocaleManager/Makefile
LocaleManager/po/Makefile
LocaleManager/src/Makefile

NaviBarPE/Makefile
NaviBarPE/po/Makefile
NaviBarPE/src/Makefile
NaviBarPE/src/icons/Makefile
NaviBarPE/src/images/Makefile

NetworkServer/Makefile
NetworkServer/po/Makefile
NetworkServer/src/Makefile

PackageManager/Makefile
PackageManager/po/Makefile
PackageManager/src/Makefile
PackageManager/src/images/Makefile

PECamManager/Makefile
PECamManager/po/Makefile
PECamManager/src/Makefile
PECamManager/src/images/Makefile

PEFAQ/Makefile
PEFAQ/po/Makefile
PEFAQ/src/Makefile
PEFAQ/src/img/Makefile

PEInfo/Makefile
PEInfo/po/Makefile
PEInfo/src/Makefile
PEInfo/src/icons/Makefile

PEPanel/Makefile
PEPanel/po/Makefile
PEPanel/src/Makefile
PEPanel/src/Daemons/Makefile
PEPanel/src/Extra/Makefile
PEPanel/src/pictures/Makefile

PEWeather/Makefile
PEWeather/po/Makefile
PEWeather/src/Makefile
PEWeather/src/weather/Makefile
PEWeather/src/weather/small/Makefile

PurePrestige/Makefile
PurePrestige/etc/Makefile
PurePrestige/etc/cron/Makefile
PurePrestige/etc/cron/scripts/Makefile
PurePrestige/po/Makefile
PurePrestige/src/Makefile
PurePrestige/src/Applications/Makefile
PurePrestige/src/Applications/appbuttons/Makefile
PurePrestige/src/Applications/NetRadioPersian/Makefile
PurePrestige/src/Applications/NetRadioPersian/buttons/Makefile
PurePrestige/src/Applications/NetRadioPersian/icons/Makefile
PurePrestige/src/Applications/PersianLiveSoccer/Makefile
PurePrestige/src/Applications/PersianLiveSoccer/images/Makefile
PurePrestige/src/buttons/Makefile
PurePrestige/src/ddbuttons/Makefile
PurePrestige/src/icons/Makefile
PurePrestige/src/images/Makefile
PurePrestige/src/infobuttons/Makefile
PurePrestige/src/nbuttons/Makefile
PurePrestige/src/panelbuttons/Makefile
PurePrestige/src/PurePrestigeAddOnsManager/Makefile
PurePrestige/src/PurePrestigeAddOnsManager/SpinnerSelector/Makefile
PurePrestige/src/rssicons/Makefile
PurePrestige/src/scripts/Makefile
PurePrestige/src/Stools/Makefile
PurePrestige/src/Stools/Moretools/Makefile
PurePrestige/src/Stools/Moretools/Cronmanager/Makefile
PurePrestige/src/Stools/Moretools/language/Makefile
PurePrestige/src/Stools/Moretools/moretoolsbuttons/Makefile
PurePrestige/src/Stools/Moretools/ScreenGrabber/Makefile
PurePrestige/src/Stools/Moretools/ScreenGrabber/keymaps/Makefile
PurePrestige/src/Stools/PPFlashBackup/Makefile
PurePrestige/src/Stools/PPFlashBackup/bin/Makefile
PurePrestige/src/Stools/PPFlashBackup/images/Makefile
PurePrestige/src/Stools/PPrestigesatEditor/Makefile
PurePrestige/src/Stools/PPrestigesatEditor/ServiceEditor/Makefile
PurePrestige/src/Stools/toolsbuttons/Makefile

QuickWeather/Makefile
QuickWeather/po/Makefile
QuickWeather/src/Makefile
QuickWeather/src/anim/Makefile
QuickWeather/src/background/Makefile
QuickWeather/src/background1/Makefile
QuickWeather/src/NA/Makefile
QuickWeather/src/SetupKeymap/Makefile
QuickWeather/src/weathericons/Makefile
QuickWeather/src/windicons/Makefile

SambaServer/Makefile
SambaServer/po/Makefile
SambaServer/src/Makefile

SatelliteEditor/Makefile
SatelliteEditor/po/Makefile
SatelliteEditor/src/Makefile

ServiceEditor/Makefile
ServiceEditor/po/Makefile
ServiceEditor/src/Makefile

SimpleSatScan/Makefile
SimpleSatScan/po/Makefile
SimpleSatScan/src/Makefile

SoftCamUpdater/Makefile
SoftCamUpdater/po/Makefile
SoftCamUpdater/src/Makefile
SoftCamUpdater/src/images/Makefile

VUSolo2CIHighBitrateFix/Makefile
VUSolo2CIHighBitrateFix/po/Makefile
VUSolo2CIHighBitrateFix/src/Makefile

])
AC_OUTPUT
