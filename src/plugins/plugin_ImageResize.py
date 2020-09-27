import wx

from plugin_Base import PluginBase

class ImageResize(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        

    def process(self, params):
        self.__image_resize(params)


    def __image_resize(self, params):

        w, h = params["image_size"] 

        bitmap_in = params["original_bitmap"]
        bw, bh = bitmap_in.GetSize()

        rw = w/bw
        rh = h/bh
        r = rw if rw < rh else rh

        image = bitmap_in.ConvertToImage()
        image = image.Scale(bw*r, bh*r, wx.IMAGE_QUALITY_HIGH)
        params["out_bitmap"] = wx.Bitmap(image)

