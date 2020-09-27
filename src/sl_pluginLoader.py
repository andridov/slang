import os
import sys

from sl_env import Env

sys.path.insert(1, './plugins')
sys.path.insert(2, './plugins/update_words_db')
sys.path.insert(3, './plugins/keystroke')



class PluginLoader:
    def __init__(self, env, plugin_class_name):
        self._plugin_name = plugin_class_name
        self._plugin_module = "plugin_{}".format(plugin_class_name)

        module = __import__(self._plugin_module)
        plugin_class_ = getattr(module, self._plugin_name)
        self._plugin = plugin_class_(env, self._plugin_name)


    def process(self, param_map=None):
        self._plugin.process(param_map)
        self._plugin.env.populate_parent_env()


