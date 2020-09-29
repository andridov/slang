import io
import json
import time
import urllib.parse

from plugin_Base import PluginBase

class SaveCardItem(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)


    def process(self, **kwargs):
        self.__save_card()

        if 'card_items_list' not in  self.env:
            self.env["card_items_list"] = []

        self.env["card_items_list"].append(self.env["card_item"])


    def __save_card(self):
        full_file_name = "{}/card_{}_{}.json".format(
            self.env["prj_saved_dir"]
            , round(time.time() * 1000)
            , urllib.parse.quote(
                self.env["card_item"]["term"].replace('/','\\'))[0:50])

        with io.open(full_file_name, 'w', encoding='utf8') as f:
            f.write(json.dumps(self.env["card_item"]
                , indent=2, ensure_ascii=False, sort_keys=False))

        self.logger.info("item saved to: {}".format(full_file_name))

