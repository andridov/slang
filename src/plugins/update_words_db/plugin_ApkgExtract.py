from zipfile import ZipFile

from plugin_Base import PluginBase

class ApkgExtract(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        self.__extract_apkg_archieve()


    def __extract_apkg_archieve(self):
        if not "input_file" in self.env["cmd_known_args"]:
            self.logger.error("nothing to process, file name is absent")

        apkg_file = self.env["cmd_known_args"].input_file
        self.logger.info("extracting '{}' file to '{}'".format(
            apkg_file, self.env["prj_anki_upkg_dir"]))


        with ZipFile(apkg_file, 'r') as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(self.env["prj_anki_upkg_dir"])

        self.logger.info("extracting '{}', done.".format(apkg_file))




