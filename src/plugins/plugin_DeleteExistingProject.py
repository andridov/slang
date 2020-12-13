# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os

from plugin_Base import PluginBase
from sl_exceptions import SlProgramStatus

class DeleteExistingProject(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        if not self.env["cmd_known_args"].delete_project:
            return

        project_dir = "{}/{}".format(
            self.env["sl_projects_dir"], self.env["sl_project_name"])

        if not os.path.exists(project_dir):
            raise SlProgramStatus("Program error",
                "Project does not exists, project_name = {}".format(
                    self.env["sl_project_name"]))

        self.logger.info("Deliting project, project_name = {}".format(
            self.env["sl_project_name"]))



        self.logger.info("Project deleted, project_name = {}".format(
            self.env["sl_project_name"]))
