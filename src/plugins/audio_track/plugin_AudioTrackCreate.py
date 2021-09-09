# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import re
import sqlite3

from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase


class AudioTrackCreate(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)

        self._db_name = "database/slang/QDB2"
        


    def process(self, **kwargs):
        self.logger.info("AudioTrackCreate started")
        notes = self.__get_notes_list()
        self.__process_notes(notes)



    def __get_notes_list(self):
        results = PluginLoader(self.env, self._db_name).process(
            query="sql_select_notes")["sql_select_notes"]

        self.logger.info(f"notes found: {len(results)}")
        
        notes = []
        for res in results:
            note = {}
            note["id"] = res[0]
            # last_used_time
            # next_use_time
            note["pace_time"] = res[3]
            note["term"] = res[4]
            note["term_audio_id"] = res[5]
            note["definition"] = res[6]
            note["definition_audio_id"] = res[7]
            notes.append(note)

        return notes



    def __process_notes(self, notes):
        for note in notes:
            self.__process_note(note)
    


    def __process_note(self, note):
        media = self.__check_and_load_media(note)
        if len(media) != 2:
            self.logger.warning(
                "Not enough content in media! " \
                f"Note ( id={note['id']} term='{note['term']}' )" \
                " will be skipped !!!")
            return

        self.__append_media(media)



    def __check_and_load_media(self,note):
        return ()


    def __append_media(self, media):
        import inspect
        self.logger.error("Not implemented {}".format(
            inspect.currentframe().f_code.co_name))
        pass

