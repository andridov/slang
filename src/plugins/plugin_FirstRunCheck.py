# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import sys
import json
import os

from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader



class FirstRunCheck(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)

        

    def process(self, **kwargs):
        self.__check_directories()



    def __check_directories(self):
        for dir_name in self.env["mandatory_directories"]:
            if not dir_name in self.env:
                self.logger.error("environment variable is absent: {}. "\
                    "Can't create dir".format(dir_name))
            if not os.path.exists(self.env[dir_name]):
                os.makedirs(self.env[dir_name])


