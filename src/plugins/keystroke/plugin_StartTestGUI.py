import os
import re
import wx
import wx.richtext
import math
import time
import vlc
from fuzzywuzzy import fuzz
from threading import Thread
import shutil


from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase

class StartTest():
    def __init__(self, env):
        self.env = env
        self.logger = env["logger"]


    def get_next_note(self):
        self.k_ratio = 1.0
        items_count = 5

        q_res = PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list = [{
                "query" :  self.env["sql_select_expired_notes"].format(
                    count=items_count)
                , "data" : () }])

        # there are no expired notes, loading new ones
        if not len(q_res[0]):
            sql = self.env["sql_select_new_notes"].format( count=items_count)
            q_res = PluginLoader(self.env, self.env["sl_db_query"]).process(
                queries_list = [{ "query" : sql, "data" : () }] )


        for r in q_res[0]:
            note = self.__get_note_from_result(r)
            if note:
                self.__current_note = note
                return note

        raise Exception("Can't select new note for this test")



    def __get_note_from_result(self, rec):
        note = {}

        note["id"] = rec[0]
        note["card_id"] = rec [1]
        note["creation_time"] = rec [2]
        note["mod_time"] = rec [3]
        note["term"] = rec [4]
        note["term_note"] = rec [5]
        note["term_audio_id"] = rec [6]
        note["image_id"] = rec [7]
        note["definition"] = rec [8]
        note["definition_note"] = rec [9]
        note["definition_audio_id"] = rec [10]
        note["times_used"] = rec [11]
        note["last_used_time"] = rec [12]
        note["pace_time"] = rec [13]
        note["pace_factor"] = rec [14]
        note["repeat_factor"] = rec [15]
        note["reviews_count"] = rec [16]

        if not note["term"]:
            # skip the notes with empty term to avoid shifts of 
            # entered words
            self.logger.warning(
                "Note id={} has empty 'term field, skipped'".format(note["id"]))
            return None;

        if not note["definition"]:
            self.logger.warning(
                "Note id={} has empty 'definition field, skipped'".format(
                    note["id"]))
            return None;

        note["words"] = self.__preprocess_term(note["term"])
        note["text"] = ' '.join(note["words"])
        note["mask"] = self.to_mask(note["text"])

        return note



    def to_mask(self, text):
        text = re.sub(self.env["regex_uppercase"]
            , self.env["mask_uppercase"], text)
        text = re.sub(self.env["regex_lowercase"]
            , self.env["mask_lowercase"], text)
        return text


    def reduce_k_ratio(self):
        self.k_ratio = 0.4 # this is a penalty for listening audio


    def __preprocess_term(self, text):
        words = [ (w) for w in re.findall("[\\S]+", text)]
        return words


    def check_results(self, entered_text):
        stat = {}

        stat["rating"] = self.__rate_current_note(entered_text)

        stat["conclusion"] = "Card: id: {}; rating = {:.5}; next_time = {}"\
            "\n\t source_text: {}".format(
                self.__current_note["id"]
                , stat["rating"]
                , int(self.__current_note["pace_time"])
                , self.__current_note["text"])

        if self.__current_note["text"] != entered_text:
            stat["conclusion"] = stat["conclusion"] + \
                "\n\tentered_text: {}".format(entered_text)

        self.__save_achievement()

        return stat



    def __rate_current_note(self, entered_text):
        note = self.__current_note

        fr = fuzz.ratio(note["text"], entered_text) / 100
        k = 2.0 + 2 * math.tanh(18 * fr - 15) * self.k_ratio
        rating = k / 4 
        note["pace_time"] = note["pace_time"] * k
        time_interval = int(self.env["minimal_time_interval_str"])
        if note["pace_time"] < time_interval:
            note["pace_time"] = time_interval

        return rating


    def __save_achievement(self):
        n = self.__current_note
        sql_query_item = {}
        sql_query_item["query"] = self.env["sql_update_achievement"]
        sql_query_item["data"] = ('note'
            , n["id"] # item_id
            , time.time() # last_used_time
            , n["pace_time"]
            , 0 # learning_status_id
            , n["repeat_factor"]
            , n["pace_factor"]
            , n["reviews_count"] + 1)

        PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list=[sql_query_item])



class StartTestGUI(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        self.st = StartTest(self.env)



    def process(self, **kwargs):
        self.__draw_gui()
        self.__start_test()



    def __draw_gui(self):
        p = self.env["win_panel"]
        sizer = wx.GridBagSizer()

        row = 0
        col = 0

        note_panel_row = row 
        note_panel = wx.Panel(p, size=(-1, 200))
        sizer.Add(note_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_note_panel(note_panel)

        row += 1
        input_panel_row = row 
        input_panel = wx.Panel(p, size=(-1, 200))
        sizer.Add(input_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_input_panel(input_panel)

        row += 1
        status_panel_row = row 
        status_panel = wx.Panel(p, size=(-1, 300))
        sizer.Add(status_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_status_panel(status_panel)

        for r in range(row+1):
            sizer.AddGrowableRow(r)
        sizer.AddGrowableCol(col)
        p.SetSizerAndFit(sizer)



    def __draw_note_panel(self, p):
        sizer = wx.GridBagSizer()

        row = 0
        col = 1

        # definition note
        self.definition_note = wx.TextCtrl(p
            , size=(800, 50)
            , style=wx.TE_MULTILINE|wx.TE_READONLY)
        sizer.Add(self.definition_note
            , pos=(row, col), flag=wx.EXPAND|wx.BOTTOM)

        # definition
        row += 1
        self.definition = wx.TextCtrl(p
            , size=(800, 150)
            , style=wx.TE_MULTILINE|wx.TE_READONLY)
        font_d = wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Arial')
        self.definition.SetFont(font_d)
        sizer.Add(self.definition
            , pos=(row, col), span=(2, 1),flag=wx.EXPAND|wx.ALL)

        # button play audio
        but_play = wx.Button(p, label="play audio", size=(200, 20))
        sizer.Add(but_play, pos=(2, 0), flag=wx.EXPAND|wx.BOTTOM)
        p.Bind(wx.EVT_BUTTON, self.__on_play_audio,  but_play)

        # image
        self.original_bitmap = wx.Image(self.env["no_image_jpg"]
            , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.env["ir_image_size"] = (200, 200)
        self.image = wx.StaticBitmap(p, size=self.env["ir_image_size"])
        sizer.Add(self.image
            , pos=(0, 0)
            , span=(row+1, 1)
            , flag=wx.EXPAND|wx.ALL)
        self.image.SetBitmap(self.original_bitmap)

        for r in range(row+1):
            sizer.AddGrowableRow(r)
        sizer.AddGrowableCol(0, 1)
        for c in range(1, col+1):
            sizer.AddGrowableCol(c, 3)
        p.SetSizerAndFit(sizer)



    def __draw_input_panel(self, p):
        sizer = wx.GridBagSizer()
        sizer.SetSizeHints(p)

        row = 0
        self.masked_text = wx.richtext.RichTextCtrl(
            p, wx.ID_ANY
            , size=(1000, 80)
            , style=wx.TE_MULTILINE|wx.TE_READONLY
                |wx.VSCROLL|wx.NO_BORDER|wx.TE_RICH2|wx.TE_CENTRE)
        font_d = wx.Font(22, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier')
        self.masked_text.SetFont(font_d)
        sizer.Add(self.masked_text, 
            pos=(row,0), span=(1,2), flag=wx.ALL|wx.EXPAND)

        row += 1
        self.text = wx.richtext.RichTextCtrl(
            p, wx.ID_ANY
            , size=(1000, 100)
            , style=wx.TE_MULTILINE|wx.VSCROLL|wx.TE_RICH2|wx.TE_CENTRE)
        self.text.SetFont(font_d)
        sizer.Add(self.text, pos=(row,0), span=(1,2), flag=wx.ALL|wx.EXPAND)

        #self.text.Bind(wx.EVT_TEXT_ENTER, self.__on_text_enter)
        self.text.Bind(wx.EVT_TEXT, self.__on_text_edit)

        row += 1
        self.but_done = wx.Button(p, label="done", size=(50, 20))
        sizer.Add(self.but_done, pos=(row, 0), flag=wx.BOTTOM|wx.LEFT)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)

        # create acceleration table
        ctrEnter_id = wx.NewId()

        p.Bind(wx.EVT_MENU, self.__on_text_enter, id=ctrEnter_id)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, wx.WXK_RETURN, ctrEnter_id)
            ])
        p.SetAcceleratorTable(accel_tbl)



    def __draw_status_panel(self, p):
        sizer = wx.GridBagSizer()
        sizer.SetSizeHints(p)

        row = 0
        self.status_text = wx.richtext.RichTextCtrl(
            p, wx.ID_ANY
            , size=(1000, 200)
            , style=wx.TE_MULTILINE|wx.TE_READONLY
                |wx.VSCROLL|wx.NO_BORDER|wx.TE_RICH2|wx.TE_CENTRE)
        font_d = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier')
        self.status_text.SetFont(font_d)
        sizer.Add(self.status_text, pos=(row,0), flag=wx.ALL|wx.EXPAND)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)



    def __on_text_enter(self, event):
        entered_text = self.text.GetValue()
        stat = self.st.check_results(entered_text)
        self.status_text.SetCaretPosition(0)
        self.status_text.BeginTextColour(
            wx.Colour(200 * (1 - stat["rating"]), 130 * stat["rating"], 0))
        self.status_text.WriteText(stat["conclusion"] + "\n\n")

        if os.path.isfile(self.env["term_audio_blob_file"]):
            back_file = self.env["term_audio_blob_file"] + ".back"
            with open(self.env["term_audio_blob_file"], 'rb') as src \
                , open(back_file, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            self.play_audio(back_file)

        self.__start_test()



    def __on_text_edit(self, event):
        masked_text = self.masked_text.GetValue()
        entered_text = self.text.GetValue()
        mask = self.st.to_mask(entered_text)

        exact_match = True

        lmt = len(masked_text)
        for i in range(len(mask)):
            if i >= lmt:
                self.text.SetStyle(i, i+1, wx.TextAttr(wx.RED))
                exact_match = False
                continue

            if mask[i] == masked_text[i]:
                self.text.SetStyle(i, i+1, wx.TextAttr(wx.BLACK))
            else:
                self.text.SetStyle(i, i+1, wx.TextAttr(wx.RED))
                exact_match = False

        if lmt == len(mask) and exact_match:
            self.__on_text_enter(None)
    


    def __start_test(self):
        note = self.st.get_next_note()
        self.__show_current_note(note)
        self.text.SetValue("")
        self.text.SetFocus()



    def __show_current_note(self, note):
        self.env["current_note_id"] = note["id"]
        PluginLoader(self.env, "keystroke/LoadNoteMedia").process()
        self.__show_media()
        self.definition_note.SetValue(note["definition_note"])
        self.definition.SetValue(note["definition"])
        self.masked_text.SetValue(note["mask"])


    def play_audio(self, audio_file=None):
        if not audio_file:
            audio_file = self.env["term_audio_blob_file"]

        if not os.path.isfile(audio_file):
            return

        thread = Thread(target=self.__do_play_audio, args=(audio_file,))
        thread.start()
        thread.join()




    def __do_play_audio(self, audio_file):
        if not os.path.isfile(audio_file):
            return

        vlc_instance = vlc.Instance()
        player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(audio_file)
        player.set_media(media)
        player.play()



    
    def __on_play_audio(self, env):
        if not os.path.isfile(self.env["term_audio_blob_file"]):
            return

        self.play_audio()
        self.st.reduce_k_ratio()



    def __show_media(self):

        out_bitmap = PluginLoader(self.env, "ImageResize").process(
            original_bitmap=wx.Image(self.env["image_blob_file"]
                    , wx.BITMAP_TYPE_ANY).ConvertToBitmap() \
                if os.path.isfile(self.env["image_blob_file"]) \
                else wx.Image(self.env["no_image_jpg"]
                    , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            , image_size=self.image.GetSize() )

        self.image.SetBitmap(out_bitmap)
