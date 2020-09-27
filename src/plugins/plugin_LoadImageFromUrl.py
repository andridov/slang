import re
import sys
import traceback
import urllib.parse
import urllib.request

from plugin_Base import PluginBase




class LoadImageFromUrl(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        


    def process(self, param_map=None):
        self.env["plugin_load_image_status"] = self.__load_image_from_url()



    def __load_image_from_url(self):

        self.__url = self.env["plugin_image_url"]
        self.__dst_image_file = self.env["plugin_dst_image_file"]

        if not self.__url:
            return False

        for reg_pattern in self.env["url_regex_patterns_list"]:
            re_result = re.match(self.env[reg_pattern], self.__url)
            if re_result:
                return self.__try_urlretrieve(re_result.group(1))

        return False



    def __try_urlretrieve(self, url):
        try:
            url = self.__url_decode(url)

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

        
