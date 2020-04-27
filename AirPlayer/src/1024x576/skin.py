# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

#<skin>
#<output id="0">
#	<resolution xres="1024" yres="576" bpp="32" />
#</output>

"""<screen name="AirPlayerMoviePlayer" position="192,480" size="704,64" title="InfoBar" flags="wfNoBorder">
	<ePixmap position="0,0" zPosition="-1" size="704,64" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/infobarmovie.png" />
	<eLabel text="AirPlayer" position="72,4" size="208,28" font="Regular;20" valign="top" noWrap="1" foregroundColor="#00ffffff" backgroundColor="#00000000" transparent="1" />
	<ePixmap zPosition="-1" position="72,32" size="480,7" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/progress_lightgrey.png" />
	<widget source="session.CurrentService" render="Progress" position="72,32" size="480,7" zPosition="2" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/progress.png" transparent="1">
		<convert type="ServicePosition">Position</convert>
	</widget>
	<widget source="session.CurrentService" render="PositionGauge" position="72,32" size="400,8" zPosition="2" transparent="1">
		<convert type="ServicePosition">Gauge</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" position="72,38" size="96,22" font="Regular;19" halign="left" foregroundColor="#00ffffff" backgroundColor="#00000000" transparent="1">
		<convert type="ServicePosition">Position</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" position="256,38" size="96,22" font="Regular;19" halign="center" foregroundColor="#00ffffff" backgroundColor="#00000000" transparent="1">
		<convert type="ServicePosition">Remaining</convert>
	</widget>
	<widget source="session.CurrentService" render="Label" position="440,38" size="112,22" font="Regular;19" halign="right" foregroundColor="#00ffffff" backgroundColor="#00000000" transparent="1">
		<convert type="ServicePosition">Length</convert>
	</widget>
	
	<widget name="bufferslider" position="72,32" size="480,7" zPosition="1" transparent="1" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/progress_grey.png" />
	<widget source="label_cache" transparent="1" render="Label" zPosition="2" position="352,3" size="200,14" font="Regular;12" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="right" />
	<widget source="label_speed" transparent="1" render="Label" zPosition="2" position="352,17" size="200,14" font="Regular;12" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="right" />
	<widget source="label_update"  transparent="1" render="Label" zPosition="4" position="150,4"  size="200,22" font="Regular;19" backgroundColor="#00000000" foregroundColor="#00ff0000" halign="right"/>
	
	<eLabel text="Premium" position="572,4" size="64,16" font="Regular;14" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="1" />
	<ePixmap zPosition="1" position="640,4" size="46,16" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/premium_off.png" />
	<widget source="premiumUser" render="Pixmap" position="640,4" size="46,16" zPosition="2" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/premium_on.png">
      <convert type="ConditionalShowHide" />
    </widget>
    
    <eLabel text="Proxy" position="572,24" size="64,16" font="Regular;14" backgroundColor="#00000000" foregroundColor="#00ffffff" transparent="1" />
	<ePixmap zPosition="1" position="640,24" size="46,16" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/proxy_off.png" />
	<widget source="useProxy" render="Pixmap" position="640,24" size="46,16" zPosition="2" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/proxy_on.png">
      <convert type="ConditionalShowHide" />
    </widget>
</screen>"""

"""<screen name="AirPlayMusicPlayer" position="272,96" size="480,362" title="AirPlayMusicPlayer" flags="wfNoBorder" > 
    <widget source="label_update"  transparent="2" render="Label" zPosition="4" position="0,0"  size="480,22" font="Regular;19" backgroundColor="#00000000" foregroundColor="#00ff0000" />
    <widget name="label_message"  transparent="2" zPosition="4" position="0,24"  size="480,48" font="Regular;22" backgroundColor="#00000000" foregroundColor="#00ff0000" />
    <widget name="cover" position="0,72" size="240,240" zPosition="1" alphatest="on" />
    <widget name="label_title"  transparent="2" zPosition="4" position="244,80"  size="232,40" font="Regular;18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center"/>
    <widget name="label_album"  transparent="2" zPosition="4" position="244,120"  size="232,40" font="Regular;18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center"/>
    <widget name="label_interpret"  transparent="2" zPosition="4" position="244,160"  size="232,40" font="Regular;18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center"/>
    <ePixmap zPosition="-1" position="256,240" size="208,6" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/progress_grey_small.png" />
    <widget name="progress" position="256,240" size="208,6" zPosition="1" transparent="1" pixmap="%s/Extensions/AirPlayer/Skins/Classic/1024x576/progress_small.png" />
</screen>"""

#</skin>
