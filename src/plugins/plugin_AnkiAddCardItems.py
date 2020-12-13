# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sqlite3
import shutil
import random
import string
import time
import re
import json

from hashlib import sha1
from copy import deepcopy

from plugin_Base import PluginBase

class AnkiAddCardItems(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)

        self.__current_time = lambda: int(round(time.time() * 1000))

        self.__conn = sqlite3.connect(self.env["prj_anki_db_file"])
        self.__cursor = self.__conn.cursor()
        self.__read_db_stat_settings()



    def process(self, **kwargs):

        card_items_list = self.env["card_items_list"]


        for item in card_items_list:
            data = "adding card: [{} -- {}]".format(item["term"], item["definition"])
            self.logger.info(data.encode("utf-8"))
            self.__add_card_item(self.__create_full_item(item))

        self.close()



    def close(self):
        self.__save_db_stat_settings()

        self.__conn.commit()
        self.__conn.close()



    def __save_db_stat_settings(self):
        anki_settings = [
            { "anki_db_next_media_id": self.__media_id },
            { "anki_db_desk_id": self.k_desk_id },
            { "anki_db_model_id": self.k_model_id }
        ]
        with open(self.env["prj_anki_env_file"], 'w') as jf:
            json.dump(anki_settings, jf, 
                indent=2, ensure_ascii=False, sort_keys=False)



    def __create_full_item(self, card_item):
        full_card_item = deepcopy(self.env["card_item_template"])
        fields = self.env["item_fields"]

        for f in fields:
            full_card_item[f] = card_item[f]

        ex = card_item["examples"]
        item_ex = full_card_item["examples"]
        length = len(ex)
        for i in range(length):
            for f in fields:
                item_ex[i][f] = ex[i][f]
 
        return full_card_item



    def __autoincrement_card_id(self):
        id = self.last_card_id 
        self.last_card_id += 1
        return id



    def __add_card_item(self, card_item):
        if self.__chk_db_contains(card_item["term"].replace("'", "`")):
            self.logger.warning(
                "item: [{} -- {}] already present in db. skipped".format(
                    card_item["term"].encode('utf-8')
                    , card_item["definition"].encode('utf-8')))
            return

        examples = card_item["examples"]
        for itm in [card_item
            , examples[0]
            , examples[1]
            , examples[2]
            , examples[3]
            , examples[4] ]:

            self.__prepare_media_for_item(itm)

        """saves card to db: 3 rows, one for table `notes` and two for table `cards`: front and back"""
        note_id = self.__add_note(card_item)              # first save note and get its id
        card_id = self.__get_next_cards_id()
        card_nid = note_id                           # id of newly created note row
        card_did = self.k_desk_id                    # desk id
        card_ord = 0
        card_mod = self.__current_time()
        card_usn = -1
        card_type = 0
        card_queue = 0
        card_due = card_id                           # new 
        card_ivl = 0
        card_factor = 2500
        card_reps = 0
        card_lapses = 0
        card_left = 1001
        card_odue = 0
        card_odid = 0
        card_flags = 0
        card_data = ""

        self.logger.info((card_id,      card_nid,     card_did,
                card_ord,     card_mod,     card_usn,
                card_type,    card_queue,   card_due,
                card_ivl,     card_factor,  card_reps,
                card_lapses,  card_left,    card_odue,
                card_odid,    card_flags,   card_data))
        self.__cursor.execute(self.env["sql_insert_card"],
            (card_id,      card_nid,     card_did,
                card_ord,     card_mod,     card_usn,
                card_type,    card_queue,   card_due,
                card_ivl,     card_factor,  card_reps,
                card_lapses,  card_left,    card_odue,
                card_odid,    card_flags,   card_data))

        # next entry (reverse card) differs:
        card_id = self.__get_next_cards_id()
        card_ord = 1
        card_left = 0

        self.__cursor.execute(self.env["sql_insert_card"],
            (card_id,      card_nid,     card_did,
             card_ord,     card_mod,     card_usn,
             card_type,    card_queue,   card_due,
             card_ivl,     card_factor,  card_reps,
             card_lapses,  card_left,    card_odue,
             card_odid,    card_flags,   card_data))



    def __read_db_stat_settings(self):
        self.__media_id = self.env["anki_db_next_media_id"]
        self.k_desk_id = self.env["anki_db_desk_id"]
        self.k_model_id = self.env["anki_db_model_id"]



    def __read_db_stat(self):
        #read 
        self.__read_db_stat_settings()

        self.logger.info(
            "current db values are:\n"
            "   desk_id = {}\n"
            "   model_id = {}\n"
            "   last_card_id = {}\n"
            "   last_note_id = {}".format(
                self.k_desk_id
                , self.k_model_id
                , self.last_card_id
                , self.last_note_id))


    def __get_next_table_id(self, table_name, id):
        request = self.env["sql_get_next_table_id"].format(
            table=table_name, id=id);
        self.__cursor.execute(request);
        result = self.__cursor.fetchall()
        result_id = result[0][0]
        return result_id



    def __get_next_cards_id(self):
        # the epoch milliseconds of when the card was created
        return self.__get_next_table_id("cards", self.__current_time())


    def __get_next_notes_id(self):
        # id is epoch seconds of when the note was created
        current_time = self.__current_time() // 1000
        return self.__get_next_table_id("notes", current_time)


    def __get_media_id(self):
        id = self.__media_id
        self.__media_id += 1
        return id


    def __create_media_id_name(self, file_name):
        fname, file_extension = os.path.splitext(file_name)
        id_file = str(self.__get_media_id()) + file_extension
        return id_file



    def __prepare_media_for_item(self, item):
        media_dir = self.env["prj_anki_media_dir"]
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        item["term_audio_dst"] = ""
        item["definition_audio_dst"] = ""
        audio_dir = self.env["prj_audio_dir"]
        if ("term_audio" in item 
            and item["term_audio"] != ""
            and self.__chk_file(item["term_audio"])):

            src_file = item["term_audio"]
            item["term_audio_dst"] = self.__create_media_id_name(src_file)
            dst_file = "{}/{}".format(media_dir, item["term_audio_dst"])
            shutil.copyfile(src_file, dst_file)

        if ("definition_audio" in item 
            and item["definition_audio"] != ""
            and self.__chk_file(item["definition_audio"])):

            src_file = item["definition_audio"]
            item["definition_audio_dst"] = self.__create_media_id_name(src_file)
            dst_file = "{}/{}".format(media_dir, item["definition_audio_dst"])
            shutil.copyfile(src_file, dst_file)

        item["image_dst"] = ""
        image_dir = self.env["prj_image_dir"]
        if ("image" in item 
            and item["image"] != ""
            and self.__chk_file(item["image"])):

            src_file = item["image"]
            item["image_dst"] = self.__create_media_id_name(src_file)
            dst_file = "{}/{}".format(media_dir, item["image_dst"])
            shutil.copyfile(src_file, dst_file)



    def __chk_db_contains(self, term):
        self.__cursor.execute(
            "select count() from notes where sfld = '{}'".format(term))
        result = self.__cursor.fetchall()

        if result[0][0] == 0:
            return False

        return True



    def __chk_file(self, media_file_name):
        if not os.path.isfile(media_file_name):
            self.logger.error(
                "file [{}] does not exists".format(media_file_name))
            return False
        return True 


    def __autoincrement_note_id(self):
        id = self.last_note_id
        self.last_note_id += 1
        return id


    # used in ankiweb
    def __base62(self, num, extra=""):
        s = string; table = s.ascii_letters + s.digits + extra
        buf = ""
        while num:
            num, i = divmod(num, len(table))
            buf = table[i] + buf
        return buf




    def __base91(self, num):
        base91_extra_chars = "!#$%&()*+,-./:;<=>?@[]^_`{|}~"

        # all printable characters minus quotes, backslash and separators
        return self.__base62(num, base91_extra_chars)


    def __guid64(self):
            "Return a base91-encoded 64bit random number."
            return self.__base91(random.randint(0, 2**64-1))



    def __chck_val(self, field, type='text'):
        if not field:
            return ""

        f = field.encode('utf8')
        self.logger.info('f -- {}: {}'.format(type, f))

        if type == 'text': 
            return field

        if type == 'sound':
            return '[sound:{}]'.format(field)

        if type == 'image':
            return '<img src="{}"/>'.format(field)

        self.logger.error("cheking value: undefined type [{}]"
            " for value[{}]".format(type, value))
        return ""


    def __entsToTxt(self, html):
        # entitydefs defines nbsp as \xa0 instead of a standard space, so we
        # replace it first
        html = html.replace("&nbsp;", " ")
        reEnts = re.compile(r"&#?\w+;")


        def fixup(m):

            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return chr(int(text[3:-1], 16))
                    else:
                        return chr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = chr(name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text # leave as is
        return reEnts.sub(fixup, html)


    def __stripHTML(self, s):
        reStyle = re.compile(r"(?si)<style.*?>.*?</style>")
        reScript = re.compile(r"(?si)<script.*?>.*?</script>")
        reTag = re.compile(r"<.*?>")

        s = reStyle.sub("", s)
        s = reScript.sub("", s)
        s = reTag.sub("", s)
        s = self.__entsToTxt(s)
        return s

    def __stripHTMLMedia(self, s):
        reMedia = re.compile(r"(?i)<img[^>]+src=[\"']?([^\"'>]+)[\"']?[^>]*>")

        "Strip HTML but keep media filenames"
        s = reMedia.sub(" \\1 ", s)
        return self.__stripHTML(s)

    def __checksum(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        return sha1(data).hexdigest()


    def __fieldChecksum(self, data):
        # 32 bit unsigned number from first 8 digits of sha1 hash
        return int(self.__checksum(
            self.__stripHTMLMedia(data).encode("utf-8"))[:8], 16)


    def __add_note(self, card_item):

        """ saves one entry to db table `notes` and returns the id of new entry"""
        note_id = self.__get_next_notes_id()
        note_guid = self.__guid64()
        note_mid = self.k_model_id  # model id (info in table `col`)
        note_mod = self.__current_time()
        note_usn = -1
        note_tags = "" # tags is space separated string, we only have one word for tag

        examples = card_item["examples"]
        note_flds = "\x1f".join([
            card_item["term"], #mandatory
            self.__chck_val(card_item["term_note"]),
            self.__chck_val(card_item["term_audio_dst"], 'sound'),
            self.__chck_val(card_item["image_dst"], 'image'),
            card_item["definition"], #mandatory
            self.__chck_val(card_item["definition_note"]),
            self.__chck_val(card_item["definition_audio_dst"], 'sound'),

            self.__chck_val(examples[0]["term"]),
            self.__chck_val(examples[0]["term_note"]),
            self.__chck_val(examples[0]["term_audio_dst"], 'sound'),
            self.__chck_val(examples[0]["image_dst"], 'image'),
            self.__chck_val(examples[0]["definition"]),
            self.__chck_val(examples[0]["definition_note"]),
            self.__chck_val(examples[0]["definition_audio_dst"], 'sound'),

            self.__chck_val(examples[1]["term"]),
            self.__chck_val(examples[1]["term_note"]),
            self.__chck_val(examples[1]["term_audio_dst"], 'sound'),
            self.__chck_val(examples[1]["image_dst"], 'image'),
            self.__chck_val(examples[1]["definition"]),
            self.__chck_val(examples[1]["definition_note"]),
            self.__chck_val(examples[1]["definition_audio_dst"], 'sound'),

            self.__chck_val(examples[2]["term"]),
            self.__chck_val(examples[2]["term_note"]),
            self.__chck_val(examples[2]["term_audio_dst"], 'sound'),
            self.__chck_val(examples[2]["image_dst"], 'image'),
            self.__chck_val(examples[2]["definition"]),
            self.__chck_val(examples[2]["definition_note"]),
            self.__chck_val(examples[2]["definition_audio_dst"], 'sound'),

            self.__chck_val(examples[3]["term"]),
            self.__chck_val(examples[3]["term_note"]),
            self.__chck_val(examples[3]["term_audio_dst"], 'sound'),
            self.__chck_val(examples[3]["image_dst"], 'image'),
            self.__chck_val(examples[3]["definition"]),
            self.__chck_val(examples[3]["definition_note"]),
            self.__chck_val(examples[3]["definition_audio_dst"], 'sound'),

            self.__chck_val(examples[4]["term"]),
            self.__chck_val(examples[4]["term_note"]),
            self.__chck_val(examples[4]["term_audio_dst"], 'sound'),
            self.__chck_val(examples[4]["image_dst"], 'image'),
            self.__chck_val(examples[4]["definition"]),
            self.__chck_val(examples[4]["definition_note"]),
            self.__chck_val(examples[4]["definition_audio_dst"], 'sound')
        ])

        note_sfld = "{0}".format(card_item["term"])
        note_csum = self.__fieldChecksum(note_flds[0])
        note_flags = 0
        note_data = 0
        # insert into table `notes`
        self.__cursor.execute(
            self.env["sql_insert_note"],
            (note_id,  note_guid, note_mid,
            note_mod, note_usn, note_tags,
            note_flds, note_sfld,  note_csum,
            note_flags, note_data))
        return note_id



            