from sl_logger import Logger
from sl_env import Env


class PluginBase:
    def __init__(self, env, name):
        self.plugin_name = name
        self.env = env.get_env_obj()
        if "logger" in env:
            self.logger = env["logger"]

        plugin_env_file = "{}/sl_plugin_{}.env.json".format(
            self.env["sl_cfg_plugin_dir"], name)

        self.env.append_env(plugin_env_file)




