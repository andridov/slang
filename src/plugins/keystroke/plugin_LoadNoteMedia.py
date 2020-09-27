import os

from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase

class LoadNoteMedia(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        

    def process(self, param_map=None):
        self.__load_media()


    def __load_media(self):
        def write_to_file(data, file_name):
            if data:
                with open(file_name, 'wb') as file:
                    file.write(data)
                    return
            if os.path.isfile(file_name):
                os.remove(file_name)


        sql_query_item = {}
        sql_query_item["query"] = self.env["sql_select_note_media"]
        sql_query_item["data"] = ( self.env["current_note_id"], )
        self.env["sql_queries_list"] = [ sql_query_item ]
        PluginLoader(self.env, "KeystrokeUpdateDb").process()

        for row in self.env["sql_query_results_list"][0]:
            write_to_file(row[0], self.env["image_blob_file"])
            write_to_file(row[1], self.env["term_audio_blob_file"])
            write_to_file(row[2], self.env["definigion_audio_blob_file"])