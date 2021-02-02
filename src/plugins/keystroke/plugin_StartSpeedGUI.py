# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import re
import wx
import wx.richtext
import sqlite3
import time
import random
import math
from fuzzywuzzy import fuzz

from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase


class StartSpeedGUI(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        self.__draw_gui()


    def __draw_gui(self):

        p = self.env["win_panel"]
        sizer = wx.GridBagSizer()

        row = 0
        col = 0

        stats_panel_row = row    
        stats_panel = wx.Panel(p, size=(-1, 80))
        sizer.Add(stats_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_stats_panel(stats_panel)

        row += 1
        note_panel_row = row 
        note_panel = wx.Panel(p, size=(-1, 200))
        sizer.Add(note_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_note_panel(note_panel)
        
        row += 1
        typing_panel_row = row    
        typing_panel = wx.Panel(p, size=(-1, 200))
        sizer.Add(typing_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_typing_panel(typing_panel)

        row += 1
        keyboard_panel_row = row
        keyboard_panel = wx.Panel(p)
        sizer.Add(keyboard_panel, pos=(row,col), flag=wx.EXPAND)
        self.__draw_keyboard_panel(keyboard_panel)

        p.SetSizer(sizer)
        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(note_panel_row)
        sizer.AddGrowableRow(typing_panel_row)
        sizer.AddGrowableCol(col)
        p.SetSizerAndFit(sizer)

        self._start_lesson()
        self.type_text.SetFocus()




    def __draw_note_panel(self, p):
        sizer = wx.GridBagSizer()
        p.SetSizer(sizer)

        row = 0
        col = 1

        self.term_note = wx.TextCtrl(p
            , style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER)
        sizer.Add(self.term_note
            , pos=(row, col)
            , flag=wx.EXPAND|wx.ALL
            , border=0)

        row += 1
        self.definition_note = wx.TextCtrl(p
            , style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER)
        sizer.Add(self.definition_note
            , pos=(row, col)
            , flag=wx.EXPAND|wx.ALL
            , border=0)

        row += 1
        self.definition = wx.TextCtrl(p
            , style=wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER)
        font_d = wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier')
        self.definition.SetFont(font_d)
        sizer.Add(self.definition
            , pos=(row, col)
            , flag=wx.EXPAND|wx.ALL
            , border=0)


        self.original_bitmap = wx.Image(self.env["no_image_jpg"]
            , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.image_window = wx.Panel(p)
        self.image = wx.StaticBitmap(self.image_window)
        sizer.Add(self.image_window
            , pos=(0, 0)
            , span=(row+1, 0)
            , flag=wx.SHAPED|wx.ALL)
        self.image.SetBitmap(self.original_bitmap)


        for r in range(row+1):
            sizer.AddGrowableRow(r)
        sizer.AddGrowableCol(1)
        p.SetSizerAndFit(sizer)




    def __draw_stats_panel(self, p):
        sizer = wx.GridBagSizer()

        col = 0
        # Speed spm / wpm
        lbl_speed = wx.StaticText(p, -1, "speed (symb,words/per min)")
        sizer.Add(lbl_speed
            , pos=(0, col), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        
        font_d = wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Arial')
        self.speed = wx.TextCtrl(p, style=wx.TE_CENTRE|wx.TE_READONLY)
        self.speed.SetFont(font_d)
        self.speed.SetForegroundColour((0, 180, 0))
        sizer.Add(self.speed, pos=(1, col), flag=wx.EXPAND|wx.ALL)

        # Errors count
        col += 1
        lbl_errors = wx.StaticText(p, -1, "erors count")
        sizer.Add(lbl_errors
            , pos=(0, col), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.errors_count = wx.TextCtrl(p, style=wx.TE_CENTRE|wx.TE_READONLY)
        self.errors_count.SetFont(font_d)
        self.errors_count.SetForegroundColour((210, 0, 0))
        sizer.Add(self.errors_count, pos=(1, col), flag=wx.EXPAND|wx.ALL)

        # WorkoutTime
        col += 1
        lbl_time = wx.StaticText(p, -1, "time (sec)")
        sizer.Add(lbl_time
            , pos=(0, col), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.time = wx.TextCtrl(p, style=wx.TE_CENTRE|wx.TE_READONLY)
        self.time.SetFont(font_d)
        self.time.SetForegroundColour((0, 0, 190))
        sizer.Add(self.time, pos=(1, col), flag=wx.EXPAND|wx.ALL)
        
        # Notes count
        col += 1
        lbl_notes = wx.StaticText(p, -1, "notes count")
        sizer.Add(lbl_notes
            , pos=(0, col), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.notes_count = wx.TextCtrl(p, style=wx.TE_CENTRE|wx.TE_READONLY)
        self.notes_count.SetFont(font_d)
        self.notes_count.SetForegroundColour((0, 0, 0))
        sizer.Add(self.notes_count, pos=(1, col), flag=wx.EXPAND|wx.ALL)

        # Words count
        col += 1
        lbl_symbols = wx.StaticText(p, -1, "symbols count")
        sizer.Add(lbl_symbols
            , pos=(0, col), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.symbols_count = wx.TextCtrl(p, style=wx.TE_CENTRE|wx.TE_READONLY)
        self.symbols_count.SetFont(font_d)
        self.symbols_count.SetForegroundColour((0, 0, 0))
        sizer.Add(self.symbols_count, pos=(1, col), flag=wx.EXPAND|wx.ALL)

        col += 1
        btn_stat = wx.Button(p, label="stat")
        sizer.Add(btn_stat, pos=(0, col), span=(2, 0), flag=wx.EXPAND|wx.ALL)
        p.Bind(wx.EVT_BUTTON, self.__on_stat,  btn_stat)

        p.SetSizer(sizer)
        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(0)
        for c in range(col):
            sizer.AddGrowableCol(c)
        p.SetSizerAndFit(sizer)



    def __draw_typing_panel(self, p):
        p.SetBackgroundColour((100, 130, 100))
        sizer = wx.GridBagSizer()

        row = 0
        self.status_text = wx.richtext.RichTextCtrl(
            p, wx.ID_ANY, size=(1, 250)
            , style=
                wx.TE_MULTILINE
                |wx.TE_READONLY
                |wx.VSCROLL
                |wx.NO_BORDER
                |wx.TE_RICH2)
        sizer.Add(self.status_text, pos=(row,0), flag=wx.ALL|wx.EXPAND)

        self.status_text_active_color = (200, 200, 200)
        self.status_text_inactive_color = (140, 140, 140)
        self.status_text.BeginFontSize(15)
        self.status_text.BeginTextColour(self.status_text_inactive_color)
        self.status_text.EndFontSize()

        row =+ 1
        self.type_text = wx.TextCtrl(p, style=wx.TE_PROCESS_ENTER)
        font_d = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Arial')
        self.type_text.SetFont(font_d)

        sizer.Add(self.type_text, pos=(row,0), flag=wx.EXPAND)
        self.type_text.Bind(wx.EVT_TEXT_ENTER, self.__on_text_enter)
        self.type_text.Bind(wx.EVT_TEXT, self.__on_text_edit)


        p.SetSizer(sizer)
        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)
       

    def __draw_keyboard_panel(self, p):
        # p.SetBackgroundColour((100, 100, 130))
        sizer = wx.GridBagSizer()

        # self.button_panel = wx.Panel(p, -1)
        # sizer.Add(self.bottom_panel
        #     , pos=(row, 0), flag=wx.ALIGN_BOTTOM|wx.EXPAND)
        # bottom_sizer = wx.GridBagSizer()

        p.SetSizer(sizer)
        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)


    def __on_text_enter(self, event):
        word = str(self.type_text.GetValue())
        word = re.sub('[\r\n\t ]', '', word)
        self.type_text.SetValue("")
        self._process_entered_word(word)


    def __on_text_edit(self, event):
        self.start_time()
        word = str(self.type_text.GetValue())
        if ' ' in word:
            self.type_text.SetValue("")
            word = re.sub('[\r\n\t ]', '', word)
            self._process_entered_word(word.split(' ')[0])


    def __on_stat(self, event):

        pass


    def _set_test_text(self, text):
        self.status_text.BeginTextColour(self.status_text_inactive_color)
        self.status_text.SetValue(text)


    def _show_note(self, note):
        self.term_note.SetValue(note["term_note"])
        self.definition.SetValue(note["definition"])
        self.definition_note.SetValue(note["definition_note"])


    def _show_media(self):
        out_bitmap = PluginLoader(self.env, "ImageResize").process(
            original_bitmap=wx.Image(self.env["image_blob_file"]
                    , wx.BITMAP_TYPE_ANY).ConvertToBitmap() \
                if os.path.isfile(self.env["image_blob_file"]) \
                else wx.Image(self.env["no_image_jpg"]
                    , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            , image_size=self.image_window.GetSize() )
        
        self.image.SetBitmap(out_bitmap)
        



    def _show_pwerv_stats(self
        , speed_spm, speed_wpm, errors_count, time, notes_count, symbols_count):
        self.speed.SetValue("{:.1f} -- {:.1f}".format(speed_spm, speed_wpm))
        self.errors_count.SetValue("{}".format(errors_count))
        self.time.SetValue("{:.1f}".format(time))
        self.notes_count.SetValue("{}".format(notes_count))
        self.symbols_count.SetValue("{}".format(symbols_count))



# ******************************************************************************

    def _start_lesson(self):
        self._show_stats()
        self.__start_time = None

        # clear
        self.__words = []
        self.__words_entered = []

        # fulsh stats
        self.current_pos = 0;
        self.currnet_word = 0;
        self.current_note = 0;
        self.current_word_in_note = 0;

        # load words
        self.__load_words_from_notes()
        self._set_test_text(" ".join(w for w in self.__words))
        self.__select_current_note()
        # self.logger.info(self.__words)

    def _show_stats(self):
        sql_query_item = {}
        sql_query_item["query"] = self.env["sql_select_speed_test_history"]
        sql_query_item["data"] = ()
        self.env["sql_queries_list"] = [ sql_query_item ]
        q_res = PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list=[{
                "query": self.env["sql_select_speed_test_history"]
                , "data":() }])

        self.__stat_items = []
        for i in q_res[0]:
            item = {}
            item["id"] = i[0]
            item["start_time"] = i[1]
            item["end_time"] = i[2]
            item["notes_count"] = i[3]
            item["symbols_count"] = i[4]
            item["speed_wpm"] = i[5]
            item["speed_spm"] = i[6]
            item["err_words_count"] = i[7]

            self.__stat_items.append(item)

        if len(self.__stat_items):
            li = self.__stat_items[-1] # last itew for show statistic
            self._show_pwerv_stats(li["speed_spm"]
                , li["speed_wpm"]
                , li["err_words_count"]
                , li["end_time"] - li["start_time"]
                , li["notes_count"]
                , li["symbols_count"])
        else:
            self._show_pwerv_stats(0, 0, 0, 0, 0, 0)


    def start_time(self):
        if not self.__start_time:
            self.__start_time = time.time()


    def _finish_lesson(self):
        # sl_slang_database_file
        start_time = self.__start_time
        end_time = time.time()
        overall_time = end_time - start_time
        notes_count = len(self.__notes)
        words_count = len(self.__words)
        symbols_count = 0
        for w in self.__words_entered:
            symbols_count = symbols_count + len(w)
        symbols_count += len(self.__words_entered) 
        speed_wpm = words_count / overall_time * 60
        speed_spm = symbols_count / overall_time  * 60
        
        text_results = self.__check_text_correctness()
        err_words_count = len(text_results)
        err_notes_ids_set = set(x["note_id"] for x in text_results)
        err_notes_count = len(err_notes_ids_set)
        err_notes_scope_id = None

        self.logger.info("Results info:")
        self.logger.info("Overall_time: {}".format(overall_time))
        self.logger.info("Notes count: {}".format(len(self.__notes)))
        self.logger.info("Words count: {}".format(len(self.__words)))
        self.logger.info("Symbols_count count: {}".format(symbols_count))
        self.logger.info("Speed wpm: {}".format(speed_wpm))
        self.logger.info("Speed spm: {}".format(speed_spm))
        self.logger.info("Incorrect words: {}".format(err_words_count))
        self.logger.info("Incorrect notes: {}".format(err_notes_count))
        self.logger.info("Errors:")
        for tr in text_results:
            self.logger.info("\t{}: {} <=> {}".format(
                tr["note_id"], tr["incorrect"], tr["correct"]))

        note_scope_id = PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list=[{ "query": self.env["sql_select_next_scope_id"]
                , "data": ( "note", ) }])[0][0][0]

        note_ids_scope = note_scope_id

        queries_list = []
        for n in self.__notes:
            sql_query_item = {}
            sql_query_item["query"] = self.env["sql_insert_item_to_scope"]
            sql_query_item["data"] = ("note", note_ids_scope, n["id"])
            queries_list.append(sql_query_item)
        PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list=queries_list)

        if (err_notes_count > 0):
            note_scope_id +=1
            err_note_ids_scope = note_scope_id
            queries_list = []
            for enid in err_notes_ids_set:
                sql_query_item = {}
                sql_query_item["query"] = self.env["sql_insert_item_to_scope"]
                sql_query_item["data"] = ('note', err_note_ids_scope, enid)
                queries_list.append(sql_query_item)
            PluginLoader(self.env, self.env["sl_db_query"]).process(
                queries_list=queries_list)
        else:
            err_note_ids_scope = None


        PluginLoader(self.env, self.env["sl_db_query"]).process(
             queries_list=[{
                "query": self.env["sql_insert_speed_test_result"]
                , "data": ( start_time, end_time
                    , notes_count, note_ids_scope
                    , words_count, symbols_count
                    , speed_wpm, speed_spm
                    , err_notes_count, err_note_ids_scope
                    , err_words_count) }])

        self.__save_achievements()



    def __check_text_correctness(self):
        result = []
        word_in_note = 0
        current_note = 0
        self.__notes[current_note]["words_entered"]  = []

        for i in range(len(self.__words_entered)):

            if self.__words[i] != self.__words_entered[i]:
                item = {}
                item["correct"] = self.__words[i]
                item["incorrect"] = self.__words_entered[i]
                item["note_id"] = self.__notes[current_note]["id"]
                result.append(item)

            self.__notes[current_note]["words_entered"].append(
                self.__words_entered[i])

            word_in_note += 1
            if word_in_note >= len(self.__notes[current_note]["words"]):
                current_note += 1
                if current_note >= len(self.__notes):
                    return result
                word_in_note = 0
                self.__notes[current_note]["words_entered"] = []

        return result


    def __save_achievements(self):

        requests = []
        for n in self.__notes:
            self.__rate_note(n)
            sql_query_item = {}
            sql_query_item["query"] = self.env["sql_update_achievement"]
            sql_query_item["data"] = ('note'
                , n["id"] # item_id
                , time.time() # last_used_time
                , n["pace_time"]
                , 0 # learning_status_id
                , n["repeat_factor"]
                , n["pace_factor"]
                , n["reviews_count"])

            requests.append(sql_query_item)

        PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list=requests)


    def __rate_note(self, note):
        source_text = " ".join(w for w in note["words"])
        entered_text = " ".join(w for w in note["words_entered"])

        fr = fuzz.ratio(source_text, entered_text) / 100
        k = 1.0 + math.tanh(50 * fr - 47)
        note["pace_time"] = note["pace_time"] * k
        time_interval = int(self.env["minimal_time_interval_str"])
        if note["pace_time"] < time_interval:
            note["pace_time"] = time_interval



    def __load_words_from_notes(self):
        self.__notes = []
        self.__words = []

        conn = sqlite3.connect(self.env["sl_slang_database_file"])
        cursor = conn.cursor()

        cursor.execute(self.env["sql_select_expired_notes"].format(
            count=self.env["notes_per_test"]))
        records = cursor.fetchall()
        for r in records:
            self.__add_note(r)

        if self.env["notes_per_test"] > len(self.__notes):
            cursor.execute(self.env["sql_select_new_notes"].format(
                count=self.env["notes_per_test"] - len(self.__notes)))
            records = cursor.fetchall()
            for r in records:
                self.__add_note(r)

        conn.commit()
        conn.close()

        random.shuffle(self.__notes)
        for n in self.__notes:
            self.__words += n["words"]


    def __add_note(self, rec):
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
                "Note id={} has empty 'term bield, skipped'".format(note["id"]))
            return;

        note["words"] = self.__preprocess_term(note["term"])
        self.__notes.append(note)
        

    def __preprocess_term(self, text):
        words = [ (w) for w in re.findall("[\\S]+", text)]
        return words
        


    def _select_next_word(self):

        if self.currnet_word >= len(self.__words):
            self._finish_lesson()
            self._start_lesson()
            return
        
        # color current word accordingly to result
        self.status_text.SetStyle(
            self.current_pos
            , self.current_pos + len(self.__words[self.currnet_word])
            , wx.TextAttr(self.cecked_word_color))
        # save to check results later
        self.__words_entered.append(self.word_entered)
        #increment 
        self.current_pos += len(self.__words[self.currnet_word]) + 1
        self.currnet_word += 1
        self.current_word_in_note += 1

        if self.currnet_word >= len(self.__words):
            self._finish_lesson()
            self._start_lesson()
            return

        if self.current_word_in_note == \
            len(self.__notes[self.current_note]["words"]):
            self.current_word_in_note = 0
            self.current_note += 1
            self.__select_current_note()



    def __select_current_note(self):
        self.env["current_note_id"] = self.__notes[self.current_note]["id"]
        PluginLoader(self.env, "keystroke/LoadNoteMedia").process()
        self._show_media()
        self._show_note(self.__notes[self.current_note])



    # def __load_media(self):
    #     def write_to_file(data, file_name):
    #         if data:
    #             with open(file_name, 'wb') as file:
    #                 file.write(data)
    #                 return
    #         if os.path.isfile(file_name):
    #             os.remove(file_name)

    #     note = self.__notes[self.current_note]

    #     conn = sqlite3.connect(self.env["sl_slang_database_file"])
    #     cursor = conn.cursor()

    #     cursor.execute(self.env["sql_select_note_media"], (note["id"],))
    #     record = cursor.fetchall()
    #     for row in record:
    #         write_to_file(row[0], self.env["image_blob_file"])
    #         write_to_file(row[1], self.env["term_audio_blob_file"])
    #         write_to_file(row[2], self.env["definigion_audio_blob_file"])

    #     conn.commit()
    #     conn.close()
        



    def _chek_current_word(self, word):
        word = word.strip()
        if not word:
            return False

        m = re.findall("[\\S]+", word)
        if not m:
            return False


        if self.currnet_word >= len(self.__words): 
             return True

        self.word_entered = word
        self.cecked_word_color = \
            wx.BLACK if word == self.__words[self.currnet_word] else wx.RED

        return True



    def _process_entered_word(self, word):
        if self._chek_current_word(word):
            self._select_next_word()




