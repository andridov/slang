import json

from googletrans import Translator

from plugin_Base import PluginBase

class TranslateText(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        self.env["translate_text_definition"] = ""

        if not self.env["translate_text_term"]:
            return

        self.env["translate_text_definition"] = self.__text_translate(
            self.env["translate_text_term"])


    def __text_translate(self, term_text):
        translator = Translator()
        res = translator.translate(term_text
            , src=self.env["term_lang"], dest=self.env["definition_lang"])
        return res.text


        

