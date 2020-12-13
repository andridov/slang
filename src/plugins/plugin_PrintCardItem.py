# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import json

from plugin_Base import PluginBase

class PrintCardItem(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        self.logger.info(json.dumps(
            self.env["card_item"]
            , indent=2, ensure_ascii=False, sort_keys=False).encode('utf8'))
