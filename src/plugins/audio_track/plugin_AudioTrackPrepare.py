# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import re
import sqlite3

from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase


class AudioTrackPrepare(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        


    def process(self, **kwargs):
        self.__prepare_file_structure()
        self.__parse_language()



    def __prepare_file_structure(self):
        
        pass



    def __parse_language(self):
        if 'language' not in self.env["cmd_known_args"]:
            self.logger.warning("the 'languade' argument is absent")
            return

        m = re.match(self.env["regex_language"]
            , self.env["cmd_known_args"].language)

        if not m:
            raise SlProgramStatus("Command line argument error:",
                "flag '--language' incorrect value, syntax: --language en-en")

        self.env["term_lang"] = m.group(1)
        self.env["definition_lang"] = m.group(2)
