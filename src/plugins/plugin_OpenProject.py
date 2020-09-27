import wx
import wx.adv
import re
import sys
import json
import os

from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader



class OpenProject(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)

        

    def process(self, params_map):
        if self.__all_data_present():
            return

        self.__proj_selected = False
        self.__draw_gui()
        self.__show_gui()




    def __all_data_present(self):
        # possibly all the data needed to start project were setted via
        # command line. 
        if not self.env["cmd_known_args"] \
            or not self.env["cmd_known_args"].project_name:
            return False
    
        known_args = self.env["cmd_known_args"]
        self.env["sl_project_name"] = known_args.project_name

        if known_args.create_project:
            self.__create_new_project()
            # no need to show "Create/Open dialog"
            return True

        if known_args.delete_project:
            self.__delete_existing_project()
            # just close the program.
            sys.exit()

        return False


    def __create_new_project(self):
        PluginLoader(self.env, "CreateNewProject").process()
        self.__save_overrides()
        self.__save_geometry_overrides()


    def __load_existing_project(self):
        self.__load_overrides()


    def __delete_existing_project(self):
        PluginLoader(self.env, "DeleteExistingProject").process()



    def __load_overrides(self):
        overrides_file = "{}/{}/{}".format(
            self.env["sl_projects_dir"]
            , self.env["sl_project_name"]
            , self.env["overrides_rel_path_file"])

        self.env.append_env(overrides_file)



    def __save_overrides(self):
        # save overrides file
        overrides = []
        for k_name in ["sl_project_name"
            , "term_lang", "definition_lang", "show_video_tab"]:
            overrides.append({k_name: self.env[k_name]})

        overrides_file = "{}/{}/{}".format(
            self.env["sl_projects_dir"]
            , self.env["sl_project_name"]
            , self.env["overrides_rel_path_file"])

        with open(overrides_file, 'w') as jf:
            json.dump(
                overrides, jf, indent=2, ensure_ascii=False, sort_keys=False)



    def __save_geometry_overrides(self):
        # save current geometry
        x, y = self.__root_win.GetPosition()
        width, height = self.__root_win.GetSize()

        state = []
        state.append({"ui_x_pos": x})
        state.append({"ui_y_pos": y})
        state.append({"ui_x_size": width})
        state.append({"ui_y_size": height})

        with open(self.env["ui_open_geometry_file"], 'w') as jf:
            json.dump(state, jf, indent=2, ensure_ascii=False, sort_keys=False)




    def __show_gui(self):
        self.__root_win.Show(True)
        self.__app.MainLoop()



    def __draw_gui(self):
        self.__app = wx.App(False)
        self.__root_win = wx.Frame(None, wx.ID_ANY
            , pos=(self.env["ui_x_pos"], self.env["ui_y_pos"]))
        self.__root_win.SetTitle("Slang Projects")
        self.__root_win.Bind(wx.EVT_CLOSE, self.__on_close)

        p = wx.Panel(self.__root_win)
        sizer = wx.GridBagSizer()

        row = 0
        col = 0

        tabs_panel_row = row
        self.tp = wx.Notebook(p)
        self.tp_new_proj = NewProjPanel(self.tp, self)
        self.tp_existing_proj = ExistingProjPanel(self.tp, self)
        sizer.Add(self.tp, pos =(0, 0), flag = wx.EXPAND|wx.ALL)

        sizer.AddGrowableRow(tabs_panel_row)
        sizer.AddGrowableCol(col)
        p.SetSizerAndFit(sizer)
        self.__root_win.SetSize((self.env["ui_x_size"], self.env["ui_y_size"]))


    def __on_close(self, evt):
        evt.Skip()


    def create_new_poject(self):
        self.__proj_selected = True
        self.logger.info("creating project name = {}".format(
            self.env["sl_project_name"]))
        self.__root_win.Close()
        # creates empty projcet structure
        self.__create_new_project()


    def open_existing_project(self):
        self.__proj_selected = True
        self.logger.info("opening project name = {}".format(
            self.env["sl_project_name"]))
        self.__root_win.Close()
        self.__load_existing_project()


    def delte_existing_project(self):
        self.logger.info("Deleting is not implemented now, you have to delete" \
            " project mannualy by deleting folder {}/{}".format(
                self.env["sl_projects_dir"], self.env["sl_project_name"]))



class NewProjPanel:
    def __init__(self, tp, op_instance):
        self.op = op_instance
        p = wx.Panel(tp)
        self.__draw_panel(p)
        tp.AddPage(p, "New project")


    def __draw_panel(self, p):
        sizer = wx.GridBagSizer()

        row = 0
        col = 0

        # project name
        lbl_prj_name = wx.StaticText(p, -1, "project name")
        sizer.Add(lbl_prj_name
            , pos=(row, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.txt_prj_name = wx.TextCtrl(p)
        sizer.Add(self.txt_prj_name
            , pos=(row, 1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.txt_prj_name.Bind(wx.EVT_TEXT, self.__on_txt_edit_prj_name)

        # term language
        row += 1
        lbl_term_lang = wx.StaticText(p, -1, "term language code*")
        sizer.Add(lbl_term_lang
            , pos=(row, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.txt_term_lang = wx.TextCtrl(p)
        sizer.Add(self.txt_term_lang
            , pos=(row, 1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.txt_term_lang.Bind(wx.EVT_TEXT, self.__on_txt_edit)

 
        # definition language
        row += 1
        lbl_def_lang = wx.StaticText(p, -1, "definition language code*")
        sizer.Add(lbl_def_lang
            , pos=(row, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.txt_definition_lang = wx.TextCtrl(p)
        sizer.Add(self.txt_definition_lang
            , pos=(row, 1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.txt_definition_lang.Bind(wx.EVT_TEXT, self.__on_txt_edit)

        # language codes
        row += 1
        lbl_lang_code_star = wx.StaticText(p, -1, "*list of ISO 639-1 codes:")
        sizer.Add(lbl_lang_code_star
            , pos=(row, 0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        lnk_lang_code_star = wx.adv.HyperlinkCtrl(p, -1,
            "https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes")
        sizer.Add(lnk_lang_code_star
            , pos=(row, 1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        # video check box
        row += 1
        self.cb_video = wx.CheckBox(p, label='Show video tab')
        self.cb_video.SetValue(True)
        sizer.Add(self.cb_video
            , pos=(row, 1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

        # button OK
        row += 1
        self.btn_ok = wx.Button(p, label="OK")
        self.btn_ok.Enable(False)
        sizer.Add(self.btn_ok, pos=(row, 0), span=(0, 2) 
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)
        p.Bind(wx.EVT_BUTTON, self.__on_btn_ok,  self.btn_ok)

        
        sizer.AddGrowableRow(row)
        sizer.AddGrowableCol(1)
        p.SetSizerAndFit(sizer)


    def __on_txt_edit_prj_name(self, evt):
        text = self.txt_prj_name.GetValue()
        new_text = re.sub(' ', '', text)
        if text != new_text:
            self.txt_prj_name.SetValue(new_text)
            self.txt_prj_name.SetInsertionPoint(len(new_text))
        self.__try_enable_btn_ok()


    def __on_txt_edit(self, evt):
        self.__try_enable_btn_ok()


    def __try_enable_btn_ok(self):
        self.btn_ok.Enable(
            len(self.txt_prj_name.GetValue()) > 0
            and len(self.txt_term_lang.GetValue()) > 0
            and len(self.txt_definition_lang.GetValue()) > 0)


    def __on_btn_ok(self, evt):
        self.op.env["sl_project_name"] = self.txt_prj_name.GetValue()
        self.op.env["term_lang"] = self.txt_term_lang.GetValue()
        self.op.env["definition_lang"] = self.txt_definition_lang.GetValue()
        self.op.env["show_video_tab"] = self.cb_video.GetValue()
        self.op.create_new_poject()




class ExistingProjPanel:
    def __init__(self, tp, op_instance):
        p = wx.Panel(tp)
        self.op = op_instance
        self.__draw_panel(p)
        tp.AddPage(p, "Existing Project")


    def __draw_panel(self, p):
        sizer = wx.GridBagSizer()

        row = 0
        self._trc_list = wx.TreeCtrl(p, wx.ID_ANY)
        sizer.Add(self._trc_list
            , pos = (0, 0), span=(row, 1), flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM)
        p.Bind(wx.EVT_TREE_SEL_CHANGED, self.__on_item_changed, self._trc_list)
        self.__show_projects()
        self._trc_list.ExpandAll()


        # button OK
        row += 1
        self.btn_ok = wx.Button(p, label="OK")
        self.btn_ok.Enable(False)
        sizer.Add(self.btn_ok, pos=(row, 0), span=(0, 2) 
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)
        p.Bind(wx.EVT_BUTTON, self.__on_btn_ok,  self.btn_ok)

    
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)



    def __show_projects(self):
        projects = self._trc_list.AddRoot("Existing_Projects")
        for d in os.listdir(self.op.env["sl_projects_dir"]):
            self._trc_list.AppendItem(projects, d)



    def __on_item_changed(self, evt):
        item_selected = self._trc_list.GetSelection()
        root_item = self._trc_list.GetRootItem()

        self.btn_ok.Enable(item_selected != root_item)



    def __on_btn_ok(self, evt):
        item_selected = self._trc_list.GetSelection()
        self.op.env["sl_project_name"] = \
            self._trc_list.GetItemText(item_selected)

        self.op.open_existing_project()