# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import wx
import json

from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader


class KeystrokeCreateGUI(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        self.__app = wx.App(False)
        self.logger.info('initializing GUI')
        self.__build_gui()
        self.logger.info('building GUI - done')



    def process(self, **kwargs):
        self.logger.info('show GUI ...')
        self.__app.MainLoop()
        self.logger.info('GUI closed!')



    def __build_gui(self):
        self.__root_win = wx.Frame(None, wx.ID_ANY
            , pos=(self.env["ui_x_pos"], self.env["ui_y_pos"]))
        self.__root_win.SetTitle("{} ({}-{})".format(
            self.env["prj_name"]
            , self.env["term_lang"]
            , self.env["definition_lang"]))
        self.__close_callback = None

        self.__root_win.Bind(wx.EVT_CLOSE, self.__on_close)

        self.env["win_panel"] = wx.Panel(self.__root_win)
        
        if not "test" in self.env["cmd_other_args"]:
            PluginLoader(self.env, "keystroke/StartSpeedGUI").process()
        else:
            PluginLoader(self.env, "keystroke/StartTestGUI").process()

        self.__root_win.SetSize((self.env["ui_x_size"], self.env["ui_y_size"]))
        self.__root_win.Show(True)



    def __on_close(self, evt):
        self.__save_current_geometry()
        evt.Skip()



    def __save_current_geometry(self):
        if "prj_ui_geometry_file" not in self.env:
            return

        # get curent window geometry
        x, y = self.__root_win.GetPosition()
        width, height = self.__root_win.GetSize()

        state = []
        state.append({"ui_x_pos": x})
        state.append({"ui_y_pos": y})
        state.append({"ui_x_size": width})
        state.append({"ui_y_size": height})

        self.logger.info("saving current windowgeometry state: {}".format(
            state))

        with open(self.env["prj_ui_geometry_file"], 'w') as jf:
            json.dump(state, jf,
                indent=2, ensure_ascii=False, sort_keys=False)


