import wx
import re

from fuzzywuzzy import fuzz
from plugin_Base import PluginBase


class MatchChecker(PluginBase):
    def __init__(self, env, name, plugin_path):
        # set logging=True if you need extra-logging
        self.logging = False
        self.__logger = None
        
        if self.logging == False and "logger" in env:
            self.__logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, plugin_path=plugin_path)

        if self.logging == False and self.__logger:
            env["logger"] = self.__logger


    def process(self, **kwargs):
        mandatory_arguments = ["source_text", "prompt_edit", "text_edit"]
        for arg in mandatory_arguments:
            if arg not in kwargs:
                self.logger.error("MatchChecker, argument missing: {}".format(
                    arg))
                return False

        return self.__check_results(kwargs["source_text"]
            , kwargs["prompt_edit"]
            , kwargs["text_edit"])



    def __check_results(self, source_text, prompt_ctrl, text_ctrl):
        entered_text = text_ctrl.GetValue()

        if entered_text and entered_text == source_text:
            return True

        value = fuzz.ratio(source_text, entered_text)

        prompt_ctrl.BeginTextColour(wx.Colour(2*(100 - value), 1.3 * value, 0))
        prompt_ctrl.SetValue(self.env["value_template"].format(value)
            + ", used symbols: [{}]".format(re.sub("[A-Za-z $]", "", source_text)))


        return False