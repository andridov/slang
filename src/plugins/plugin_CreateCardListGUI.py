import wx
import sys

from plugin_Base import PluginBase
from sl_logger import Logger

sys.path.insert(1, './plugins/common')
from mainFormGUI import MainFormGUI



class CreateCardListGUI(PluginBase):

    def __init__(self, env, name):
        super().__init__(env, name)
        self.__app = wx.App(False)
        self.logger.info('CreateCardGUI is initialized, starting to build GUI')
        self.__mf_gui = MainFormGUI(self.env)
        self.logger.info('building GUI - done')


    def process(self, param_map=None):
        self.logger.info('show GUI ...')
        self.__app.MainLoop()
        self.logger.info('GUI closed!')


