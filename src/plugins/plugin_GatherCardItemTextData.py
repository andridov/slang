
from plugin_Base import PluginBase

class GatherCardItemTextData(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)


    def process(self, param_map=None):
        tab_ids_list = self.env["tab_ids_list"]
        text_data_mapping = self.env["text_data_mapping"]
        card_item = self.env["card_item"]

        update_items_list = [card_item
            , card_item["examples"][0]
            , card_item["examples"][1]
            , card_item["examples"][2]
            , card_item["examples"][3]
            , card_item["examples"][4]
        ]

        length = len(update_items_list)
        for i in range(length):
            for k,v in text_data_mapping.items():
                update_items_list[i][k] = getattr(tab_ids_list[i], v).GetValue()

        self.env["card_item_term"] = card_item["term"]
        self.env["card_item_definition"] = card_item["definition"]



