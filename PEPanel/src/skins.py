#!/usr/bin/python
# -*- coding: utf-8 -*-
from Screens.Screen import Screen


class Extramenu(Screen):

    skin = """
	<screen position="center,center" size="580,400" title="" >
		<!--ePixmap position="50,100" size="150,150" pixmap="~/pictures/extrasetup.png" alphatest="on" />
		<widget name="pixmap" position="50,100" size="150,150" alphatest="blend" /-->

                <widget name="list" position="80,50" size="500,350" scrollbarMode="showOnDemand" />
		<!--eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" /-->

	        <ePixmap name="green"    position="80,350"   zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
	        <ePixmap name="blue"  position="220,350" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
	        <ePixmap name="red" position="360,350" zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
        	<!--ePixmap name="red"   position="430,300" zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" /-->

        	<widget name="key_green" position="80,350" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
        	<widget name="key_blue" position="220,350" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
                <widget name="key_red" position="360,350" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
        	<!--widget name="key_red" position="430,300" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /-->
        </screen>"""


class Menusimple(Screen):

    skin = """
        	<screen position="center,center" size="580,350" title="" >

                <widget name="list" position="75,50" size="500,250" scrollbarMode="showOnDemand" />
		<!--eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" /-->

	        <ePixmap name="red"    position="10,300"   zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
	        <ePixmap name="green"  position="150,300" zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
	        <ePixmap name="yellow" position="290,300" zPosition="2" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
        	<ePixmap name="blue"   position="430,300" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />

        	<widget name="key_red" position="10,300" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
        	<widget name="key_green" position="150,300" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
                <widget name="key_yellow" position="290,300" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
        	<widget name="key_blue" position="430,300" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
        </screen>"""


class ItemList(Screen):

    skin = """

                 <screen position="center,center" size="1280,720" title="Choice Box" flags="wfNoBorder">
                 <ePixmap position="40,30" zPosition="-10" size="1200,660" pixmap="~/pictures/pepanelbck.png" alphatest="on" />
                 <!--eLabel text="Choice Box" position="700,80" size="400,50" font="Regular;40" halign="right" backgroundColor="#00151515" transparent="1" /-->
                 <widget name="title" position="770,80" size="400,50" font="Regular;40" halign="center" backgroundColor="#00151515" transparent="1" />

                 <widget name="text" position="80,240" size="550,25" font="Regular;22" />
                 <widget name="list" position="80,330" size="500,250"  itemHeight="32" selectionPixmap="~/pictures/sel900x30.png" scrollbarMode="showOnDemand" transparent="1" />

                 <ePixmap position="584,184" size="610,370" pixmap="~/pictures/pig1.png" alphatest="on" />
    <!--widget source="session.CurrentService" render="Label" position="690,220" zPosition="3" size="480,30" font="Regular;25" halign="center" valign="center" noWrap="1" foregroundColor="grey" backgroundColor="#00151515" transparent="1"-->
    <widget source="session.CurrentService" render="Label" position="584,205" zPosition="3" size="580,30" font="Regular;25" halign="center" valign="center" noWrap="1" foregroundColor="grey" backgroundColor="#00151515" transparent="1">

      <convert type="ServiceName">Name</convert>
    </widget>
    <!--widget source="session.VideoPicture" render="Pig" position="790,170" size="370,370" zPosition="1" backgroundColor="unff000000" /-->
    <!--widget source="session.VideoPicture" render="Pig" position="730,220" size="450,252" zPosition="1" backgroundColor="unff000000" /-->
    <widget source="session.VideoPicture" render="Pig" position="600,200" size="550,308" zPosition="1" backgroundColor="unff000000" />

         </screen>"""
