# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import re
import time
import wx, wx.dataview
import subprocess

from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader


class InitVideoParams(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)

        if "last_played_file" not in self.env:
            self.env["last_played_file"] = ""

        self.env["last_position"] = 0
        self.env["video_audio_track"] = 0
        self.env["video_audio_file"] = ""
        self.env["video_subt1_file"] = ""
        self.env["video_subt2_file"] = ""

        self.__video_handlers = [
            MKVHandler(self.env, self.logger),
            YoutubeLinkHandler(self.env, self.logger)
        ]



    def process(self, **kwargs):
        if "source" not in kwargs \
            or "directory" not in kwargs:
            self.logger.error("Missing argumets for InitVideoParams.process")
            return

        self.__source_name = kwargs["source"]
        self.__directory_name = kwargs["directory"]
        self.__process_with_handlers()



    def __process_with_handlers(self):
        self.env["videos_map"] = {}
        self.env["audios_map"] = {}
        self.env["subtitles_map"] = {}

        for handler in self.__video_handlers:
            if not handler.match(self.__directory_name, self.__source_name):
                continue

            handler.pre_process()
            if len(self.env["audios_map"]) or len(self.env["subtitles_map"]):
                self.__show_gui()
                handler.post_process()



    def __show_gui(self):

        self.env["video_selected"] = ""
        self.env["audio_selected"] = ""
        self.env["subt1_selected"] = ""
        self.env["subt2_selected"] = ""

        root_win = wx.Dialog(None, wx.ID_ANY
            , pos=(self.env["ui_x_pos"], self.env["ui_y_pos"]))
        root_win.SetTitle("Stream selection window")
        p = wx.Panel(root_win)
        sizer = wx.GridBagSizer()

        row = 0
        col = 0
        lbl_term = wx.StaticText(p, -1, "available streams:")
        sizer.Add(lbl_term, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)

        col += 1        
        lbl_video = wx.StaticText(p, -1, "video stream to play")
        sizer.Add(lbl_video, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        self.txt_video = wx.TextCtrl(p)
        sizer.Add(self.txt_video, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        self.txt_video.SetDropTarget(TextDropTarget(self.txt_video, self.env, "video_selected"))
        row += 1
        lbl_audio = wx.StaticText(p, -1, "audio stream to play")
        sizer.Add(lbl_audio, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        self.txt_audio = wx.TextCtrl(p)
        sizer.Add(self.txt_audio, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        self.txt_audio.SetDropTarget(TextDropTarget(self.txt_audio, self.env, "audio_selected"))
        row += 1
        lbl_subt1 = wx.StaticText(p, -1, "subtitle-term to play")
        sizer.Add(lbl_subt1, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        self.txt_subt1 = wx.TextCtrl(p)
        sizer.Add(self.txt_subt1, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        self.txt_subt1.SetDropTarget(TextDropTarget(self.txt_subt1, self.env, "subt1_selected"))
        row += 1
        lbl_subt2 = wx.StaticText(p, -1, "subtitle-definition to play")
        sizer.Add(lbl_subt2, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        self.txt_subt2 = wx.TextCtrl(p)
        sizer.Add(self.txt_subt2, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        self.txt_subt2.SetDropTarget(TextDropTarget(self.txt_subt2, self.env, "subt2_selected"))
        row += 1
        growable_row = row
        sizer.Add(wx.Panel(p), pos=(row, col))

        self._trk_list = wx.TreeCtrl(p, wx.ID_ANY)
        sizer.Add(self._trk_list
            , pos = (1, 0), span=(row, 1), flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM)
        self._trk_list.Bind(wx.EVT_TREE_BEGIN_DRAG, self.__on_begin_drag)
        p.Bind(wx.EVT_MOUSE_CAPTURE_LOST, lambda x: None)
        self.__init_trk_list(self._trk_list)

        p.SetSizer(sizer)
        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(growable_row)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        p.SetSizerAndFit(sizer)

        root_win.SetSize((800, 500))
        root_win.ShowModal()
        root_win.Destroy()



    def __on_begin_drag(self, event):
        item = event.GetItem()
        if self._trk_list.ItemHasChildren(item):
            return

        dropsrc = wx.DropSource(self._trk_list)
        text = self._trk_list.GetItemText(item)
        txt_data = wx.TextDataObject(text)
        dropsrc.SetData(txt_data)
        dropsrc.DoDragDrop(True)



    def __init_trk_list(self, trk_list):
        streams = trk_list.AddRoot("Streams")
        videos = trk_list.AppendItem(streams, "videos")
        for k,v in self.env["videos_map"].items():
            trk_list.AppendItem(videos, v)
        audios = trk_list.AppendItem(streams, "audios")
        for k,v in self.env["audios_map"].items():
            trk_list.AppendItem(audios, v)
        subtitles = trk_list.AppendItem(streams, "subtitles")
        for k,v in self.env["subtitles_map"].items():
            trk_list.AppendItem(subtitles, v)
        trk_list.ExpandAll()
  


#drag-n-drop handler: text
class TextDropTarget(wx.TextDropTarget):
    def __init__(self, textCtrl, env, key):
        wx.TextDropTarget.__init__(self)
        self.env = env
        self.key = key
        self.textCtrl = textCtrl


    def OnDropText(self, x, y, data):
        self.textCtrl.SetValue(data)
        self.env[self.key] = data
        return True

# ------------------------------------------------------------------------------
# video source handlers:
class MKVHandler:
    def __init__(self, env, logger):
        self.env = env
        self.logger = logger


    def match(self, directory_name, source_name):
        source = "{}/{}".format(directory_name, source_name)
        if not os.path.isfile(source):
            return False

        if (re.match(self.env["reg_mkv_source"], source)):
            self.logger.info("Processing source with MKVHandler handler")

            self.env["last_played_file"] = source
            return True

        return False


    def pre_process(self):

        command = PluginLoader(self.env, "CmdRun").process(
                run_file=self.env["video_file_commands"]
                , cmd_name="command_get_media_file_info"
                , media_file=self.env["last_played_file"]
                , get_command_only=True)

        cmd = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = cmd.communicate()
        cmd.wait()
        search_text = (out if out else err).decode("utf-8")

        def search_and_add(reg_name, text, out_map):
            pattern = re.compile(self.env[reg_name], re.MULTILINE)
            for m in re.finditer(pattern, search_text):
                # self.logger.info("match({})=={}".format(reg_name, m))
                out_map[m.group(1)] = m.group(0)

        search_and_add("pre_mkv_reg_audios"
            , search_text, self.env["audios_map"])
        search_and_add("pre_mkv_reg_subtitles"
            , search_text, self.env["subtitles_map"])
        search_and_add("pre_mkv_reg_videos"
            , search_text, self.env["videos_map"])
        # self.logger.info("v={},\na={},\ns={}".format(
        #     videos_map, audios_map, subtitles_map))



    def post_process(self):
        self.logger.info("selected values are:\n{}\n{}\n{}\n{}\n".format(
            self.env["video_selected"]
            , self.env["audio_selected"]
            , self.env["subt1_selected"]
            , self.env["subt2_selected"]))

        # for k,v in self.env["videos_map"].items():
        #     if v == self.env["video_selected"]:

        for k,v in self.env["audios_map"].items():
            if self.env["audio_selected"] == v:
                self.env["video_audio_track"] = int(k.split(':')[1])
                self.env["video_audio_file"] = self.__create_audio_file(k)

        for k,v in self.env["subtitles_map"].items():
            if self.env["subt1_selected"] == v:
                self.env["video_subt1_file"] = self.__create_subtitle_file(k)

        for k,v in self.env["subtitles_map"].items():
            if self.env["subt2_selected"] == v:
                self.env["video_subt2_file"] = self.__create_subtitle_file(k)



    def __create_audio_file(self, track_map_id):
        out_file = ""

        self.logger.info("extracting audio track id: {}".format(track_map_id))

        active_dir = os.path.dirname(self.env["last_played_file"])
        in_file_name = os.path.basename(self.env["last_played_file"])
        out_file = "{}/{}_audio_{}.mp3".format(
            active_dir, in_file_name, track_map_id.replace(':', '_'))

        status = PluginLoader(self.env, "CmdRun").process(
                run_file=self.env["video_file_commands"]
                , cmd_name="command_extract_audio_track"
                , in_file=self.env["last_played_file"]
                , track_id=track_map_id
                , out_file=out_file
                , active_dir=active_dir)

        if not os.path.isfile(out_file):
            self.logger.error("Can't extract audio track.")
            return None

        return out_file



    def __create_subtitle_file(self, track_map_id):

        self.logger.info("extracting subts track id: {}".format(track_map_id))

        active_dir = os.path.dirname(self.env["last_played_file"])
        in_file_name = os.path.basename(self.env["last_played_file"])
        out_file = "{}/{}_subtitle_{}.srt".format(
            active_dir, in_file_name, track_map_id.replace(':', '_'))

        status = PluginLoader(self.env, "CmdRun").process(
                run_file=self.env["video_file_commands"]
                , cmd_name="command_extract_subtitles"
                , in_file=self.env["last_played_file"]
                , track_id=track_map_id
                , out_file=out_file
                , active_dir=active_dir)

        if not status:
            self.logger.warning("Can't extract subtitles track.")
            return None

        PluginLoader(self.env, "PreprocessSubtitleFile").process(
            subt_file=out_file)

        return out_file




class YoutubeLinkHandler(MKVHandler):
    def __init__(self, env, logger):
        super().__init__(env, logger)
        self.env = env
        self.logger = logger
        self.__vid = None



    def match(self, directory_name, source_name):

        m = re.match(self.env["reg_youtube_source"], source_name)
        if m:
            self.logger.info("Processing source with YoutubeLink handler")
            self.__vid = m.group(1)
            
            result = PluginLoader(self.env, "CmdRun").process(
                run_file=self.env["youtube_load_commands"]
                , vid=self.__vid, out_dir=directory_name)

            file_name = "{}.mp4".format(self.__vid) 

            return super().match(directory_name, file_name)

        return False


