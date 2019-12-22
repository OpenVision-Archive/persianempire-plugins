#!/bin/sh
#13.12.2010
##############Änderbare Variablen###############
VSNDMAN=$4 #manuelle SecondStageLoader Version, wird hier ein Wert eingegeben, dann wird dieser Wert immer benutzt! Unabhängig der Ermittlungen über ipkg-list oder IHAD
################################################

DIRECTORY=`echo "$1" | sed -e "s/\/*$/\1/"`
DEBUG=$3

#################Exit cleanup################
for sig in 0 1 2 3 6 14 15; do
	trap "cleanup $sig" $sig
done

#echo "$1 $2 $3 $4"
cleanup() {
	EXIT_CODE=$?
	if [ $EXIT_CODE = 130 ] ; then
		echo " "
		echo "**************************"
		echo "*     Aborted by User    *"
		echo "**************************"
	fi
	if [ -s "$SWAPDIR"/swapfile_backup ] ; then #Überprüfen ob Swapfile von Script erstellt wurde, wenn ja löschen
		# start mod by JackDaniel
		swapoff $SWAPDIR/swapfile_backup 2> /dev/null
		rm -rf $SWAPDIR/swapfile_backup
		echo " "
		echo "----------------------------------------"
		echo "deactivating an deleting swapfile"
		echo "----------------------------------------"
	fi
	
	mountedroot=`mount | grep /tmp/bi/root | cut -d " " -f3`
	mountedboot=`mount | grep /tmp/bi/boot | cut -d " " -f3`
	if [ "$mountedroot" = "/tmp/bi/root" -o "$mountedboot" = "/tmp/bi/boot" ]; then
		umount /tmp/bi/root 2> /dev/null
		umount /tmp/bi/boot 2> /dev/null
		echo " "
		echo "----------------------------------------"
		echo "umount /tmp/bi/root"
		echo "umount /tmp/bi/boot"
		echo "----------------------------------------"
	fi
	rm -rf /tmp/secondstage.bin
	rm -rf /tmp/bi
	rm -rf $DIRECTORY/bi
	echo " "
	echo "---------------------------------------------------"
	echo "- For questions visit: www.dreamoem.com  -"
	echo "- please attach-"
	echo "- the log from /tmp/FlashBackupLog.               -"
	echo "---------------------------------------------------"

	echo "exit "$EXIT_CODE
#	echo "exit "$EXIT_CODE > /tmp/"exit-code"
	trap - 0 # Exit Handler deaktivieren
	exit $EXIT_CODE
}
MTDBOOT=2
MTDROOT=3

SWAPSIZE=$2
if [ "$SWAPSIZE" -lt 1 ]; then
SWAPSIZE=128
fi

if grep -qs 7020 /proc/bus/dreambox ; then
	BOXTYPE=dm7020
	VSND=84
	OPTIONS="--eraseblock=0x4000 -n -b"
elif grep -qs DM600PVR /proc/bus/dreambox ; then
	BOXTYPE=dm600pvr
	VSND=84
	OPTIONS="--eraseblock=0x4000 -n -b"
elif grep -qs DM500PLUS /proc/bus/dreambox ; then
	BOXTYPE=dm500plus
	VSND=84
	OPTIONS="--eraseblock=0x4000 -n -b"
elif grep -qs 'ATI XILLEON HDTV SUPERTOLL' /proc/cpuinfo ; then
	BOXTYPE=dm7025
	VSND=84
	OPTIONS="--eraseblock=0x4000 -n -l"
elif grep -qs 'dm7025' /etc/model ; then
	BOXTYPE=dm7025
	VSND=84
	OPTIONS="--eraseblock=0x4000 -n -l"
elif grep -qs 'dm8000' /etc/model ; then
	BOXTYPE=dm8000
	VSND=84
	OPTIONS="--eraseblock=0x20000 -n -l"
elif grep -qs dm800se /etc/model ; then
        BOXTYPE=dm800se
       	VSND=84b
        OPTIONS="--eraseblock=0x4000 -n -l"
elif grep -qs 'dm800' /etc/model ; then
	BOXTYPE=dm800
	VSND=84b
	HTTPFILE=sim2-dm800-82.bin
	OPTIONS="--eraseblock=0x4000 -n -l"
elif grep -qs 'dm500hd' /etc/model ; then
	BOXTYPE=dm500hd
	VSND=84b
	OPTIONS="--eraseblock=0x4000 -n -l"
else
	echo "No supported Dreambox found!!!"
	exit 0
fi
# Edit by Erim Start
echo " "
echo "*********************"
echo "** $BOXTYPE found **"
echo "*********************"
echo " "

echo "---------------------------------------------------------------"
############# Überprüfe ob Datenträger vorhanden ist, wenn nicht suche alternativen ###############
listdummy=ls "$DIRECTORY"/blabla 2> /dev/null
FREESIZE=`df -m "$DIRECTORY" | tr -s " " | tail -n1 | cut -d' ' -f4 | sed "s/Available/0/`
if ! [ "$FREESIZE" -gt "128" ]; then
	echo ""$DIRECTORY" can't be used for FlashBackup because there is too less space left on the device!"
	echo "trying to find an alternative medium"
echo "---------------------------------------------------------------"
	DEVICE=`df -m | grep / | awk '{print $4 " " $1}' | sort -n | cut -d ' ' -f2 | tail -n1`
	DIRECTORY=`mount | grep $DEVICE | sort -n | cut -d ' ' -f3`
	FREESIZE=`df -m | grep / | awk '{print $4 " " $1}' | sort -n | cut -d ' ' -f1 | tail -n1`
	if [ "$FREESIZE" -lt "128" ]; then
		echo "No laternative medium could be found"
		echo "probably no correct medium is mounted"
		echo "---------------------------------------------------------------"
		exit 0
	else
		echo "Alternative medium=$DIRECTORY"
echo "---------------------------------------------------------------"
	fi
fi

############# Überprüfe freien Datenträgerplatz ###############
echo "check if 128MB are free in $DIRECTORY"
if [ "$FREESIZE" -lt "128" ]; then
		echo "Free memory space="$FREESIZE"MB,aborting FlashBackup"
		echo "---------------------------------------------------------------"
		exit 0
	else
		echo "Free memory space="$FREESIZE"MB=OK"
	if [ $DEBUG = "debugon" ] 2> /dev/null ; then
		SWAPDIR=$DIRECTORY/backup/FlashBackup-Debug
		SSLDIR=$DIRECTORY/backup/FlashBackup-Debug/SSL
	else
		SWAPDIR=$DIRECTORY/backup/FlashBackup
		SSLDIR=$DIRECTORY/backup/FlashBackup/SSL
	fi
	echo "---------------------------------------------------------------"
fi
mkdir -p $SSLDIR
###############Überprüfe auf manuell gesetzten SSL############


#############Überprüfe ob VSND ein numerischer Wert ist##################

############Versuche Flash-Image zu ermitteln###########
if [ $BOXTYPE = "dm8000" -o $BOXTYPE = "dm800se" -o $BOXTYPE = "dm800" -o $BOXTYPE = "dm7025" -o $BOXTYPE = "dm500hd" ] ;then
	echo "Trying to identify flash-image"

if grep -qs "comment=iCVS Image" /etc/image-version ; then
		IMAGEINFO=iCVS
		LINK="Link: http://www.ihad.tv"
		echo "$IMAGEINFO found"
	elif grep -qs "\<oe@dreamboxupdate.com\>" /etc/image-version ; then
		IMAGEINFO=CVS
		LINK="Link: http://www.dreamboxupdate.com"
		echo "$IMAGEINFO found"
	elif grep -qs "url=http:\/\/www.i-have-a-dreambox.com" /etc/image-version ; then
#		IMAGEINFO=Gemini-`cat /etc/image-version | grep version | cut -d'2' -f1 | sed 's/.*\(.\{3\}\)$/\1/' | cut -b 1`.`cat /etc/image-version | grep version | cut -d'2' -f1 | sed 's/.*\(.\{2\}\)$/\1/'` # sed Befehl schnappt sich die letzten 3 Zeichen
		IMAGEINFO=Gemini-`cat /etc/issue | cut -d " " -f2 | cut -d "." -f1-2 | head -n 1` #sed 's/.*\(.\{2\}\)$/\1/'` # sed Befehl schnappt sich die letzten 3 Zeichen
		LINK="Link: http://www.ihad.tv"
		echo "$IMAGEINFO found"
	elif [ `cat /etc/image-version | grep creator | sed "s/creator=//" | cut -d " " -f 1` = "OoZooN" ] ; then
		IMAGEINFO=OoZooN-`cat /etc/issue | cut -d " " -f2 | cut -d "." -f1-2 | head -n 1`
		LINK="Link: http://www.oozoon.de/progs/images/$BOXTYPE"
		echo "$IMAGEINFO found"
	elif [ `cat /etc/image-version | grep creator | sed "s/creator=//" | cut -d " " -f 1` = "newnigma2" ] ; then
		IMAGEINFO=Newnigma-`cat /etc/image-version | grep catalog | sed 's/.*\(.\{3\}\)$/\1/'`
		echo "$IMAGEINFO found"
		LINK="Link: http://www.newnigma2.to/"
		
	elif [ `cat /etc/image-version | grep creator | sed "s/creator=//" | cut -d " " -f 1` = "LT" ] ; then
		IMAGEINFO=LT-Team
		LINK="Link: http://www.lt-forums.org/"
		echo "$IMAGEINFO found"
	elif [ `cat /etc/image-version | grep creator | sed "s/creator=//" | cut -d " " -f 1` = "MiLo" ] ; then
		IMAGEINFO=MiLo
		LINK="Link: http://www.pli-images.org/"
		echo "$IMAGEINFO found"
	elif grep -qs "MerlinDownloadBrowser" /usr/lib/enigma2/python/Plugins/Extensions/AddOnManager/plugin.py ; then
		IMAGEINFO="Merlin-2.Excalibur"-`cat /etc/issue | cut -d " " -f2 | cut -d "." -f1-2 | head -n 1`
		LINK="Link: http://www.dreambox-tools.info/"
		echo "$IMAGEINFO found"
	elif [ `cat /etc/image-version | grep creator | sed "s/creator=//" | cut -d " " -f 1` = "PLi" ] ; then
		IMAGEINFO=PLi
		LINK="Link: http://www.pli-images.org/"
		echo "$IMAGEINFO found"
	else
		IMAGEINFO=FlashBackup
		LINK="Link: http://sources.dreamboxupdate.com/opendreambox/1.6/$BOXTYPE/experimental"
		echo "Couldn't identify flash-image, using FlashBackup as backupname"
	fi
else
	IMAGEINFO=FlashBackup
	echo "Couldn't identify flash-image, using FlashBackup as backupname"
fi
	if [ -e /usr/lib/enigma2/python/Plugins/Bp/geminimain ]; then
#		IMAGEINFO=Gemini-`cat /etc/image-version | grep version | cut -d'2' -f1 | sed 's/.*\(.\{3\}\)$/\1/' | cut -b 1`.`cat /etc/image-version | grep version | cut -d'2' -f1 | sed 's/.*\(.\{2\}\)$/\1/'` # sed Befehl schnappt sich die letzten 3 Zeichen
		GP3="GP3."`cat /usr/lib/enigma2/python/Plugins/Bp/geminimain/gVersion.py | sed -e "s/^.*'\(.*\)'.*$/\1/"`"-"
		LINK="Link: http://www.ihad.tv"
		echo "$GP3 found"
fi
	echo "---------------------------------------------------------------"
DATE=`date +%Y-%m-%d@%H.%M.%S`
PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/PurePrestige/Stools/PPFlashBackup
MKFS=/usr/sbin/mkfs.jffs2
BUILDIMAGE=/usr/bin/buildimage
BACKUPIMAGE=$SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-sim2-SSL-$VSND.nfi
SND=secondstage-sim2-$BOXTYPE-$VSND.bin

if [ ! -f $MKFS ] ; then
#	echo $MKFS" not found in /usr/bin :("
	exit 0
fi
if [ ! -f $BUILDIMAGE ] ; then
	echo $BUILDIMAGE" not found in /usr/bin :("
        exit 0
fi

############Überprüfe ob SSL auf HDD liegt, wenn nicht download SSL ##########
if [ -f $SSLDIR/$SND ] ; then
  cp -r $SSLDIR/$SND /tmp/secondstage.bin 2> /dev/null
  echo "Secondstageloader found in $SSLDIR ,use $SND"
else
  echo "...Download" $SND
  wget -q http://mfaraj57.dreamoem.net/secondstage/$SND -O $SSLDIR/$SND > /dev/null
###########Überprüfe download####################
	if [ -f $SSLDIR/$SND ] ; then
		cp -r $SSLDIR/$SND /tmp/secondstage.bin 2> /dev/null
	else
		echo ""
		echo "##############################################################"
		echo "# "$SND" couldn't be downloaded #"
		echo "# maybe your Box or dreamoem.com is offline    #"
		echo "##############################################################"
		echo ""
        exit 0
	fi
fi
############### Prüfe ob MD5 Datei auf HDD liegt und #################

echo "---------------------------------------------------------------"

echo "---------------------------------------------------------------"

case "$DIRECTORY" in
	/media/net* )
		echo "Skipping SWAP-creation because the backup will be done to a network device"
	;;
	* )
		echo "Checking free memory, about "$SWAPSIZE"MB will bee needed"
let MEMFREE=`free | grep Total | tr -s " " | cut -d " " -f 4 `/1024
  if [ "$MEMFREE" -lt $SWAPSIZE ]; then
  echo "Memory is smaller than "$SWAPSIZE"MB, FlashBackup has to create a swapfile"
echo "---------------------------------------------------------------"
  # Edit by Erim Stop
  #start mod by JackDaniel
  echo "Creating swapfile on $SWAPDIR with "$SWAPSIZE"MB"
  dd if=/dev/zero of=$SWAPDIR/swapfile_backup bs=1024k count=$SWAPSIZE
  mkswap $SWAPDIR/swapfile_backup
  swapon $SWAPDIR/swapfile_backup
echo "---------------------------------------------------------------"
  echo "Swapfile activated"
echo "---------------------------------------------------------------"
  # end mod by JackDaniel
else
  echo "memory="$MEMFREE"MB=OK"
fi
	;;
esac

echo "***********************************************"
#start mod by JackDaniel
starttime="$(date +%s)"
echo "* FlashBackup started at: `date +%H:%M:%S`          *"
echo "***********************************************"
# end mod by JackDaniel
rm -rf $DIRECTORY/bi
mkdir -p $DIRECTORY/bi
mkdir -p /tmp/bi/root
mkdir -p /tmp/bi/boot

echo "Mounting flash filesystems"
mount -t jffs2 /dev/mtdblock/$MTDROOT /tmp/bi/root
mount -t jffs2 /dev/mtdblock/$MTDBOOT /tmp/bi/boot
echo "Done mounting the filesystems"

if [ -s /tmp/secondstage.bin ] ; then
	echo "create boot.jffs2..."
	$MKFS --root=/tmp/bi/boot --faketime --output=$DIRECTORY/bi/boot.jffs2 $OPTIONS
		SZboot=`ls -al $DIRECTORY/bi/boot.jffs2 | awk '{print $5}'`
	echo "create root.jffs2..."
	$MKFS --root=/tmp/bi/root --faketime --output=$DIRECTORY/bi/root.jffs2 $OPTIONS
		SZroot=`ls -al $DIRECTORY/bi/root.jffs2 | awk '{print $5}'`
	echo "create Secondstageloader..."
	if [ $BOXTYPE = "dm800se" -o $BOXTYPE = "dm800" -o $BOXTYPE = "dm8000" -o $BOXTYPE = "dm500hd" ] ; then
		cp /tmp/secondstage.bin $DIRECTORY/bi/main.bin.gz
	else
		gzip -c /tmp/secondstage.bin > $DIRECTORY/bi/main.bin.gz
	fi
	SZssl=`ls -al /tmp/secondstage.bin | awk '{print $5}'`
	rm -rf /tmp/secondstage.bin

	echo "create" $BOXTYPE "FlashBackup..."

	if [ $BOXTYPE = "dm7025" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm800se" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE 64 > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm800" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE 64 > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm8000" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE 64 large > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm7020" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm600pvr" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm500plus" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE > $BACKUPIMAGE
	elif [ $BOXTYPE = "dm500hd" ] ; then
		$BUILDIMAGE $DIRECTORY/bi/main.bin.gz $DIRECTORY/bi/boot.jffs2 $DIRECTORY/bi/root.jffs2 $BOXTYPE 64 > $BACKUPIMAGE
	fi

SZimage=`ls -al $BACKUPIMAGE | awk '{print $5}'`
SZsum=`expr $SZboot "+" $SZroot "+" $SZssl`
SZdiff=`expr $SZimage "-" $SZsum`

########Abfrage Image erstellt ######## 
		if [ "$SZsum" -lt $SZimage ]; then
#		if [ -f $BACKUPIMAGE ] ; then
		echo "----------------------------------------------------------------------"
		echo "FlashBackup created in:" $BACKUPIMAGE
		echo "----------------------------------------------------------------------"
			echo "Enigma2: Experimental " > $SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-SSL-$VSND.nfo
			echo "Machine: Dreambox $BOXTYPE" >> $SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-SSL-$VSND.nfo
			echo "Date: "$DATE | cut -d '@' -f1 | sed -e "s/-//g" >> $SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-SSL-$VSND.nfo
			echo "Issuer: $IMAGEINFO" >> $SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-SSL-$VSND.nfo
			echo $LINK >> $SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-SSL-$VSND.nfo

		else
			echo "Download Error :("
			rm -rf $SWAPDIR/$IMAGEINFO-$GP3$BOXTYPE-$DATE-SSL-$VSND.nfi
			exit 1
		fi

echo "Removing the build directory and mount points"
umount /tmp/bi/root
umount /tmp/bi/boot
rm -rf /tmp/bi
rm -rf $DIRECTORY/bi
stoptime="$(date +%s)"
elapsed_seconds="$(expr $stoptime - $starttime)"
echo "***********************************************"
echo "* FlashBackup finished at: `date +%H:%M:%S`            *"
echo "* Duration of FlashBackup: $((elapsed_seconds / 60))minutes $((elapsed_seconds % 60))seconds *"
echo "***********************************************"
# end mod by JackDaniel
fi
exit 0
