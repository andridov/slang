import os
import sys
import glob
import json
import shutil
import sqlite3

from plugin_Base import PluginBase


class WordsDbUpdate(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)

        self.__deque_name = ""
        self.__term_language = ""
        self.__term_definition = ""



    def process(self, param_map=None):
        self.__get_deque_info()
        self.__read_data()
        self.__update_db_data()

        

    def __get_deque_info(self):
        self.__deque_name = self.env["prj_anki_pkg_file_name"]
        self.__deque_description = self.env["prj_description_file"]
        self.__term_language= self.env["prj_term_language"]
        self.__definition_language = self.env["prj_definition_language"]



    def __read_data(self):
        self.logger.info(
            "Reading file: {}".format(self.env["card_items_file"]))

        with open(self.env["card_items_file"], encoding="utf8") as f:
            self.env["card_items"] = json.load(f)



    def __update_db_data(self):
        self.logger.info(
            "Updating database {}".format(self.env["prj_database_file"]))

        self.__conn = sqlite3.connect(self.env["prj_database_file"])
        self.__cursor = self.__conn.cursor()

        language_id = 0
        self.__cursor.execute(self.env["sql_insert_language"].format(
            term_language=self.__term_language
            , definition_language=self.__definition_language))
        self.__cursor.execute(self.env["sql_select_language"].format(
            term_language=self.__term_language
            , definition_language=self.__definition_language))
        records = self.__cursor.fetchall()
        language_id = records[0][0]
        self.logger.info("language_id = {}".format(language_id))

        tags_scope_id = self.__insert_scope()

        deque_id = 0
        self.__cursor.execute(self.env["sql_insert_deque"], (self.__deque_name
            , language_id, self.__deque_description, tags_scope_id))
        self.__cursor.execute(self.env["sql_select_deque"].format(
            file_name=self.__deque_name, language_id=language_id))
        records = self.__cursor.fetchall()
        deque_id = records[0][0]
        deque_version = records[0][4]
        if not self.__deque_description:
            self.__deque_description = records[0][5]

        # find and delete existing cards/notes/media
        # TODO: should be update only, without deleting.
        for delete_instruction in self.env["sql_delete_deque_instructions"]:
            self.__cursor.execute(delete_instruction.format(deque_id=deque_id))

        for card in self.env["card_items"]:
            self.__insert_card(deque_id, card)

        # update deque data (version, and description)
        deque_version += 1
        self.__cursor.execute(self.env["sql_update_deque"].format(
            deque_id=deque_id
            , version=deque_version
            , description=self.__deque_description))

        self.__conn.commit()
        self.__conn.close()

        self.logger.info("Updating database is finished")



    def __insert_tag(self, tag_name, tag_description=None):
        self.__cursor.execute(self.env["sql_insert_tag"], (tag_name
            , tag_description))
        self.__cursor.execute(self.env["sql_select_tag"], (tag_name,))
        records = self.__cursor.fetchall()
        tag_id = records[0][0]
        if not tag_id:
            self.logger.error("Can't create tag, name: {}".fromat(tag_name))
        return tag_id



    def __insert_scope(self):
        if not self.env["cmd_known_args"].tags:
            return None

        tags_list = self.env["cmd_known_args"].tags
        if not len(tags_list):
            return None

        self.__cursor.execute(self.env["sql_select_type"], ("tag",))
        records = self.__cursor.fetchall()
        scope_type_id = records[0][0]

        self.__cursor.execute(self.env["sql_select_next_scope_id"], ("tag",))
        records = self.__cursor.fetchall()
        scope_id = records[0][0]

        for tag_name in tags_list:
            tag_id = self.__insert_tag(tag_name)
            self.__cursor.execute(self.env["sql_insert_scope"], 
                (scope_type_id, scope_id, tag_id))

        return scope_id



    def __insert_card(self, deque_id, card):
        if not card or not deque_id:
            return

        self.__cursor.execute(self.env["sql_insert_card"].format(
            deque_id=deque_id))
        self.__cursor.execute(self.env["sql_select_empty_card"].format(
            deque_id=deque_id))
        records = self.__cursor.fetchall()
        card_id = records[0][0]

        notes = []
        note_ids = []

        notes.append(card)
        notes.extend(card["examples"])
        for note in notes:
            
            prefix = self.env["words_db_note_prefix"] 
            if prefix in note["term_note"] or prefix in note["definition_note"]:
                # skip the notes already imported from other deques
                continue

            # self.logger.debug("words_db adding: {}".format(note["term"]))
            # insert blobs to database
            term_audio_id = self.__insert_media(note["term_audio"])
            image_id = self.__insert_media(note["image"])
            definition_audio_id = self.__insert_media(note["definition_audio"])

            self.__cursor.execute(self.env["sql_insert_note"], (
                card_id
                , note["creation_time"]
                , note["mod_time"]
                , note["term"]
                , note["term_note"]
                , term_audio_id
                , image_id
                , note["definition"]
                , note["definition_note"]
                , definition_audio_id))

            note_ids.append(self.__cursor.lastrowid)

        note_len = len(note_ids)
        self.__cursor.execute(self.env["sql_update_card"].format(
            card_id=card_id
            , deque_id=deque_id
            , base_note_id = note_ids[0]
            , ex_1_note_id = note_ids[1] if note_len > 1 else 'NULL' 
            , ex_2_note_id = note_ids[2] if note_len > 2 else 'NULL'
            , ex_3_note_id = note_ids[3] if note_len > 3 else 'NULL'
            , ex_4_note_id = note_ids[4] if note_len > 4 else 'NULL'
            , ex_5_note_id = note_ids[5] if note_len > 5 else 'NULL'))




    def __insert_media(self,  media_file):
        if not media_file or not os.path.isfile(media_file):
            return "NULL"

        with open(media_file, 'rb') as file:
            media_blob = file.read()
            self.__cursor.execute(
                self.env["sql_insert_media"], (sqlite3.Binary(media_blob), ))
            return self.__cursor.lastrowid

        return "NULL"

