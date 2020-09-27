import os
import re
import time
import wx, wx.dataview
import subprocess

from plugin_Base import PluginBase



class InitVideoParams(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)

        self.env["last_position"] = 0
        self.env["video_audio_track"] = 0
        self.env["video_audio_file"] = ""
        self.env["video_subt1_file"] = ""
        self.env["video_subt2_file"] = ""

        self.__video_handlers = {
            MKVHandler(self.env, self.logger)
        }



    def process(self, param_map=None):
        self.__process_with_handlers()



    def __process_with_handlers(self):
        input_video_source = self.env["last_played_file"]
        if not input_video_source:
            return

        self.env["videos_map"] = {}
        self.env["audios_map"] = {}
        self.env["subtitles_map"] = {}

        for handler in self.__video_handlers:
            if not handler.match(input_video_source):
                continue

            handler.pre_process()
            if len(self.env["audios_map"]) or len(self.env["subtitles_map"]):
                self.__show_gui()
                handler.post_process()



    def __show_gui(self):

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
        txt_video = wx.TextCtrl(p)
        sizer.Add(txt_video, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        txt_video.SetDropTarget(TextDropTarget(txt_video))
        txt_video.Bind(wx.EVT_TEXT, self.__on_select_video)
        txt_video.Bind(wx.EVT_TEXT_PASTE, self.__on_select_video)
        row += 1
        lbl_audio = wx.StaticText(p, -1, "audio stream to play")
        sizer.Add(lbl_audio, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        txt_audio = wx.TextCtrl(p)
        sizer.Add(txt_audio, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        txt_audio.SetDropTarget(TextDropTarget(txt_audio))
        txt_audio.Bind(wx.EVT_TEXT, self.__on_select_audio)
        txt_audio.Bind(wx.EVT_TEXT_PASTE, self.__on_select_audio)
        row += 1
        lbl_subt1 = wx.StaticText(p, -1, "subtitle-term to play")
        sizer.Add(lbl_subt1, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        txt_subt1 = wx.TextCtrl(p)
        sizer.Add(txt_subt1, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        txt_subt1.SetDropTarget(TextDropTarget(txt_subt1))
        txt_subt1.Bind(wx.EVT_TEXT, self.__on_select_subt1)
        txt_subt1.Bind(wx.EVT_TEXT_PASTE, self.__on_select_subt1)
        row += 1
        lbl_subt2 = wx.StaticText(p, -1, "subtitle-definition to play")
        sizer.Add(lbl_subt2, pos=(row,col), flag=wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        row += 1
        txt_subt2 = wx.TextCtrl(p)
        sizer.Add(txt_subt2, pos=(row,col), flag = wx.EXPAND|wx.LEFT)
        txt_subt2.SetDropTarget(TextDropTarget(txt_subt2))
        txt_subt2.Bind(wx.EVT_TEXT, self.__on_select_subt2)
        txt_subt2.Bind(wx.EVT_TEXT_PASTE, self.__on_select_subt2)
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

        self.env["video_selected"] = ""
        self.env["audio_selected"] = ""
        self.env["subt1_selected"] = ""
        self.env["subt2_selected"] = ""

        root_win.SetSize((600, 250))
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



    def __on_select_video(self, event):
        self.env["video_selected"] = event.GetString()

    def __on_select_audio(self, event):
        self.env["audio_selected"] = event.GetString()

    def __on_select_subt1(self, event):
        self.env["subt1_selected"] = event.GetString()

    def __on_select_subt2(self, event):
        self.env["subt2_selected"] = event.GetString()

  


#drag-n-drop handler: text
class TextDropTarget(wx.TextDropTarget):
    def __init__(self, textCtrl):
        wx.TextDropTarget.__init__(self)
        self.textCtrl = textCtrl


    def OnDropText(self, x, y, data):
        self.textCtrl.SetValue(data)
        return True

# ------------------------------------------------------------------------------
# video source handlers:
class MKVHandler:
    def __init__(self, env, logger):
        self.env = env
        self.logger = logger


    def match(self, source):
        if (re.match(self.env["reg_mkv_source"], source)):
            self.logger.info("Processing source with MKVHandler handler")
            return True
        return False


    def pre_process(self):

        command = self.env["pre_mkv_command"]
        command.append(self.env["last_played_file"])
        self.logger.info("running command: {}".format(command))
        cmd = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = cmd.communicate()
        cmd.wait()
        search_text = str(out if out else err)
        #self.logger.info("ff_text={}".format(search_text))

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
            if v == self.env["audio_selected"]:
                self.env["video_audio_track"] = int(k.split(':')[1])
                self.env["video_audio_file"] = self.__create_audio_file(k)

        for k,v in self.env["subtitles_map"].items():
            if v == self.env["subt1_selected"]:
                self.env["video_subt1_file"] = self.__create_subtitle_file(k)

        for k,v in self.env["subtitles_map"].items():
            if v == self.env["subt2_selected"]:
                self.env["video_subt2_file"] = self.__create_subtitle_file(k)

    


    def __create_audio_file(self, track_map_id):
        out_file = ""

        self.logger.info("extracting audio track id: {}".format(track_map_id))
        self.env["input_audio_map_value"] = track_map_id
        self.env["output_audio_file_value"] = "{}/audio_{}.mp3".format(
            os.path.dirname(self.env["last_played_file"])
            , track_map_id.replace(':', '_'))
        
        command = []
        for cn in self.env["audio_mkv_command_param_names"]:
            command.append(self.env[cn])

        self.logger.info("executing audio command: {}".format(command))
        out_file = self.env["output_audio_file_value"]

        cmd = subprocess.Popen(command)
        cmd.wait()

        self.logger.info("executing audio_command, done.")
        # restore values
        self.env["input_audio_map_value"] = ""
        self.env["output_audio_file_value"] = ""

        return out_file



    def __create_subtitle_file(self, track_map_id):
        outfile = ""

        self.logger.info(
            "extracting subtitle track id: {}".format(track_map_id))

        self.env["input_subtitle_map_value"] = track_map_id
        self.env["output_subtitle_file_value"] = "{}/subtitle_{}.srt".format(
            os.path.dirname(self.env["last_played_file"])
            , track_map_id.replace(':', '_'))
        
        command = []
        for cn in self.env["subtitle_mkv_command_param_names"]:
            command.append(self.env[cn])

        self.logger.info("executing audio command: {}".format(command))
        out_file = self.env["output_subtitle_file_value"]

        cmd = subprocess.Popen(command)
        cmd.wait()

        self.logger.info("executing audio_command, done.")
        # restore values
        self.env["input_subtitle_map_value"] = ""
        self.env["output_subtitle_file_value"] = ""

        return out_file

