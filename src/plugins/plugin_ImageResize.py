import wx

from plugin_Base import PluginBase

class ImageResize(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        

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

