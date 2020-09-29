
import os
import io
import urllib.parse
import urllib.request
import requests
import wx


from plugin_Base import PluginBase
from sl_pluginLoader import PluginLoader

class GatherCardItemMediaData(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

    def process(self, **kwargs):
        tab_ids_list = self.env["tab_ids_list"]
        card_item = self.env["card_item"]

        update_items_list = [ 
            card_item
            , card_item["examples"][0]
            , card_item["examples"][1]
            , card_item["examples"][2]
            , card_item["examples"][3]
            , card_item["examples"][4]
        ] 
        
        length = len(update_items_list)
        for i in range(length):
            self.__attach_images(tab_ids_list[i], update_items_list[i])
            if i == 0 or self.env['save_examples_audio'] == True:
                self.__attach_audios(tab_ids_list[i], update_items_list[i])



    def __url_encode(self, name):
        return urllib.parse.quote(name.replace('/','\\'))



    def __attach_images(self, tab_from, item_to):
        media_data_mapping = self.env["media_data_mapping"]

        img_url_text = getattr(
            tab_from, media_data_mapping["image_url_obj"]).GetValue()

        if not img_url_text:
            return

        if os.path.isfile(img_url_text):
            item_to["image"] = img_url_text
            return

        orig_bitmap = getattr(tab_from, media_data_mapping["bitmap_obj"])
        image_size_txt = getattr(
            tab_from, media_data_mapping["image_size_obj"]).GetValue()
        bitmap = tab_from.bitmap_resize(orig_bitmap, image_size_txt)
        suffix = tab_from.caption
        full_file_name = "{}/{}_{}.jpg".format(
            self.env["prj_image_dir"]
            , self.__url_encode(self.env["card_item_term"])[0:50]
            , suffix.replace(' ', '_'))

        rel_file_name = os.path.relpath(full_file_name).replace('\\','/')
        
        bitmap.SaveFile(rel_file_name, wx.BITMAP_TYPE_JPEG)
        item_to["image"] = rel_file_name

        

    def __attach_audios(self, tab_from, item_to):
        mdm = self.env["media_data_mapping"]
        self.__attach_audio(
            item_to
            , "term"
            , "term_audio"
            , getattr(tab_from, mdm["term_audio_obj"]).GetValue()
            , "{}_{}".format(tab_from.caption, "term"))
        
        if not self.env["save_definition_audio"]:
            item_to["definition_audio"] = ""
            return

        self.__attach_audio(
            item_to
            , "definition"
            , "definition_audio"
            , getattr(tab_from, mdm["definition_audio_obj"]).GetValue()
            , "{}_{}".format(tab_from.caption, "def"))



    def __attach_audio(self
        , item_to
        , text_fld_caption
        , audio_fld_caption
        , audio_file
        , suffix):

        media_data_mapping = self.env["media_data_mapping"]

        if audio_file and os.path.isfile(audio_file):
            item_to[audio_fld_caption] = audio_file
            return

        if not text_fld_caption in item_to or not item_to[text_fld_caption]:
            item_to[audio_fld_caption] = ""
            return

        # saving to file take place here

        # creating full file name
        full_file_name = "{}/{}_{}.mp3".format(
            self.env["prj_audio_dir"]
            , self.__url_encode(item_to[text_fld_caption])[0:50]
            , suffix.replace(' ', '_'))
        rel_file_name = os.path.relpath(full_file_name).replace('\\','/')
        

        if audio_file == "file-snipping" \
            and "video_audio_file" in self.env \
            and os.path.isfile(self.env["video_audio_file"]):

            self.__get_audio_from_file(rel_file_name)
            item_to[audio_fld_caption] = rel_file_name
            return



        # using default audio engine here
        url=""
        if  text_fld_caption=="term":
            url = self.env["term_audio_engine"].format(
                item_to[text_fld_caption])
        elif text_fld_caption == "definition" \
            and self.env["save_definition_audio"] == True:
            url = self.env["definition_audio_engine"].format(
                item_to[text_fld_caption])

        if not url:
            item_to[audio_fld_caption] = ""
            return

        r = requests.get(url, allow_redirects=True)
        with io.open(rel_file_name, 'wb') as f:
            f.write(r.content)

        item_to[audio_fld_caption] = rel_file_name



    def __get_audio_from_file(self, rel_file_name):
        self.env["out_audio_file_name"] = rel_file_name
        PluginLoader(self.env, "SaveAudioFromFile").process()


