import wx

from plugin_Base import PluginBase



class TestGUIComponents(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        self.logger = self.env['logger']

    def process(self):
        PluginLoader(env, "TestGUIComponents").process({'c':56})


   