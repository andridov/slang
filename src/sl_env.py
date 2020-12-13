# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import json
import re


from sl_logger import Logger


import traceback


class Env(dict):
    def __init__(self, parent_env=None):
        if parent_env:
            self.update(parent_env)
        self.__parent_env = parent_env

        self["__export_list"] = []
        self.current_env_file = ''
        self.__loaded_env_files = set()

        self.__logger = None
        if 'logger' in self:
            self.__logger = self["logger"]



    def __del__(self):
        self.populate_parent_env()



    def append_env(self, env_file):

        current_env_file = os.path.abspath(env_file)
        if current_env_file in self.__loaded_env_files:
            return

        if self.__logger:
            self.__logger.info(
                "loading env, file: {}".format(current_env_file))

        self.current_env_file = current_env_file
        self.__loaded_env_files.add(current_env_file)
        with open(current_env_file, encoding="utf8") as f:
            json_env = json.load(f)
            self.__parse_and_add(json_env)



    def get_env_obj(self):
        return Env(self)


    def populate_parent_env(self):
        if not "__export_list" in self or len(self["__export_list"]) == 0 :
            return

        if not self.__parent_env:
            raise Exception("Parent envirionment does not exist. "\
                "Can't export variables: {}".format(self["__export_list"]))

        for export_item_name in self["__export_list"]:
            self.__parent_env[export_item_name] = self[export_item_name]




    def print_env(self):
        if not self.__logger and "logger" in self:
            self.__logger = self["logger"]

        if self.__logger:
            for k, v in sorted(self.items()):
                self.__logger.info("\t{} : {}".format(k, v))
        else:
            for k, v in sorted(self.items()):
                print("\t{} : {}".format(k, v))



    def __parse_and_add(self, json_env):
        kvp = KeyValueParser(self)
        for m in json_env:
            for k, v in m.items():
                kvp.parse(k, v)




class KVH:
    def __init__(self, key_regex, value_regex, handler_name):
        self.k = re.compile(key_regex)
        self.v = re.compile(value_regex)
        self.handler = handler_name



    def match(self, key, value):
        m = re.match(self.k, key)
        if not m:
            return False
        self.key_match_result = m

        m = re.match(self.v, value)
        if not m:
            return False
        self.value_match_result = m

        return True




class KeyValueParser:
    def __init__(self, dict):
        self.dict = dict
        self.__set_handlers()



    class ProcessStatus:
        EXIT = -1
        CONTINUE = 0



    def __set_handlers(self):
        self.handlers_list =[
            #   KEY_regex,     VALUE_regex,        HANDLER_name
            KVH(r"--",         r".+",              'handle_comment'),
            KVH(r"__import",   r".+",              'handle_import_value'),
            KVH(r"__export",   r".+",              'handle_export_value'),
            KVH(r".+",      r"(.*)\$\(([^\)]+)\)(.*)", 'handle_value_substitution'),
            KVH(r".+_dir",     r".+",              'handle_absolute_directory'),
            KVH(r"__include",  r".+",              'handle_include_env'),
            KVH(r".*",         r".+",              'handle_key_value')
        ]



    def parse(self, k, v):
        if not isinstance(v, str):
            self.dict[k] = v
            return

        for kvh in self.handlers_list:
            if kvh.match(k, v):
                result = getattr(self, kvh.handler)(kvh, k, v)
                if result == self.ProcessStatus.EXIT:
                    return
                # some transformation could happen with value, so update it
                v = self.dict[k]



    # --------------------------------------------------------------------------
    # handlers 

    def handle_comment(self, kvh, k, v):
        # skip all comments
        return self.ProcessStatus.EXIT


    def handle_import_value(self, kvh, k, v):
        if v in self.dict:
            return self.ProcessStatus.EXIT
        raise Exception("Variable '{}' expected before loading '{}'".format(
            v, self.dict.current_env_file))


    def handle_export_value(self, kvh, k, v):
        # each __export value will be stored into the __export_list array.
        # At the moment before destruction object all variables named in 
        # __export_list will be moved to parent environment. Existing variables
        # will be overrided.
        if '__export_list' not in self.dict:
            self.dict["__export_list"] = []
        self.dict["__export_list"].append(v)
        return self.ProcessStatus.EXIT


    def handle_value_substitution(self, kvh, k, v):
        match = kvh.value_match_result
        v = match.group(1) + self.dict[match.group(2)] + match.group(3)
        self.dict[k] = v
        # repeat foreach substitution
        if kvh.match(k, v):
            self.handle_value_substitution(kvh, k, v)
        return self.ProcessStatus.CONTINUE


    def handle_absolute_directory(self, kvh, k, v):
        self.dict[k] = os.path.realpath(v)
        return self.ProcessStatus.CONTINUE


    def handle_include_env(self, kvh, k, v):
        file = v
        if v[0] == '.':
            current_env_dir = os.path.dirname(self.dict.current_env_file)
            file = current_env_dir + v[1:]

        self.dict.append_env(file)
        return self.ProcessStatus.EXIT


    def handle_key_value(self, kvh, k, v):
        self.dict[k] = v
        return self.ProcessStatus.CONTINUE

