import json

from plugin_Base import PluginBase

class PrintCardItem(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        

    def process(self, param_map=None):
        self.logger.info(json.dumps(
            self.env["card_item"]
            , indent=2, ensure_ascii=False, sort_keys=False).encode('utf8'))
