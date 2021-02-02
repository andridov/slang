# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import wx
import wx.richtext
import wx.lib.newevent
import re
import vlc
import sys
import json
import time
import urllib.parse
import urllib.request
from copy import deepcopy

from plugin_Base import PluginBase
from sl_pepProcessor import PluginEntryPointProcessor
from sl_pluginLoader import PluginLoader
from sl_exceptions import SlProgramStatus
from sl_logger import Logger
from subtitles import SubTitle


class MainFormGUI:
    def __init__(self, env):
        self.env = env;
        self.logger = self.env["logger"]

        self.__build_gui()
        self.env["tab_ids_list"] = [
            self.__fv_base
            , self.__fv_ex_1
            , self.__fv_ex_2
            , self.__fv_ex_3
            , self.__fv_ex_4
            , self.__fv_ex_5
        ]


    def __build_gui(self):
        self.__root_win = wx.Frame(None, wx.ID_ANY
            , pos=(self.env["ui_x_pos"], self.env["ui_y_pos"]))
        self.__root_win.SetTitle("{} ({}-{})".format(
            self.env["prj_name"]
            , self.env["term_lang"]
            , self.env["definition_lang"]))
        self.__close_callback = None
        self.__root_win.Bind(wx.EVT_CLOSE, self.__on_close)


        p = wx.Panel(self.__root_win)
        self.c_nb = wx.Notebook(p)
        sizer = wx.GridBagSizer()

        self.__fv_video = None
        if self.env["show_video_tab"]:
            self.__fv_video = VideoTab(
                self.c_nb, "Video", self.env, self.logger)

            if "subtitle_term_font_scale" in self.env:
                self.__fv_video.subt_1.SetFontScale(
                    self.env["subtitle_term_font_scale"])
            if "subtitle_definition_font_scale" in self.env:
                self.__fv_video.subt_2.SetFontScale(
                    self.env["subtitle_definition_font_scale"])

        self.__fv_base = CardTab(self.c_nb, "Base", self.env, self.logger)
        self.__fv_ex_1 = CardTab(self.c_nb, "Ex 1", self.env, self.logger)
        self.__fv_ex_2 = CardTab(self.c_nb, "Ex 2", self.env, self.logger)
        self.__fv_ex_3 = CardTab(self.c_nb, "Ex 3", self.env, self.logger)
        self.__fv_ex_4 = CardTab(self.c_nb, "Ex 4", self.env, self.logger)
        self.__fv_ex_5 = CardTab(self.c_nb, "Ex 5", self.env, self.logger)
        sizer.Add(self.c_nb, pos =(0, 0), flag = wx.EXPAND|wx.ALL)

        self.__btn_add_data = wx.Button(p
            , label="Add data to collection", size=(0,40))
        sizer.Add(self.__btn_add_data, pos = (1, 0), flag = wx.EXPAND|wx.ALL)
        self.__btn_add_data.Bind(wx.EVT_BUTTON, self.__on_btn_add_data)
        #set handler add_data_to_collection

        p.SetSizer(sizer)
        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)
        self.__root_win.SetSize((self.env["ui_x_size"], self.env["ui_y_size"]))

        self.__create_accel_table(self.__root_win)

        self.__root_win.Show(True)


    def __create_accel_table(self, win):
        ctrQ_id = wx.NewId()
        ctrEnter_id = wx.NewId()
        ctrl0_id = wx.NewId()
        ctrl1_id = wx.NewId()
        ctrl2_id = wx.NewId()
        ctrl3_id = wx.NewId()
        ctrl4_id = wx.NewId()
        ctrl5_id = wx.NewId()
        ctrl6_id = wx.NewId()

        win.Bind(wx.EVT_MENU, self.__on_form_quit, id=ctrQ_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_add_data, id=ctrEnter_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_0, id=ctrl0_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_1, id=ctrl1_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_2, id=ctrl2_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_3, id=ctrl3_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_4, id=ctrl4_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_5, id=ctrl5_id)
        win.Bind(wx.EVT_MENU, self.__on_btn_set_tab_6, id=ctrl6_id)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('Q'), ctrQ_id),
            (wx.ACCEL_CTRL, wx.WXK_RETURN, ctrEnter_id),
            (wx.ACCEL_CTRL, ord('1'), ctrl0_id),
            (wx.ACCEL_CTRL, ord('2'), ctrl1_id),
            (wx.ACCEL_CTRL, ord('3'), ctrl2_id),
            (wx.ACCEL_CTRL, ord('4'), ctrl3_id),
            (wx.ACCEL_CTRL, ord('5'), ctrl4_id),
            (wx.ACCEL_CTRL, ord('6'), ctrl5_id),
            (wx.ACCEL_CTRL, ord('7'), ctrl6_id)
            ])
        win.SetAcceleratorTable(accel_tbl)


    def __get_empty_tab_obj(self):
        for obj in [ [self.__fv_base, 1]
            , [self.__fv_ex_1, 2]
            , [self.__fv_ex_2, 3]
            , [self.__fv_ex_3, 4]
            , [self.__fv_ex_4, 5]
            , [self.__fv_ex_5, 6] ]:

            if not obj[0].term.GetValue():
                return obj

        self.logger.warning("All tabs are full")
        return None


    def __on_btn_add_data(self, event):
        if (self.env["show_video_tab"]
            and self.__fv_video
            and self.c_nb.GetSelection() == 0):

            tab_obj = self.__get_empty_tab_obj()
            if not tab_obj:
                return

            self.__fv_video.save_snapshot_file()
            tab_obj[0].term.SetValue(self.__fv_video.get_term_text())
            tab_obj[0].definition.SetValue(
                self.__fv_video.get_definition_text())
            tab_obj[0].load_video_file()
            
            if self.__fv_video and self.__fv_video.subtitle_1:
                from_to = self.__fv_video.subtitle_1.get_from_to(
                    self.__fv_video.time)
                if from_to:
                    self.env["current_subtitle1_from"] = from_to[0]
                    self.env["current_subtitle1_to"] = from_to[1]
            tab_obj[0].load_audio_file()


            # move to the Base tab
            self.c_nb.SetSelection(tab_obj[1])

            return


        if (self.__fv_base.term.GetValue() == ""
            or self.__fv_base.definition.GetValue() == ""):
            return

        self.env["card_item"] = deepcopy(self.env["card_item_template"])

        pepp = PluginEntryPointProcessor(self.env, "sl_pep_AddCardItemToList")
        pepp.process()

        self.__clear_data()


        if (self.env["show_video_tab"] and self.__fv_video):
            self.__fv_video.time_slider.SetFocus()
        else:
            self.__fv_base.term.SetFocus()



    def __on_close(self, evt):
        if (self.__fv_video):
            self.__fv_video.save_current_state()

        self.__save_current_geometry()
        evt.Skip()



    def __on_btn_set_tab_0(self, evt):
        self.c_nb.SetSelection(0)
        evt.Skip()

    def __on_btn_set_tab_1(self, evt):
        self.c_nb.SetSelection(1)
        evt.Skip()

    def __on_btn_set_tab_2(self, evt):
        self.c_nb.SetSelection(2)
        evt.Skip()

    def __on_btn_set_tab_3(self, evt):
        self.c_nb.SetSelection(3)
        evt.Skip()

    def __on_btn_set_tab_4(self, evt):
        self.c_nb.SetSelection(4)
        evt.Skip()

    def __on_btn_set_tab_5(self, evt):
        self.c_nb.SetSelection(5)
        evt.Skip()

    def __on_btn_set_tab_6(self, evt):
        if (self.env["show_video_tab"]
            and self.__fv_video):
            self.c_nb.SetSelection(6)
        evt.Skip()

    def __clear_data(self):
        for fv in [self.__fv_base
            , self.__fv_ex_1
            , self.__fv_ex_2
            , self.__fv_ex_3
            , self.__fv_ex_4
            , self.__fv_ex_5]:
            fv.clear_data()

        self.c_nb.SetSelection(0)


    def __on_form_quit(self, event):
        self.__root_win.Close()



    def __get_curr_tab_obj(self):
        return [self.__fv_base
            , self.__fv_ex_1
            , self.__fv_ex_2
            , self.__fv_ex_3
            , self.__fv_ex_4
            , self.__fv_ex_5][self.c_nb.GetSelection()]



    def __save_current_geometry(self):
        if "sl_ccl_geometry_file" not in self.env:
            return

        # get curent window geometry
        x, y = self.__root_win.GetPosition()
        width, height = self.__root_win.GetSize()

        state = []
        state.append({"ui_x_pos": x})
        state.append({"ui_y_pos": y})
        state.append({"ui_x_size": width})
        state.append({"ui_y_size": height})

        if "show_video_tab" in self.env and self.__fv_video:
            state.append({"subtitle_term_font_scale": 
                self.__fv_video.subt_1.GetFontScale()})
            state.append({"subtitle_definition_font_scale": 
                self.__fv_video.subt_2.GetFontScale()})

        self.logger.info("saving current windowgeometry state: {}".format(
            state))

        full_file_name = "{}/{}".format( self.env["prj_config_local_dir"]
            , self.env["sl_ccl_geometry_file"])

        with open(full_file_name, 'w') as jf:
            json.dump(state, jf,
                indent=2, ensure_ascii=False, sort_keys=False)




#drag-n-drop handler: text
class TextDropTarget(wx.TextDropTarget):
    def __init__(self, textCtrl):
        wx.TextDropTarget.__init__(self)
        self.textCtrl = textCtrl


    def OnDropText(self, x, y, data):
        self.textCtrl.SetValue(data)
        return True



#drag-n-drop handler: text
class ImageDropTarget(wx.FileDropTarget):
    def __init__(self, tabCtrl, imgCtrl):
        wx.TextDropTarget.__init__(self)
        self.tabCtrl = tabCtrl
        self.imgCtrl = imgCtrl


    def OnDropText(self, x, y, data):
        self.tabCtrl.logger.info("dropped: {}".format(data))
        return True



class AudioEdit(wx.TextCtrl):
    def __init__(self, parent):
        self.__audio_data = None
        super().__init__(parent)


    def SetValue(self, value):
        if os.path.isfile(value):
            with open(value, "rb") as af :
                self.__audio_data = bytearray(af.read())
            value = "[audio_data]"

        super().SetValue(value)


    def has_audio_data(self):
        return True if self.__audio_data else False


    def save_data_to_file(self, file_name):
        edit_value = super().GetValue()
        if self.__audio_data and edit_value == "[audio_data]":
            with open(file_name, "wb") as af:
                af.write(self.__audio_data)
            return True

        return False


    def clear(self):
        self.__audio_data = None
        super().SetValue("")



class CardTab:
    def __init__(self, nb, caption, env, logger):
        self.env = env
        self.logger = logger
        self.caption = caption

        p = wx.Panel(nb)
        sizer = wx.GridBagSizer()
        self.tab_sizer = sizer


        row = 0 #term
        lbl_term = wx.StaticText(p, -1, "term")
        sizer.Add(lbl_term
            , pos=(row, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.term = wx.TextCtrl(p)
        self.__set_bgcolor(self.term, True)
        sizer.Add(self.term
            , pos=(row, 1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.term.SetDropTarget(TextDropTarget(self.term))


        row += 1 #term_note
        lbl_term_note = wx.StaticText(p, -1, "term_note")
        sizer.Add(lbl_term_note
            , pos = (row, 0)
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.term_note = wx.TextCtrl(p)
        self.__set_bgcolor(self.term_note)
        sizer.Add(self.term_note,
            pos = (row, 1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.term_note.SetDropTarget(TextDropTarget(self.term_note))


        row += 1 #term_audio
        btn_term_audio = wx.Button(p, label="play/load")
        sizer.Add(btn_term_audio
            , pos=(row, 0)
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.term_audio = AudioEdit(p)
        self.__set_bgcolor(self.term_audio)
        sizer.Add(self.term_audio,
            pos = (row, 1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.term_audio.Bind(wx.EVT_KILL_FOCUS, self.__on_term_audio_change)


        row += 1 #image
        growable_row = row
        self.original_bitmap = wx.Image("{}/media/image/no_image.jpg".format(
                self.env["prj_data_dir"])
            , wx.BITMAP_TYPE_ANY).ConvertToBitmap()


        self.image_window = wx.Panel(p)
        self.image = wx.StaticBitmap(self.image_window)
        self.image_row = row
        self.image_col = 1
        sizer.Add(self.image_window
            , pos=(self.image_row,self.image_col)
            , flag=wx.EXPAND|wx.ALL)
        txt_value = "240x240" if self.caption == "Base" else "160x160"
        self.image.SetBitmap(
             self.bitmap_resize(self.original_bitmap, txt_value))
       
        row += 1 #image_url
        self.image_size = wx.ComboBox(p, -1, value=txt_value, pos=(row,0)
            , choices=[
                "original"
                , "160x160"
                , "240x240"
                , "320x320"
                , "480x480"
                , "720x720"]
            , style=0)
        sizer.Add(self.image_size
            , pos = (row, 0), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.image_url = wx.TextCtrl(p)
        self.__set_bgcolor(self.image_url)
        sizer.Add(self.image_url
            , pos = (row, 1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.image_url.Bind(wx.EVT_TEXT, self.__on_image_url_change)
        self.image_url.Bind(wx.EVT_TEXT_PASTE, self.__on_image_url_paste)
        self.image_url.SetDropTarget(TextDropTarget(self.image_url))

        row += 1
        lbl_definition = wx.StaticText(p, -1, "definition")
        sizer.Add(lbl_definition
            , pos = (row, 0)
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.definition = wx.TextCtrl(p)
        self.__set_bgcolor(self.definition, True)
        sizer.Add(self.definition
            , pos = (row, 1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.definition.Bind(wx.EVT_TEXT, self.__on_definition_change)
        self.definition.SetDropTarget(TextDropTarget(self.definition))

        row += 1 #definition_note
        lbl_definition = wx.StaticText(p, -1, "definition_note")
        sizer.Add(lbl_definition
            , pos = (row, 0)
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.definition_note = wx.TextCtrl(p)
        self.__set_bgcolor(self.definition_note)
        sizer.Add(self.definition_note
            , pos = (row, 1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.definition_note.SetDropTarget(TextDropTarget(self.definition_note))

        row += 1 #definition_audio
        btn_definition_audio = wx.Button(p, label="play/load")
        sizer.Add(btn_definition_audio
            , pos=(row, 0)
            , flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.definition_audio = AudioEdit(p)
        self.__set_bgcolor(self.definition_audio)
        sizer.Add(self.definition_audio
            , pos = (row, 1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT)
        self.definition_audio.Bind(
            wx.EVT_KILL_FOCUS, self.__on_definition_audio_change)

        sizer.AddGrowableRow(growable_row)
        sizer.AddGrowableCol(1)
        p.SetSizerAndFit(sizer)
        self.__create_accel_table(p)

        nb.AddPage(p, self.caption)


    def __create_accel_table(self, win):
        ctrT_id = wx.NewId()
        ctrD_id = wx.NewId()

        win.Bind(wx.EVT_MENU, self.__on_set_term_focus, id=ctrT_id)
        win.Bind(wx.EVT_MENU, self.__on_set_definition_focus, id=ctrD_id)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('T'), ctrT_id),
            (wx.ACCEL_CTRL, ord('D'), ctrD_id) ])
        win.SetAcceleratorTable(accel_tbl)



    def __set_bgcolor(self, control, mandatory=False):
        if not mandatory:
            return;

        redness_grade = 25
        current_color = control.GetBackgroundColour()
        delta = (redness_grade, 0, 0) if current_color[0] < 215 \
            else (0, -redness_grade, -redness_grade)

        color = (current_color[0] + delta[0]
            , current_color[1] + delta[1]
            , current_color[2] + delta[2])
        control.SetBackgroundColour(color)



    def __on_set_term_focus(self, event):
        self.term.SetFocus()



    def __on_set_definition_focus(self, event):
        term_text = self.term.GetValue()

        if not self.definition.GetValue() and term_text \
            and self.env["autotranslate_term_text"] :
            try:
                self.env["translate_text_term"] = term_text
                PluginLoader(self.env, "TranslateText").process()
                self.definition.SetValue(self.env["translate_text_definition"])
            except Exception as e:
                self.logger.error(
                    "translate, status: {}".format(e))

        self.definition.SetFocus()



    def clear_data(self):
        self.term.SetValue("")
        self.term_note.SetValue("")
        self.term_audio.SetValue("")
        self.image_url.SetValue("")
        #reset bitmap
        self.original_bitmap = wx.Image(
            "{}/no_image.jpg".format(self.env["prj_image_dir"])
            , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.image.SetBitmap(self.original_bitmap)

        self.image_size.SetValue(
            "240x240" if self.caption == "Base" else "160x160")
        self.definition.SetValue("")
        self.definition_note.SetValue("")
        self.definition_audio.SetValue("")



    def bitmap_resize(self, image, size_variant=""):
        max_size=0

        if self.original_bitmap is None:
            return None

        if size_variant == "original":
            return self.original_bitmap #image resize not needed
        elif size_variant == "":
            max_size = min(
                self.image_window.GetSize()[0], self.image_window.GetSize()[1])
        elif size_variant == "160x160": max_size = 160
        elif size_variant == "240x240": max_size = 240
        elif size_variant == "320x320": max_size = 320
        elif size_variant == "480x480": max_size = 480
        elif size_variant == "720x720": max_size = 720
        else:
            self.logger.error("bitmap_resize, size is incorrect")

        w = self.original_bitmap.GetWidth()
        h = self.original_bitmap.GetHeight()
        r = max_size/w if w > h else max_size/h
        image = self.original_bitmap.ConvertToImage()

        image = image.Scale(w*r, h*r, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result



    def __image_set_bitmap(self, bitmap):
        out_bitmap = PluginLoader(self.env, "ImageResize").process(
            original_bitmap=
                self.bitmap_resize(bitmap, self.image_size.GetValue())
            , image_size=self.image_window.GetSize())
        
        self.image.SetBitmap(out_bitmap)



    def __paste_image_from_clipboard(self):
        self.clip = wx.Clipboard()
        img = wx.BitmapDataObject()

        self.clip.Open()
        self.clip.GetData(img)
        self.clip.Close()

        self.original_bitmap = img.GetBitmap()
        if self.original_bitmap:
            self.__image_set_bitmap(self.original_bitmap) 
            self.image_url.SetValue("$")



    def load_video_file(self):
        self.load_image_file(self.env["video_snapshot_file"]) 
        self.image_url.SetValue("snapshot")



    def load_image_file(self, src_image):
        img = wx.Image(src_image, wx.BITMAP_TYPE_ANY)
        self.original_bitmap = wx.Bitmap(img)
        self.__image_set_bitmap(self.original_bitmap)



    def load_audio_file(self):

        if not "video_audio_file" in self.env \
            or not self.env["video_audio_file"]:
            return

        dst_file=self.env["prj_temp_dir"] + "/temp_audio_file.mp3"
        if dst_file:
            os.remove(dst_file) 
        PluginLoader(self.env, "CmdRun").process(
            run_file=self.env["audio_file_commands"], out_file=dst_file)
        self.term_audio.SetValue(dst_file)




#*******************************************************************************
# GUI handlers


    def __on_term_audio_change(self, event):
        pass



    def __on_definition_audio_change(self, event):
        pass


    def __on_image_url_paste(self, event):
        self.__paste_image_from_clipboard()
        event.Skip()


    def __on_image_url_change(self, event):
        url = self.image_url.GetValue()
        dst_file=self.env["prj_temp_dir"] + "/temp_img_file"
        result = PluginLoader(self.env, "LoadImageFromUrl").process(url=url
            , dst_file=dst_file)

        if isinstance(result, dict):
            # extended  answer
            if result["status"] == True:
                self.term.SetValue(result["term_text"])
                self.load_image_file(result["image_file"])
                if "definition_text" in result:
                    self.definition.SetValue(result["definition_text"])
                else:
                    self.definition.SetValue("")
                self.term_audio.SetValue(result["audio_file"])
        elif result:
            self.load_image_file(dst_file)



    def __on_definition_change(self, event):
        pass




#*******************************************************************************
# popup menus:

class VideoPopupMenu(wx.Menu):
    def __init__(self, parent):
        super(VideoPopupMenu, self).__init__()
        self.parent = parent


    # delete pervious and reload new context items for audio tracks
    def reload(self, vlc_player):
        # delete perfious items in menu first
        menu_items = self.GetMenuItems()
        for item in menu_items:
            self.Delete(item)

        if not vlc_player:
            return

        self.vlc_player = vlc_player

        # get list of audio tracks from VLC player
        self.audio_items={}
        tracks = vlc_player.audio_get_track_description()
        for track in tracks:
            item_name = "audio: {}".format(track[1])
            menu_id = wx.NewId()
            self.audio_items[menu_id]=track
            mi = wx.MenuItem(self, menu_id, item_name)
            self.Append(mi)
            self.Bind(wx.EVT_MENU, self.__on_video_menu_item_select, id=menu_id)


    def __on_video_menu_item_select(self, e):
        current_id = e.GetId()
        if current_id in self.audio_items:
            track_id = self.audio_items[current_id][0]
            self.vlc_player.audio_set_track(track_id)
            self.parent.env["video_audio_track"] = track_id
            return



class SubtPopupMenu(wx.Menu):
    def __init__(self, subt_object, video_tab_object):
        super(SubtPopupMenu, self).__init__()
        self.subt_object = subt_object
        self.video_tab_object = video_tab_object

        self.__create_menu_items()


    def __create_menu_items(self):
        menu_id = wx.NewId()
        m_copy = wx.MenuItem(self, menu_id, "copy text")
        self.Append(m_copy)
        self.Bind(wx.EVT_MENU, self.__on_subt_menu_item_copy, id=menu_id)

        menu_id = wx.NewId()
        m_load = wx.MenuItem(self, menu_id, "load subtitle file")
        self.Append(m_load)
        self.Bind(wx.EVT_MENU, self.__on_subt_menu_item_load, id=menu_id)

        menu_id = wx.NewId()
        m_disable = wx.MenuItem(self, menu_id, "disable subtitle")
        self.Append(m_disable)
        self.Bind(wx.EVT_MENU, self.__on_subt_menu_item_disable, id=menu_id)


    def copy_text_to_buffer(self):
        if not self.subt_object:
            return

        text = self.subt_object.GetStringSelection()
        if not text:
            text = self.subt_object.GetValue()
        text = text.replace('\n',' ')

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()


    def __on_subt_menu_item_copy(self, e):
        self.copy_text_to_buffer()


    def __on_subt_menu_item_load(self, e):
        subt_file = ''
        dialog_path = '~'
        dlg = wx.FileDialog(self.subt_object, "Choose a subtitles file"
            , os.path.expanduser('~'), "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            subt_file = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
        dlg.Destroy()
        if not os.path.isfile(subt_file):
            return

        vt = self.video_tab_object
        if self.subt_object == vt.subt_1:
            vt.env["video_subt1_file"] = subt_file
            vt.subtitle_1 = SubTitle(vt.env, "video_subt1_file")
            return
        if self.subt_object == vt.subt_2:
            vt.env["video_subt2_file"] = subt_file
            vt.subtitle_2 = SubTitle(vt.env, "video_subt2_file")
            return


    def __on_subt_menu_item_disable(self, e):
        vt = self.video_tab_object
        if self.subt_object == vt.subt_1:
            vt.subtitle_1 = None
            vt.env["video_subt1_file"] = ""
            self.subt_object.SetValue("")
            return
        if self.subt_object == vt.subt_2:
            vt.subtitle_2 = None
            vt.env["video_subt2_file"] = ""
            self.subt_object.SetValue("")
            return




#drag-n-drop handler: text
class LinkDropTarget(wx.TextDropTarget):
    def __init__(self, video_tab_object):
        wx.TextDropTarget.__init__(self)
        self.video_tab_object = video_tab_object


    def OnDropText(self, x, y, text):
        # self.video_tab_object(text)
        self.video_tab_object.logger.info("received link: {}".format(text))
        # self.EVT_LOAD_LINK(self.video_tab_object, text)
        # because we use drag-n-drop mechanism during link loading we need 
        # to create new event and finish this one.
        # self.video_tab_object.on_link_load(text)
        wx.CallAfter(self.video_tab_object.on_link_load, text)
        return True




# video processing (video tab could be disabled)
class VideoTab:
    def __init__(self, nb, caption, env, logger):
        self.env = env
        self.logger = logger
        self.caption = caption
        self.video_length = 0
        self.subtitle_1 = None
        self.subtitle_2 = None

        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

        self.LoadLinkEvent, self.EVT_LOAD_LINK = wx.lib.newevent.NewEvent()

        self.__init_gui(nb, caption)
        self.load_previous_state()



    def __init_gui(self, nb, caption):
        p = wx.Panel(nb)
        self.tab_panel = p
        sizer = wx.GridBagSizer()

        splitter = wx.SplitterWindow(p)

        self.video_panel = wx.Panel(splitter, size=(200,150))
        self.video_panel.SetBackgroundColour(wx.BLACK)
        nb.Bind(wx.EVT_RIGHT_DOWN, self.__on_video_right_down)
        self.tab_panel.Bind(wx.EVT_RIGHT_DOWN, self.__on_video_right_down)
        splitter.Bind(wx.EVT_RIGHT_DOWN, self.__on_video_right_down)
        self.video_panel.Bind(wx.EVT_RIGHT_DOWN, self.__on_video_right_down)
        # self.video_panel.Bind(self.EVT_LOAD_LINK, self.on_link_load)
        self.video_panel.SetDropTarget(LinkDropTarget(self))

        self.bottom_panel = wx.Panel(splitter, size=(200,50))
        self.__draw_bottom_panel(self.bottom_panel)

        splitter.SplitHorizontally(self.video_panel, self.bottom_panel)
        splitter.SetMinimumPaneSize(200)
        sizer.Add(splitter, pos=(0, 0), flag=wx.EXPAND)

        p.SetSizer(sizer)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)

        nb.AddPage(p, self.caption)
        self.__create_accel_table(p)

        self.timer = wx.Timer(p)
        p.Bind(wx.EVT_TIMER, self.on_timer, self.timer)



    def __draw_bottom_panel(self, p):
        sizer = wx.GridBagSizer()

        row = 1
        col = 0

        # load button
        self.load_button = wx.Button(p, label="load")
        sizer.Add(self.load_button, pos=(row,col), flag=wx.EXPAND)
        p.Bind(wx.EVT_BUTTON, self.on_load,  self.load_button)

        # play_pause button
        col += 1
        self.play_pause_button = wx.Button(
            p, label="play / pause")
        sizer.Add(self.play_pause_button, pos=(row,col), flag=wx.EXPAND)
        p.Bind(wx.EVT_BUTTON, self.on_play_pause,  self.play_pause_button)

        # << button
        col += 1
        self.back_button = wx.Button(p, label="<<")
        sizer.Add(self.back_button, pos=(row,col), flag=wx.EXPAND)
        p.Bind(wx.EVT_BUTTON, self.on_back,  self.back_button)

        # >> button
        col += 1
        self.forward_button = wx.Button(p, label=">>")
        sizer.Add(self.forward_button, pos=(row,col), flag=wx.EXPAND)
        p.Bind(wx.EVT_BUTTON, self.on_forward,  self.forward_button)

        # time slider
        self.time_slider = wx.Slider(p, -1, 0, 0, 1000)
        sizer.Add(self.time_slider, span=(0,col+1)
            , pos=(0,0), flag=wx.EXPAND)
        self.time_slider.Bind(wx.EVT_SLIDER, self.on_time_slider_scroll)

        # subtitles 1
        row += 1
        subt1_row = row
        self.subt_1 = wx.richtext.RichTextCtrl(
            p, wx.ID_ANY, size=(0,60),
            style=wx.TE_MULTILINE|wx.TE_READONLY|wx.VSCROLL)
        self.subt_1.SetBackgroundColour((0,0,0))

        sizer.Add(self.subt_1, span=(0,col+1), pos=(row,0), flag=wx.EXPAND)
        self.subt1_menu = SubtPopupMenu(self.subt_1, self)
        self.subt_1.Bind(wx.EVT_RIGHT_DOWN, self.__on_subt1_right_down)

        s1_font_up_id = wx.NewId()
        s1_font_down_id = wx.NewId()
        s1_copy_id = wx.NewId()
        self.subt_1.Bind(wx.EVT_MENU, self.on_s1_font_up, id=s1_font_up_id)
        self.subt_1.Bind(wx.EVT_MENU, self.on_s1_font_down, id=s1_font_down_id)
        self.subt_1.Bind(wx.EVT_MENU, self.on_s1_copy, id=s1_copy_id)
        accel_tbl_s1 = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('='), s1_font_up_id),
            (wx.ACCEL_CTRL, ord('-'), s1_font_down_id),
            (wx.ACCEL_CTRL, ord('c'), s1_copy_id)])
        self.subt_1.SetAcceleratorTable(accel_tbl_s1)

        # subtitles 2
        row += 1
        subt2_row = row
        self.subt_2 = wx.richtext.RichTextCtrl(
            p, wx.ID_ANY, size=(0,60),
            style=wx.TE_MULTILINE|wx.TE_READONLY|wx.VSCROLL)
        self.subt_2.SetBackgroundColour((0,0,0))
        sizer.Add(self.subt_2, span=(0,col+1), pos=(row,0), flag=wx.EXPAND)
        self.subt2_menu = SubtPopupMenu(self.subt_2, self)
        self.subt_2.Bind(wx.EVT_RIGHT_DOWN, self.__on_subt2_right_down)

        s2_font_up_id = wx.NewId()
        s2_font_down_id = wx.NewId()
        s2_copy_id = wx.NewId()
        self.subt_2.Bind(wx.EVT_MENU, self.on_s2_font_up, id=s2_font_up_id)
        self.subt_2.Bind(wx.EVT_MENU, self.on_s2_font_down, id=s2_font_down_id)
        self.subt_2.Bind(wx.EVT_MENU, self.on_s2_copy, id=s2_copy_id)
        accel_tbl_s2 = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('='), s2_font_up_id),
            (wx.ACCEL_CTRL, ord('-'), s2_font_down_id),
            (wx.ACCEL_CTRL, ord('c'), s1_copy_id)])
        self.subt_2.SetAcceleratorTable(accel_tbl_s2)


        for i in range(col+1):
            sizer.AddGrowableCol(i)
        sizer.AddGrowableRow(subt1_row)
        sizer.AddGrowableRow(subt2_row)
        p.SetSizerAndFit(sizer)



    def __on_font_up(self, ctrl):
        fs = ctrl.GetFontScale()
        ctrl.SetFontScale(fs + 0.1)

    def __on_font_down(self, ctrl):
        fs = ctrl.GetFontScale()
        ctrl.SetFontScale(fs - 0.1)


    def on_s1_font_up(self, evt):
        self.__on_font_up(self.subt_1)
        evt.Skip()

    def on_s1_font_down(self, evt):
        self.__on_font_down(self.subt_1)
        evt.Skip()

    def on_s1_copy(self, evt):
        self.subt1_menu.copy_text_to_buffer()

    def on_s2_font_up(self, evt):
        self.__on_font_up(self.subt_2)
        evt.Skip()

    def on_s2_font_down(self, evt):
        self.__on_font_down(self.subt_2)
        evt.Skip()

    def on_s2_copy(self, evt):
        self.subt2_menu.copy_text_to_buffer()

    def __create_accel_table(self, win):
        but_space_id = wx.NewId()
        but_left_id = wx.NewId()
        but_right_id = wx.NewId()

        win.Bind(wx.EVT_MENU, self.on_play_pause, id=but_space_id)
        win.Bind(wx.EVT_MENU, self.on_back, id=but_left_id)
        win.Bind(wx.EVT_MENU, self.on_forward, id=but_right_id)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_SPACE, but_space_id),
            (wx.ACCEL_NORMAL, wx.WXK_LEFT, but_left_id),
            (wx.ACCEL_NORMAL, wx.WXK_RIGHT, but_right_id) ])
        win.SetAcceleratorTable(accel_tbl)


    def __on_video_right_down(self, e):
        video_menu = VideoPopupMenu(self)
        video_menu.reload(self.vlc_player)
        self.video_panel.PopupMenu(video_menu, e.GetPosition())


    def __on_subt1_right_down(self, e):
        self.subt_1.PopupMenu(self.subt1_menu, e.GetPosition())


    def __on_subt2_right_down(self, e):
        self.subt_2.PopupMenu(self.subt2_menu, e.GetPosition())


    def load_previous_state(self):
        if "video_config_file" not in self.env:
            return
        if not os.path.isfile(self.env["video_config_file"]):
            return

        self.env.append_env(self.env["video_config_file"])
        
        self.__start_playing_video()


    def save_current_state(self):
        if "video_config_file" not in self.env:
            return

        state = []
        state.append({"last_played_file": self.env["last_played_file"] \
            if "last_played_file" in self.env else ""})
        state.append({"last_position": self.vlc_player.get_position()})
        state.append({"video_audio_track": self.vlc_player.audio_get_track()})
        state.append({"video_audio_file": self.env["video_audio_file"] \
            if "video_audio_file" in self.env else ""})

        if self.subtitle_1:
            state.append(
                {"video_subt1_file": self.subtitle_1.get_full_file_name()})
            state.append(
                {"video_subt1_shift": self.subtitle_1.get_shift_value()})
        if self.subtitle_2:
            state.append(
                {"video_subt2_file": self.subtitle_2.get_full_file_name()})
            state.append(
                {"video_subt2_shift": self.subtitle_2.get_shift_value()})

        self.logger.info("saving current video state: {}".format(state))

        with open(self.env["video_config_file"], 'w') as jf:
            json.dump(state, jf,
                indent=2, ensure_ascii=False, sort_keys=False)



    def save_snapshot_file(self):
        self.vlc_player.video_take_snapshot(
            0, self.env["video_snapshot_file"], 0, 0)



    def __get_item_text(self, item):
        text = item.GetStringSelection()
        if not text:
            text = item.GetValue()
        text = text.replace('<i>', '')
        text = text.replace('</i>', '')
        return text.replace('\n',' ')



    def get_term_text(self):
        return self.__get_item_text(self.subt_1)



    def get_definition_text(self):
        return self.__get_item_text(self.subt_2)



    def __load_video(self, file_name):
        self.video_length = 0
        self.vlc_media = self.vlc_instance.media_new(file_name)
        self.vlc_player.set_media(self.vlc_media)

        handle = self.video_panel.GetHandle()
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.vlc_player.set_xwindow(handle)
        elif sys.platform == "win32":  # for Windows
            self.vlc_player.set_hwnd(handle)
        elif sys.platform == "darwin":  # for MacOS
            self.vlc_player.set_nsobject(handle)

        self.on_play_pause(None)



    def __load_subtitles(self):
        if "video_subt1_file" in self.env \
        and self.env["video_subt1_file"] \
        and os.path.isfile(self.env["video_subt1_file"]):
            self.subtitle_1 = SubTitle(self.env, "video_subt1_file")
        if "video_subt2_file" in self.env \
        and self.env["video_subt2_file"] \
        and os.path.isfile(self.env["video_subt2_file"]):
            self.subtitle_2 = SubTitle(self.env, "video_subt2_file")



    def on_load(self, evt):
        dlg = wx.FileDialog(self.tab_panel
            , "Choose a video file or youtube link"
            , os.path.expanduser('~'), "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            source = dlg.GetFilename()
            directory = dlg.GetDirectory()
        # finally destroy the dialog
        dlg.Destroy()

        # do prep settings here        
        PluginLoader(self.env, "InitVideoParams").process(
            source=source, directory=directory)
        self.__start_playing_video()



    def on_link_load(self, evt):
        PluginLoader(self.env, "InitVideoParams").process(
            source=evt, directory=self.env["sl_global_temp_file"])
        self.__start_playing_video()



    def __start_playing_video(self):
        if "last_played_file" not in self.env \
            or not self.env["last_played_file"] \
            or not os.path.isfile(self.env["last_played_file"]):
            return

        self.__load_video(self.env["last_played_file"])
        self.__load_subtitles()

        # wait for video loading to proces
        while not self.vlc_player.is_playing():
            time.sleep(0.1)

        if "last_position" in self.env:
            self.logger.info("setting video to last position: {}".format(
                self.env["last_position"]))
            self.vlc_player.set_position(self.env["last_position"])

        if "video_audio_track" in self.env:
            self.logger.info("setting last audio track: {}".format(
                self.env["video_audio_track"]))
            self.vlc_player.audio_set_track(self.env["video_audio_track"])

        self.vlc_player.video_set_spu(-1)
        self.vlc_player.audio_set_volume(100)


    def on_play_pause(self, evt):
        if self.vlc_player.is_playing():
            self.vlc_player.pause()
            self.timer.Stop()
        else:
            self.vlc_player.play()
            self.timer.Start(100)



    def on_back(self, evt):
        pos = self.vlc_player.get_time()
        pos -= 5000
        self.vlc_player.set_time(pos)



    def on_forward(self, evt):
        pos = self.vlc_player.get_time()
        pos += 5000
        self.vlc_player.set_time(pos)



    def on_time_slider_scroll(self, evt):
        pos = self.time_slider.GetValue()
        self.vlc_player.set_time(pos)



    def on_timer(self, evt):
        if not self.video_length:
            self.video_length = self.vlc_player.get_length()
            self.time_slider.SetRange(-1, self.video_length)

        if not self.vlc_player.is_playing():
            return

        self.time = self.vlc_player.get_time()

        self.time_slider.SetValue(self.time)

        if self.subtitle_1:
            text = self.subtitle_1.get_text(self.time)
            if self.subt_1.GetValue() != text:
                ta = wx.TextAttr()
                ta.SetTextColour(wx.Colour(80, 155, 35))
                ta.SetAlignment(wx.TEXT_ALIGNMENT_CENTRE)
                self.subt_1.SetDefaultStyle(ta)
                self.subt_1.SetValue(text)


        if self.subtitle_2:
            text = self.subtitle_2.get_text(self.time)
            if self.subt_2.GetValue() != text:
                ta = wx.TextAttr()
                ta.SetTextColour(wx.Colour(80, 100, 140))
                ta.SetAlignment(wx.TEXT_ALIGNMENT_CENTRE)
                self.subt_2.SetDefaultStyle(ta)
                self.subt_2.SetValue(text)

        evt.Skip()


