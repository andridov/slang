# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re
import sys
import traceback
import urllib.parse
import urllib.request

from sl_env import Env
from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase




class LoadImageFromUrl(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)
        


    def process(self, **kwargs):
        if "url" not in kwargs:
            self.logger.error("Url expected in ImageUrlProcess.process method")
            return False
        self.__url = kwargs["url"]

        self.__dst_image_file = ""
        if "dst_file" not in kwargs:
            self.__dst_image_file = self.env["prj_temp_dir"] + "/temp_img_file"
        else:
            self.__dst_image_file = kwargs["dst_file"]

        try:
            
            return self.__load_image_from_url()
        
        except Exception as e:
            self.logger.error(
                "LoadImageFromUrl, exception error: {}".format(e))
            self.logger.error(traceback.format_exc())
        except:
            self.logger.error("LoadImageFromUrl, Unexpected error")
            self.logger.error(traceback.format_exc())



    def __load_image_from_url(self):

        if not self.__url:
            return False

        for pattern in self.env["url_regex_handlers_list"]:
            re_result = re.match(pattern["regex"], self.__url)
            if re_result:
                return getattr(self, pattern["handler"])(re_result)

        return False



    # handlers
    def handler_empty_string(self, re_match):
        return True



    def handler_youglish(self, re_match):
        return PluginLoader(self.env, "YouglishLoad").process(url=self.__url)



    def hander_google_search(self, re_match):
        encoded_url = urllib.parse.unquote(self.__url)
        img_re = self.env["google_search_url_regex"]

        self.logger.debug(encoded_url)

        m = re.search(img_re, encoded_url)
        if not m:
            self.logger.warning("can't parse google imgres: {}".format(url))
            return False

        if m.group(1):
            self.__url = m.group(1)
            return self.__try_urlretrieve()

        return False



    def hander_link_location(self, re_match):
        return self.__try_urlretrieve()



    def __try_urlretrieve(self):
        try:
            url = self.__url_decode(self.__url)

            self.logger.info("loading image from url={}".format(url))

            # Adding information about user agent
            opener=urllib.request.build_opener()
            opener.addheaders=[("User-Agent",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                + "(KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36")]
            urllib.request.install_opener(opener)

            urllib.request.urlretrieve(url, self.__dst_image_file)
            return True

        except Exception as e:
            self.logger.error(
                "__try_urlretrieve; {}\n {} ".format(e, sys.exc_info()))

        except:
            self.logger.error(
                "__try_urlretrieve; Unexpected error\n{}".format(
                    sys.exc_info()))

        return False



    def __url_decode(self, url):
        re_result = re.match(self.env["encoded_image_pattern"], url)
        if re_result:
            return urllib.parse.unquote(url)

        return url

        
