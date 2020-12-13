# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import wx

from plugin_Base import PluginBase

class ImageResize(PluginBase):
    def __init__(self, env, name, **kwargs):
        
        self.logging = False
        self.__logger = None
        if self.logging == False and "logger" in env:
            self.__logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, **kwargs)
        
        if self.logging == False and self.__logger:
            env["logger"] = self.__logger



    def process(self, **kwargs):
        return self.__image_resize(**kwargs)



    def __image_resize(self, **kwargs):

        w, h = kwargs["image_size"]

        bitmap_in = kwargs["original_bitmap"]
        bw, bh = bitmap_in.GetSize()

        rw = w/bw
        rh = h/bh
        r = rw if rw < rh else rh

        image = bitmap_in.ConvertToImage()
        image = image.Scale(bw*r, bh*r, wx.IMAGE_QUALITY_HIGH)

        return wx.Bitmap(image)

