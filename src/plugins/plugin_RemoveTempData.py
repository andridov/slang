# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import os
import glob
import shutil

from plugin_Base import PluginBase

class RemoveTempData(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        for pattern_key in self.env["remove_file_patterns"]:
            pattern = self.env[pattern_key]
            self.logger.debug("deleting {}:".format(pattern))
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path): 
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.error(e)
