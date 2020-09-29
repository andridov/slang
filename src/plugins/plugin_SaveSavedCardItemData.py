import io
import os
import glob
import json
import time
from datetime import datetime

from plugin_Base import PluginBase

class SaveSavedCardItemData(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        self.__append_saved_cards()
        self.__save_current_card_items_list()



    def __append_saved_cards(self):
        if 'card_items_list' not in  self.env:
            self.env["card_items_list"] = []

        for full_file_name in glob.iglob(self.env["saved_card_item_template"]):
            with open(full_file_name, encoding="utf8") as f:
                data = json.load(f)
                if self.__is_missing_in_card_items(data):
                    self.env["card_items_list"].append(data)



    def __save_current_card_items_list(self):
        
        if len(self.env["card_items_list"]) == 0:
            return

        current_month_archive_dir = "{}/{}_{:02d}".format(
            self.env["prj_saved_arch_dir"]
            , datetime.now().year
            , datetime.now().month)

        if not os.path.exists(current_month_archive_dir):
            os.mkdir(current_month_archive_dir)

        full_file_name = "{}//cardItems_{}_{}.json".format(
            current_month_archive_dir
            , round(time.time() * 1000)
            , len(self.env["card_items_list"]))

        with io.open(full_file_name, 'w', encoding='utf8') as f:
            f.write(json.dumps(self.env["card_items_list"]
                , indent=2, ensure_ascii=False, sort_keys=False))



    def __is_missing_in_card_items(self, data):
        if not "term" in data:
            return False

        term = data["term"]
        card_items_list = self.env["card_items_list"]
        for card_item in card_items_list:
            if term == card_item["term"]:
                return False

        return True
