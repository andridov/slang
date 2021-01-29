# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import pkg_resources


from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader



class CheckDependencies(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)



    def process(self, **kwargs):
        self.__process()



    def __process(self):
        for package in self.env["packages_list"]:
            if not self.__check_package(package):

                PluginLoader(self.env, "CmdRun").process(
                    run_file=self.env["cmd_install_package_file"]
                    , package_name=package)

                if not self.__check_package(package):
                    raise Exception(f"Can't find/install package: {package}")
            


    def __check_package(self, package_name):
        try:
            dist = pkg_resources.get_distribution(package_name)
            self.logger.info(f'{dist.key} ({dist.version}) is installed')
            return True

        except pkg_resources.DistributionNotFound:
            self.logger.info(f'{package_name} is NOT installed')
            return False