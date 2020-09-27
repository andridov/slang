import io
import json
import re
import sqlite3
import time

from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader

class AnkiDBDataRead(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)

        self.__cards = []

        # it's needed to assign correct path to plugin.env.json files
        self.env["sl_cfg_plugin_dir"] = \
            "{}/..".format(self.env["sl_cfg_plugin_dir"])
        

    def process(self, param_map=None):
        self.__read_anki_media_mapping()
        self.__read_anki_database()
        self.__save_card_items()



    def __read_anki_media_mapping(self):
        with open(self.env["anki_media_mapping_file"], encoding="utf8") as f:
            self.env["media_mapping"] = json.load(f)



    def __save_card_items(self):
        if not len(self.__cards): 
            self.logger.warning("Cards container is empty. Nothing to save.")
            return

        self.logger.info(
            "Saving items to {}".format(self.env["card_items_file"]))

        with io.open(self.env["card_items_file"], 'w', encoding='utf8') as f:
            f.write(json.dumps(self.__cards
                , indent=2, ensure_ascii=False, sort_keys=False))



    def __read_anki_database(self):
        anki_database_file = self.env["anki_database_file"]
        self.logger.info("Reading anki database {}".format(anki_database_file))
        con = sqlite3.connect(anki_database_file)
        cur = con.cursor()

        for row in cur.execute(self.env["sql_read_notes"]):
            card_item = self.__deserialize_flds(row[0], row[1], row[2])
            if card_item:
                self.__cards.append(card_item)



    def __deserialize_flds(self, flds, creation_time, mod_time):
        def time_value(t):
            value = int(t)
            now_time = time.time()
            # must be in milliseconds. not epoch 
            #perfom adjustement to epoch format here
            if value > now_time:
                value = value / 1000
            return value

        if not flds:
            return None

        fields = flds.split("\x1f")

        card_item = {}
        examples = [{},{},{},{},{}]
        notes = [card_item
            , examples[0]
            , examples[1]
            , examples[2]
            , examples[3]
            , examples[4] ]

        i = 0
        for itm in notes:
            itm["term"] = fields[i]
            i += 1
            itm["term_note"] = fields[i]
            i += 1
            itm["term_audio"] = self.__get_sound_name(fields[i])
            i += 1
            itm["image"] = self.__get_image_name(fields[i])
            i += 1
            itm["definition"] = fields[i]
            i += 1
            itm["definition_note"] = self.__get_sound_name(fields[i])
            i += 1
            itm["definition_audio"] = fields[i]
            i += 1
            #adding ids and timestamps


            itm["creation_time"]  = time_value(creation_time)
            itm["mod_time"] = time_value(mod_time)

        card_item["examples"] = examples

        self.env["card_item"] = card_item
        PluginLoader(self.env, "PurgeCardItem").process()

        return card_item



    def __get_image_name(self, text):
        return self.__get_media_file(self.env["regex_image"], text)

    def __get_sound_name(self, text):
        return self.__get_media_file(self.env["regex_sound"], text)



    def __get_media_file(self, regex_template, text):
        m = re.match(regex_template, text)
        if not m:
            return ""

        file_name = m.group(1)
        for key,value in self.env["media_mapping"].items():
            if value == file_name:
                return "{}/{}".format(self.env["prj_anki_upkg_dir"], key)

        self.logger.warning(
            "Resourse file='{}' is not found in media_mapping".format(
                file_name))
        return ""


        
