# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from sl_logger import Logger
from sl_env import Env


class PluginBase:
    def __init__(self, env, name, **kwargs):
        self.plugin_name = name
        self.env = env.get_env_obj()
        if "logger" in env:
            self.logger = env["logger"]

        plugin_path = ""
        if kwargs and "plugin_path" in kwargs:
        	plugin_path = "/" + kwargs["plugin_path"] 

        plugin_env_file = "{}{}/sl_plugin_{}.env.json".format(
            self.env["sl_cfg_plugin_dir"], plugin_path, name)

        self.env.append_env(plugin_env_file)




