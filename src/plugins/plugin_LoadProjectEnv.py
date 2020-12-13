# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import os
import glob
import json

from plugin_Base import PluginBase
from sl_exceptions import SlProgramStatus

class LoadProjectEnv(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        if not os.path.exists(self.env["prj_dir"]):
            raise SlProgramStatus("Error",
                "project dir '{}' does not exists".format(self.env["prj_dir"]))

        # create all directories, if needed
        directory_keys = self.env["check_dir_list"]
        for dk in directory_keys:
            d = self.env[dk]
            if not os.path.isdir(d):
                self.logger.info("creating folder: {}".format(d))
                os.makedirs(d)

        self.__load_created_cards()


    # add pervious results to saved data...
    # prj_saved_dir

    def __load_created_cards(self):
        if 'card_items_list' not in  self.env:
            self.env["card_items_list"] = []

        # load single items from file
        for full_file_name in glob.iglob(self.env["saved_card_item_template"]):
            with open(full_file_name, encoding="utf8") as f:
                data = json.load(f)
                self.env["card_items_list"].append(data)
                self.logger.info("added previously saved card: {}".format(
                    data["term"]))

        # load list of items from file
        for file in glob.iglob(self.env["saved_card_item_list_template"]):
            with open(file, encoding="utf8") as f:
                data_list = json.load(f)
                for data in data_list:
                    self.env["card_items_list"].append(data)
                    self.logger.info("added previously saved card: {}".format(
                        data["term"]))
        


