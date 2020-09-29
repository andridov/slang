
from plugin_Base import PluginBase

class PurgeCardItem(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)


    def process(self, **kwargs):
        examples = self.env["card_item"]["examples"]
        examples = [x for x in examples if self.__item_not_empty(x)]
        self.env["card_item"]["examples"] = examples


    def __item_not_empty(self, data):
        for f in self.env["item_fields"]:
            if data[f]:
                return True
        return False
