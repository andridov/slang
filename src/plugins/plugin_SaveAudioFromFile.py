import subprocess

from plugin_Base import PluginBase

class SaveAudioFromFile(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        command = []
        for cn in self.env["command_param_names"]:
            command.append(self.env[cn])
            
        self.logger.info("saving audio: {}".format(command))
        subprocess.run(command)
        self.logger.info("audio track saved")

