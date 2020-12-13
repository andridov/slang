# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import re
import sys


class SubTitleItem:
    def __init__(self, time_start_arr, time_end_arr, text):

        self.time_start = self.__to_ms(time_start_arr) 
        self.time_end = self.__to_ms(time_end_arr)

        self.text = text


    def __to_ms(self, arr):
        return \
            int(arr[0]) * 60 * 60 * 1000 \
            +int(arr[1]) * 60 * 1000 \
            +int(arr[2]) * 1000 \
            +int(arr[3])


    def to_str(self, time_ms):
        h = time_ms // 3600000
        time = time_ms - h * 3600000
        m = time // 60000
        time = time - m * 60000
        s = time // 1000
        ms  =  time - s * 1000
        
        return "{}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)



class SubTitle:
    def __init__(self, env, subt_file_env_name):
        if subt_file_env_name not in env:
            raise SlProgramStatus("error"
                , "There is no such environment variable '{}'".format(
                    subt_file_env_name))

        if not os.path.isfile(env[subt_file_env_name]):
            raise SlProgramStatus("error", "Sbtitle file '{}' not found".format(
                env["subt_file_env_name"]))

        self.env = env
        self.__env_file_name = subt_file_env_name
        self.__file_name = env[subt_file_env_name]
        self.__delay_ms = 0
        self.__subtitles = []

        self.__load_from_file(self.__file_name)




    def __load_from_file(self, subt_file):
        self.__file_name = subt_file

        pattern = re.compile(self.env["video_subtitle_regex_pattern"]
            , flags=re.MULTILINE)

        data = open(self.__file_name, encoding='utf-8').read()

        match_iter = pattern.findall(data)
        for m in match_iter:
            sti = SubTitleItem([m[0], m[1], m[2], m[3]]
                , [m[4], m[5], m[6], m[7]], m[8])
            self.__subtitles.append(sti)


    def reload_file(self, subt_file):
        self.__load_from_file(subt_file)

        if not self.__env_file_name:
            self.logger.warning("the environment variable '__env_file_name'"\
                " is missed. subtitle file will not be saved!!!")
            return
        env[self.__env_file_name] = subt_file



    def get_full_file_name(self):
        return self.__file_name



    def get_shift_value(self):
        return self.__delay_ms



    def get_text(self, current_time):
        time = current_time + self.__delay_ms
        return self.__get_text(time)



    def get_from_to(self, time):
        item = self.__find_item(time)
        if not item:
            return None

        start = item.time_start - 2000
        end = item.time_end + 2000
        return (item.to_str(start), item.to_str(end))



    def __get_text(self, time):
        item = self.__find_item(time)
        return item.text if item else ""



    def __find_item(self, time):
        for item in self.__subtitles:
            if time < item.time_start:
                return None

            if time > item.time_start and time < item.time_end:
                return item

        return None
