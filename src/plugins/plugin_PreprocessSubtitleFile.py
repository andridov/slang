import os
import re
import json

from plugin_Base import PluginBase

class PreprocessSubtitleFile(PluginBase):
    def __init__(self, env, name, **kwargs):
        
        self.logging = False
        self.__logger = None
        if self.logging == False and "logger" in env:
            self.__logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, **kwargs)
        
        if self.logging == False and self.__logger:
            env["logger"] = self.__logger
            self.logger = self.__logger



    def process(self, **kwargs):

        if "subt_file" not  in kwargs \
            or not os.path.isfile(kwargs["subt_file"]):
            return

        self.__compile_regex()

        subt_file = kwargs["subt_file"]
        self.logger.info(subt_file)
        with open(subt_file, 'r', encoding="utf8") as sf:
              subts = self.__preprocess_subtitle(sf.read())
        if subts:
            with open(subt_file, 'w', encoding="utf8") as sf:
                sf.write(subts)



    def __compile_regex(self):
        self.__item_pattern = re.compile(self.env["subt_item_regex"])
        self.__open_tag_pattern = re.compile(self.env["open_tag_regex"])



    def __preprocess_subtitle(self, subt_str):
        dst_str = ""

        for (number, tf, tt, text) in re.findall(self.__item_pattern, subt_str):
            text = self.__process_subt_text(text)
            dst_str += "{}\n{} --> {}\n{}\n\n".format(number, tf, tt, text)

        return dst_str



    def __process_subt_text(self, text):
        m = re.match(self.__open_tag_pattern, text)
        while m:
            text = self.__remove_tag(m.group(1), text)
            m = re.match(self.__open_tag_pattern, text)

        return text



    def __remove_tag(self, tag_name, text):
        rt = self.env["named_tag_content_regex"].format(tag_name=tag_name)
        named_tag_content_pattern = re.compile(rt)

        m = re.match(named_tag_content_pattern, text)
        if m:
            text = m.group(1) + m.group(2) + m.group(3)

        return text