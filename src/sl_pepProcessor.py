import os
import json
import sys

sys.path.insert(1, './plugins')

from sl_logger import Logger
from sl_env import Env
from sl_pluginLoader import PluginLoader

from sl_exceptions import SlPluginStatus \
    , SlPluginEntryPointStatus \
    , SlProgramStatus


class PluginEntryPointProcessor:
    def __init__(self, env, plugin_entry_point_name):
        self._pep_name = plugin_entry_point_name
        self._env = env
        self.__init_pep()



    def __init_pep(self):
        self.logger = Logger().get_logger()
        self.logger.info("starting pep: {}".format(self._pep_name))

        pep_file = "{}/{}.env.json".format(
            self._env["sl_cfg_pep_dir"], self._pep_name)

        self._env.append_env(pep_file)
        


    def process(self, **kwargs):
        for plugin_name in self._env["plugins"]:
            try:
                PluginLoader(self._env, plugin_name).process(**kwargs)

            except SlPluginStatus as status:
                self.logger.warning(
                    "plugin '{}' has finished with status: {}".format(
                    plugin_name, status))

            except SlPluginEntryPointStatus as status:
                self.logger.warning(
                    "plugin '{}' has finished with status: {}".format(
                    plugin_name, status))
                break;

            except SlProgramStatus as status:
                self.logger.warning(
                    "plugin '{}' has finished with status: {}".format(
                    plugin_name, status))
                sys.exit()



