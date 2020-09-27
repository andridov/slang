import os
import re
import sys
import glob
import shutil

from sl_exceptions import SlPluginStatus \
    , SlPluginEntryPointStatus \
    , SlProgramStatus

from plugin_Base import PluginBase

class WordsDbPrepare(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        


    def process(self, param_map=None):
        self.__create_project_params()
        self.__clean_objects()
        self.__create_objects()



    def __create_project_params(self):
        self.env["prj_anki_pkg_file_name"] = \
            os.path.basename(self.env["cmd_known_args"].input_file)
        if 'description' in self.env["cmd_known_args"]:
            self.env["prj_description_file"] =  \
                self.env["cmd_known_args"].description
        
        if 'language' not in self.env["cmd_known_args"]:
            raise SlProgramStatus("Command line argument error:",
                "flag '--language' is missing, syntax: --language en-en")
            

        m = re.match(self.env["regex_language"]
            , self.env["cmd_known_args"].language)

        if not m:
            raise SlProgramStatus("Command line argument error:",
                "flag '--language' incorrect value, syntax: --language en-en")

        self.env["prj_term_language"] = m.group(1)
        self.env["prj_definition_language"] = m.group(2)
        self.logger.info("term language {}, definition language {}".format(
            self.env["prj_term_language"]
            , self.env["prj_definition_language"]))



    def __clean_objects(self):
        self.logger.info("cleaning pervious objects...")

        for obj in self.env["list_of_objects_to_clean"]:
            curr_obj = self.env[obj]
            # delete directory:
            if os.path.isdir(curr_obj):
                try:
                    shutil.rmtree(curr_obj)
                except OSError as e:
                    raise SlProgramStatus("Program error",
                        "ErrInfo: {}, {}".format(e.filename, e.strerror))

            # deleting file:
            if os.path.isfile(curr_obj):
                os.remove(curr_obj)

            # it's a mask
            for file_path in glob.glob(curr_obj):
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path): 
                        shutil.rmtree(file_path)
                except OSError as e:
                    raise SlProgramStatus("Program error",
                        "ErrInfo: {}, {}".format(e.filename, e.strerror))
                except Exception as e:
                    raise SlProgramStatus("Program error",
                        "ErrInfo: {}".format(e))



    def __create_objects(self):
        self.logger.info("creating directory structure...")

        for obj in self.env["list_of_directories_to_create"]:
            curr_obj = self.env[obj]
            self.logger.info("creating {}".format(curr_obj))
            if not os.path.exists(curr_obj):
                os.makedirs(curr_obj)


