import os
import re
import sqlite3


from plugin_Base import PluginBase

class FindOtherSamples(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)


    def process(self, **kwargs):
        if "sl_slang_db_add_older_notes" not in self.env \
            or not self.env["sl_slang_db_add_older_notes"] \
            or not os.path.isfile(self.env["sl_slang_database_file"]):
            return


        self.__examples_capacity = 5 

        self.__conn = sqlite3.connect(self.env["sl_slang_database_file"])
        self.__cursor = self.__conn.cursor()

        self.__find_and_add_other_samples()

        self.__conn.commit()
        self.__conn.close()



    def __find_and_add_other_samples(self):

        card_item = self.env["card_item"]
        examples = card_item["examples"]
        for note in [card_item
            , examples[0]
            , examples[1]
            , examples[2]
            , examples[3]
            , examples[4] ]:

            if "term" not in note or not note["term"]:
                break

            self.__cursor.execute(self.env["sql_select_candidates"], {
                "term_pattern": "%{}%".format(note["term"]),
                "term": note["term"]
            })

            candidates = self.__cursor.fetchall()

            # for candidate in candidates:
            for i in range(0, len(candidates)):
                candidate_item = self.__to_item(candidates[i])

                if not re.match(self.env["regex_candidate_filter"].format(
                    term=note["term"]), candidate_item["term"]):
                    continue

                if note["term"] in candidate_item["term"]:
                    self.__add_example(candidate_item)
        


    def __to_item(self, db_out):
        # converts from db output to python dictionary
        #    0   n.note_id               976, 
        #    1   n.term,                 'term...', 
        #    2   n.term_note,            '', 
        #    3   n.term_audio_id,        1425,
        #    4   n.image_id,             1426, 
        #    5   n.definition,           'definition...', 
        #    6   n.definition_note,      '',
        #    7   n.definition_audio_id,  'NULL', 
        #    8   n.times_used,           0, 
        #    9   d.file_name             'file_name.apkg'
        item = {}
        item["note_id"] = db_out[0]
        item["term"] = db_out[1]
        item["term_note"] = self.env["words_db_note_template"].format(
            db_out[9], db_out[1])
        item["term_audio_id"] = db_out[3]
        item["image_id"] = db_out[4]
        item["definition"] = db_out[5]
        item["definition_note"] = self.env["words_db_note_template"].format(
            db_out[9], db_out[6])
        item["definition_audio_id"] = db_out[7]
        item["file_name"] = db_out[9]

        return item



    def __add_example(self, new_example):

        if not new_example["term"] or not new_example["definition"]:
            return

        note = None
        examples = self.env["card_item"]["examples"]
        for example in examples:
            if "term" not in example or not example["term"]:
                note = example
                break

        if not note:
            return

        deque_name = new_example["file_name"].replace('.', '_')

        note["term"] = new_example["term"]
        note["term_note"] = new_example["term_note"]
        note["term_audio"] = self.__get_media(
            "audio", new_example["term_audio_id"], deque_name)
        note["image"] = self.__get_media(
            "image", new_example["image_id"], deque_name)
        note["definition"] = new_example["definition"]
        note["definition_note"] = new_example["definition_note"]
        note["definition_audio"] = self.__get_media(
            "audio", new_example["definition_audio_id"], deque_name)

        self.__cursor.execute(
            self.env["sql_update_note_use_counter"].format(
                note_id=new_example["note_id"]))



    def __get_media(self, media_type, media_id, deque_name):
        if not media_id or media_id == 'NULL':
            return ""

        new_file_name = "{}\\{}\\{}_{}".format(
            self.env["prj_media_dir"], media_type, deque_name, media_id)

        self.__cursor.execute(
            self.env["sql_write_media_data"].format(media_id=media_id))
        data = self.__cursor.fetchall()

        with open(new_file_name, 'wb') as file:
            file.write(data[0][0])

            return os.path.relpath(new_file_name).replace('\\','/')

        return ""


