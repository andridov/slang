import os
import shutil
import json
from zipfile import ZipFile

from plugin_Base import PluginBase



class AnkiCreateDataPackage(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):

        z = ZipFile(self.env["prj_anki_zip_file"], "w")
        # add sqlite file to archive
        z.write(self.env["prj_anki_db_file"], "collection.anki2")

        # and file `media` with json - all media files and id
        media_file = self.env["prj_anki_media_file"]
        if os.path.isfile(media_file):
            with open(media_file, encoding="utf8") as f:
                media = json.load(f)
        else:
            media = {}

        media_dir = self.env["prj_anki_media_dir"]
        for roots, dirs, files in os.walk(media_dir):
            for file in files:
                z.write(os.path.join(media_dir, file), file)
                media[file] = file

        with open(media_file, 'w') as mf:
            json.dump(media, mf, indent=2)
        z.write(media_file, "media")

        z.close()
