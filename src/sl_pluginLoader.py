# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sys

from sl_env import Env

sys.path.insert(1, './plugins')


class PluginLoader:
    def __init__(self, env, plugin):
        plugin_path = ""
        plugin_class_name = plugin

        if plugin.find('/') != -1:
            plugin_path = plugin[0:plugin.rindex('/')]
            sys.path.insert(2, "./plugins/" + plugin_path)
            plugin_class_name = plugin[plugin.rindex('/')+1:]

        self._plugin_name = plugin_class_name
        self._plugin_module = "plugin_{}".format(plugin_class_name)

        module = __import__(self._plugin_module)
        plugin_class_ = getattr(module, self._plugin_name)

        self._plugin = plugin_class_(env, self._plugin_name
            , plugin_path=plugin_path)


    def process(self, **kwargs):
        result = self._plugin.process(**kwargs)
        self._plugin.env.populate_parent_env()
        
        return result


