import os
import glob
import shutil

from plugin_Base import PluginBase
from sl_exceptions import SlProgramStatus

class CreateNewProject(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        

    def process(self, param_map=None):

        if os.path.exists(self.env["prj_dir"]):
            self.logger.info("Project already exists, project_name = {}".format(
                self.env["sl_project_name"]))

            raise SlProgramStatus("New project creating error",
                "flag '--create-project' was used, but project already exists")


        self.logger.info("Creating new project, project_name = {}".format(
            self.env["sl_project_name"]))

        # creating some directories, needed for this step
        for dir_key in self.env["list_of_directories_to_create"]:
            directory = self.env[dir_key]
            if not os.path.isdir(directory):
                self.logger.info("creating dir: {}".format(directory))
                os.makedirs(directory)

        # copy files, needed for new project
        for src_id, dst_id in self.env["list_of_files_to_copy"].items():
            src = self.env[src_id]
            dst = self.env[dst_id]
            for full_file_name in glob.glob(src):
                self.logger.info("copying file {} --> {} ".format(
                        full_file_name, dst))
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, dst)


            