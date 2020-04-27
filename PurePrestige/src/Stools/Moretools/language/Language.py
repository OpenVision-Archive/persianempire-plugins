# -*- coding: utf-8 -*-
from __future__ import print_function
import gettext
import locale
from Tools.Directories import SCOPE_LANGUAGE, resolveFilename

class Language:

    def __init__(self):
        gettext.install('enigma2', resolveFilename(SCOPE_LANGUAGE, ''), unicode=0, codeset='utf-8')
        self.activeLanguage = 0
        self.lang = {}
        self.langlist = []
        self.addLanguage('Arabic', 'ar', 'AE')
        self.addLanguage('\xd0\x91\xd1\x8a\xd0\xbb\xd0\xb3\xd0\xb0\xd1\x80\xd1\x81\xd0\xba\xd0\xb8', 'bg', 'BG')
        self.addLanguage('Catal\xc3\xa0', 'ca', 'AD')
        self.addLanguage('\xc4\x8cesky', 'cs', 'CZ')
        self.addLanguage('Dansk', 'da', 'DK')
        self.addLanguage('Deutsch', 'de', 'DE')
        self.addLanguage('\xce\x95\xce\xbb\xce\xbb\xce\xb7\xce\xbd\xce\xb9\xce\xba\xce\xac', 'el', 'GR')
        self.addLanguage('English', 'en', 'EN')
        self.addLanguage('Espa\xc3\xb1ol', 'es', 'ES')
        self.addLanguage('Eesti', 'et', 'EE')
        self.addLanguage('Persian', 'fa', 'IR')
        self.addLanguage('Suomi', 'fi', 'FI')
        self.addLanguage('Fran\xc3\xa7ais', 'fr', 'FR')
        self.addLanguage('Frysk', 'fy', 'NL')
        self.addLanguage('Hebrew', 'he', 'IL')
        self.addLanguage('Hrvatski', 'hr', 'HR')
        self.addLanguage('Magyar', 'hu', 'HU')
        self.addLanguage('\xc3\x8dslenska', 'is', 'IS')
        self.addLanguage('Italiano', 'it', 'IT')
        self.addLanguage('Lietuvi\xc5\xb3', 'lt', 'LT')
        self.addLanguage('Latvie\xc5\xa1u', 'lv', 'LV')
        self.addLanguage('Nederlands', 'nl', 'NL')
        self.addLanguage('Norsk', 'no', 'NO')
        self.addLanguage('Polski', 'pl', 'PL')
        self.addLanguage('Portugu\xc3\xaas', 'pt', 'PT')
        self.addLanguage('Romanian', 'ro', 'RO')
        self.addLanguage('\xd0\xa0\xd1\x83\xd1\x81\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9', 'ru', 'RU')
        self.addLanguage('Slovensky', 'sk', 'SK')
        self.addLanguage('Sloven\xc5\xa1\xc4\x8dina', 'sl', 'SI')
        self.addLanguage('Srpski', 'sr', 'YU')
        self.addLanguage('Svenska', 'sv', 'SE')
        self.addLanguage('\xe0\xb8\xa0\xe0\xb8\xb2\xe0\xb8\xa9\xe0\xb8\xb2\xe0\xb9\x84\xe0\xb8\x97\xe0\xb8\xa2', 'th', 'TH')
        self.addLanguage('T\xc3\xbcrk\xc3\xa7e', 'tr', 'TR')
        self.addLanguage('Ukrainian', 'uk', 'UA')
        self.callbacks = []

    def addLanguage(self, name, lang, country):
        try:
            self.lang[str(lang + '_' + country)] = (name, lang, country)
            self.langlist.append(str(lang + '_' + country))
        except:
            print('Language ' + str(name) + ' not found')

    def activateLanguage(self, index):
        try:
            lang = self.lang[index]
            print('Activating language ' + lang[0])
            gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ''), languages=[lang[1]]).install(names='ngettext')
            self.activeLanguage = index
            for x in self.callbacks:
                x()

        except:
            print('Selected language does not exist!')

        try:
            locale.setlocale(locale.LC_TIME, self.getLanguage())
        except:
            print('Failed to set LC_TIME to ' + self.getLanguage() + ". Setting it to 'C'")
            locale.setlocale(locale.LC_TIME, 'C')

    def activateLanguageIndex(self, index):
        if index < len(self.langlist):
            self.activateLanguage(self.langlist[index])

    def getLanguageList(self):
        return [ (x, self.lang[x]) for x in self.langlist ]

    def getActiveLanguage(self):
        return self.activeLanguage

    def getActiveLanguageIndex(self):
        idx = 0
        for x in self.langlist:
            if x == self.activeLanguage:
                return idx
            idx += 1

    def getLanguage(self):
        try:
            return str(self.lang[self.activeLanguage][1]) + '_' + str(self.lang[self.activeLanguage][2])
        except:
            return ''

    def addCallback(self, callback):
        self.callbacks.append(callback)

    def precalcLanguageList(self):
        T1 = _('Please use the UP and DOWN keys to select your language. Afterwards press the OK button.')
        T2 = _('Language selection')
        l = open('language_cache.py', 'w')
        print(>> l, 'LANG_TEXT = {')
        for language in self.langlist:
            self.activateLanguage(language)
            print(>> l, '"%s": {' % language)
            print(>> l, '\t"T1": "%s",' % _(T1))
            print(>> l, '\t"T2": "%s",' % _(T2))
            print(>> l, '},')

        print(>> l, '}')


language = Language()
