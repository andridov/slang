# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import subprocess

from plugin_Base import PluginBase

class SaveAudioFromFile(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        if "out_file" not in kwargs:
            raise Exception("the destination file is absent,"\
                " specify the 'out_file' parameter for this plugin")



        command = []
        for cn in self.env["command_param_names"]:
            command.append(self.env[cn])
            
        self.logger.info("saving audio: {}".format(command))
        subprocess.run(command)
        self.logger.info("audio track saved")

