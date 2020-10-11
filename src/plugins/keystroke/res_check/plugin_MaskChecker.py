import re
import wx

from plugin_Base import PluginBase


class MaskChecker(PluginBase):
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
                self.logger.error("MaskChecker, argument missing: {}".format(
                    arg))
                return False
        masked_text = self.__to_mask(kwargs["source_text"])

        prompt_edit = kwargs["prompt_edit"]
        if masked_text != prompt_edit.GetValue():
            prompt_edit.SetValue(masked_text)

        return self.__check_results(masked_text, kwargs["text_edit"])



    def __to_mask(self, text):
        text = re.sub(self.env["regex_uppercase"]
            , self.env["mask_uppercase"], text)
        text = re.sub(self.env["regex_lowercase"]
            , self.env["mask_lowercase"], text)
        return text


    def __check_results(self, masked_text, text_edit):

        entered_text = text_edit.GetValue()
        if not entered_text:
            return False

        mask = self.__to_mask(entered_text)
 
        exact_match = True
        lmt = len(masked_text)
        for i in range(len(mask)):
            if i >= lmt:
                text_edit.SetStyle(i, i+1, wx.TextAttr(wx.RED))
                exact_match = False
                continue

            if mask[i] == masked_text[i]:
                text_edit.SetStyle(i, i+1, wx.TextAttr(wx.BLACK))
            else:
                text_edit.SetStyle(i, i+1, wx.TextAttr(wx.RED))
                exact_match = False

        if lmt == len(mask) and exact_match:
            return True

        return False