import requests
import urllib
import re
import os
import shutil
import subprocess


from sl_env import Env
from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase




class YouglishLoad(PluginBase):
    def __init__(self, env, name, **kwargs):
        self.logging = False
        self.__logger = None
        if self.logging == False and "logger" in env:
            self.__logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, **kwargs)
        
        if self.logging == False and self.__logger:
            env["logger"] = self.__logger
            self.env["logger"] = self.__logger
            self.logger = self.__logger

        self.env.print_env()

        self.__prepare()



    def process(self, **kwargs):
        if "url" not in kwargs:
            self.logger.error("YouglishLoad, url argument is absent")

        self.__url = kwargs["url"]

        self.__dst_image_file = ""
        if "dst_file" not in kwargs:
            self.__dst_image_file = \
                self.env["youglish_temp_dir"] + "/temp_img_file"
        else:
            self.__dst_image_file = kwargs["dst_file"]

        result = {}
        result["status"] = self.__process()
        if result["status"] == True:
            result["term_text"] = self.__term_text
            result["audio_file"] = self.__audio_file
            result["image_file"] = self.__image_file
            if self.__definition_text:
                result["definition_text"] = self.__definition_text

        return result


    def __prepare(self):
        self.__time_pattern = re.compile(self.env["subt_time_regex"])
        self.__middle_time = 0

        # create or clean temp/youglish folder
        tmp_dir = self.env["youglish_temp_dir"]
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        else:
            self.__delete_folder_content(tmp_dir)



    def __delete_folder_content(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def __run_command(self, run_file, cmd_name, **kwargs):
        command = PluginLoader(self.env, "CmdRun").process(
            run_file=run_file
            , cmd_name=cmd_name
            , get_command_only=True
            , **kwargs)

        output_str = ""
        p = subprocess.Popen(command,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        for line in p.stdout.readlines():
            output_str += line.decode("utf-8", 'ignore')

        return (retval, output_str.strip())



    def __process(self):
        self.logger.debug("YouglishLoad run")        

        r = requests.get(self.__url, allow_redirects=True)
        if not r:
            self.logger.info("null response received")
            return False

        data = r.text

        # text_file_name = "{}/response.txt".format(self.env["youglish_temp_dir"])
        # text_file = open(text_file_name, 'w', encoding="utf8")
        # text_file.write(data)
        # text_file.close()

        self.__searched_text = self.__get_searched_text(self.__url)
        term_text = self.__get_request_data(data, "src_text_regex", True)
        vid = self.__get_request_data(data, "src_vid_regex", True)

        # alternate way of downloading subtitles, video, audio
        PluginLoader(self.env, "CmdRun").process(
            run_file="youglish.env.json"
            , cmd_name="command_yt_subtitles_download", vid=vid)

        subt_file = self.__find_subt_file(vid, self.env["term_lang"])
        if not subt_file:
            raise Exception("Can't open subtitle file for language: {}".format(
                self.env["term_lang"]))

        PluginLoader(self.env, "PreprocessSubtitleFile").process(
            subt_file=subt_file)
        
        s_e_time = self.__find_s_e_time(subt_file, term_text)
        if not s_e_time:
            s_e_time = self.__find_s_e_time(subt_file, self.__searched_text)
        start_time, end_time = s_e_time
        
        response = self.__run_command(run_file="youglish.env.json"
            , cmd_name="command_yt_get_media_link", vid=vid)
                
        PluginLoader(self.env, "CmdRun").process(
            run_file="youglish.env.json"
            , cmd_name="command_ffmpeg_download_video"
            , vid=vid, media_link=response[1]
            , start=start_time, end=end_time)

        PluginLoader(self.env, "CmdRun").process(
            run_file="youglish.env.json"
            , cmd_name="command_extract_full_audio", vid=vid)
        
        PluginLoader(self.env, "CmdRun").process(
            run_file="youglish.env.json"
            , cmd_name="command_save_image_0", vid=vid)

        # result = PluginLoader(self.env, "CmdRun").process(
        #     run_file="youglish.env.json"
        #     , cmd_name="command_yt_media_download", vid=vid)

        # subt_file = self.__find_subt_file(vid, self.env["term_lang"])
        # if not subt_file:
        #     raise Exception("Can't open subtitle file for language: {}".format(
        #         self.env["term_lang"]))

        # PluginLoader(self.env, "PreprocessSubtitleFile").process(
        #     subt_file=subt_file)

        # s_e_time = self.__find_s_e_time(subt_file, term_text)
        # if not s_e_time:
        #     s_e_time = self.__find_s_e_time(subt_file, self.__searched_text)
        # start_time, end_time = s_e_time
        
        # # extract audio
        # result = PluginLoader(self.env, "CmdRun").process(
        #     run_file="youglish.env.json"
        #     , cmd_name="command_extract_audio"
        #     , vid=vid, start=start_time, end=end_time)

        # extract image
        # result = PluginLoader(self.env, "CmdRun").process(
        #     run_file="youglish.env.json"
        #     , cmd_name="command_save_image"
        #     , vid=vid, start=self.__to_str(self.__middle_time))


        self.__term_text = term_text
        self.__definition_text = self.__find_definition_text(vid)
        self.__audio_file = "{}/{}.mp3".format(
            self.env["youglish_temp_dir"], vid)
        self.__image_file = "{}/{}.jpg".format(
            self.env["youglish_temp_dir"], vid)

        return True


    def __get_searched_text(self, url):
        searched_text = None

        for url_text in re.findall(self.env["url_searched_text_regex"], url):
            searched_text = urllib.parse.unquote(url_text)
            break

        self.logger.info("the searched text is: '{}'".format(searched_text))

        return searched_text


    def __get_request_data(self, request_text, regex_idx, mandatory=False):
        re_pattern = re.compile(self.env[regex_idx], re.MULTILINE)
        matches = [m.groups() for m in re_pattern.finditer(request_text)]
        if not len(matches):
            self.logger.warning("no matches for {} in request_text".format(
                regex_idx))
            if mandatory:
                raise Exception("No matches for {}='{}' in request_text".format(
                    regex_idx, self.env[regex_idx]))

        return matches[0][0]


    def __find_subt_file(self, vid, lang):
        subt_file = None

        candidates = [lang] if lang not in self.env["subt_lang_mpapping"] \
            else self.env["subt_lang_mpapping"][lang]

        for subt_lang in candidates:
            subt_file = "{}/{}.{}.vtt".format(
                self.env["youglish_temp_dir"], vid, subt_lang)

            if os.path.isfile(subt_file):
                break

            subt_file = None

        return subt_file


    def __find_definition_text(self, vid):

        subt_file = self.__find_subt_file(vid, self.env["definition_lang"])
        if not subt_file:
            return None

        subts_str = None
        with open(subt_file, 'r', encoding="utf8") as sf:
            subt_str = sf.read()

        subt_pattern = re.compile(self.env["subt_item_regex"])
        for (ts, te, text) in re.findall(subt_pattern, subt_str):
            if self.__to_ms(ts) < self.__middle_time \
                and self.__to_ms(te) > self.__middle_time:
                return text

        return None


    def __find_s_e_time(self, subt_file, term_text):
        subts_str = None

        with open(subt_file, 'r', encoding="utf8") as sf:
            subt_str = sf.read()
        if not subt_str:
            self.logger.error("Can't read the file {}".format(subt_file))
            return None 

        subt_pattern = re.compile(self.env["subt_item_regex"])
        for (ts, te, text) in re.findall(subt_pattern, subt_str):
            text = self.__preprocess_subt_text(text)
            if term_text in text:
                tl = self.__to_ms(ts)
                tl = tl if tl < 2000 else tl - 2000
                tu = self.__to_ms(te) + 2000
                self.__middle_time = int((tl + tu) / 2)
                return (self.__to_str(tl), self.__to_str(tu))

        return None



    def __to_ms(self, time_str):
        for (h, m, s, ms) in re.findall(self.__time_pattern, time_str):
            return \
                int(h) * 60 * 60 * 1000 \
                +int(m) * 60 * 1000 \
                +int(s) * 1000 \
                +int(ms)

        return 0



    def __to_str(self, time_ms):
        h = time_ms // 3600000
        time = time_ms - h * 3600000
        m = time // 60000
        time = time - m * 60000
        s = time // 1000
        ms  =  time - s * 1000
        
        return "{}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)




    def __preprocess_subt_text(self, text):
        text = text.replace('\n', ' ')
        return re.sub(r'[ \t]+', ' ', text)
