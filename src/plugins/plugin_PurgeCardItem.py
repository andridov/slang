
from plugin_Base import PluginBase

class PurgeCardItem(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)


    def process(self, param_map=None):
        examples = self.env["card_item"]["examples"]
        examples = [x for x in examples if self.__item_not_empty(x)]
        self.env["card_item"]["examples"] = examples


    def __item_not_empty(self, data):
        for f in self.env["item_fields"]:
            if data[f]:
                return True
        return False
