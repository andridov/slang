# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re
import wx

from plugin_Base import PluginBase


class WordsCounter(PluginBase):
    def __init__(self, env, name, plugin_path):
        # set logging=True if you need extra-logging
        self.logging = False
        
        if self.logging == False and "logger" in env:
            self.logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, plugin_path=plugin_path)

        if self.logging == False and self.logger:
            env["logger"] = self.logger


    def process(self, **kwargs):
        mandatory_arguments = ["source_text", "prompt_edit", "text_edit"]
        for arg in mandatory_arguments:
            if arg not in kwargs:
                self.logger.error("WordsCounter, argument missing: {}".format(
                    arg))
                return False

        return self.__check(kwargs["source_text"]
            , kwargs["prompt_edit"]
            , kwargs["text_edit"])


    def __check(self, source_text, prompt_edit, text_edit):
        entered_text = text_edit.GetValue()
        source_words = source_text.split()

        if not entered_text:
            self.__show_result(prompt_edit, len(source_words), 0, 0, 0)
            return False

        if entered_text == source_text:
            return True

        entered_words = entered_text.split()

        correct = 0
        known = 0
        incorrect = 0
        i = 0

        count = min(len(entered_words), len(source_words))
        while i < count:
            if entered_words[i] == source_words [i]:
                correct += 1
                i += 1
                continue

            if entered_words[i] in source_words:
                known += 1
                i += 1
                continue

            incorrect += 1
            i += 1 

        self.__show_result(prompt_edit
            , len(source_words) - len(entered_words)
            , correct, known, incorrect)

        return False

        

    def __show_result(self, prompt_ctrl, left, correct, known, incorrect):
        prompt_ctrl.SetValue(self.env["counter_template"].format(
            left=left, correct=correct, known=known, incorrect=incorrect))
        prompt_ctrl.SetStyle(  1,  2, wx.TextAttr(wx.BLACK))
        prompt_ctrl.SetStyle(  6,  8, wx.TextAttr(wx.GREEN))
        prompt_ctrl.SetStyle( 11, 13, wx.TextAttr(wx.BLUE))
        prompt_ctrl.SetStyle( 16, 18, wx.TextAttr(wx.RED))


