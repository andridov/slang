import os

from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase

class LoadNoteMedia(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        self.__load_media()


    def __load_media(self):
        def write_to_file(data, file_name):
            if data:
                with open(file_name, 'wb') as file:
                    file.write(data)
                    return
            if os.path.isfile(file_name):
                os.remove(file_name)

        query_result = PluginLoader(self.env, self.env["sl_db_query"]).process(
            queries_list= [
                { "query" : self.env["sql_select_note_media"]
                    , "data" : ( self.env["current_note_id"], ) } ] )

        for row in query_result[0]:
            write_to_file(row[0], self.env["image_blob_file"])
            write_to_file(row[1], self.env["term_audio_blob_file"])
            write_to_file(row[2], self.env["definigion_audio_blob_file"])