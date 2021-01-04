import json
import json

from plugin_Base import PluginBase

class SaveEnv(PluginBase):
    def __init__(self, env, name, **kwargs):
        
        self.logging = False
        self.__logger = None
        if self.logging == False and "logger" in env:
            self.__logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, **kwargs)
        
        if self.logging == False and self.__logger:
            env["logger"] = self.__logger
            self.logger = self.__logger


    def process(self, **kwargs):

        if not "file" in kwargs:
            self.logger.error("SaveEnv: file not set")
        dst_file = kwargs["file"]

        if not "dst_env" in kwargs:
            self.logger.error(
                "SaveEnv: 'env' not set for file:".fromat(dst_file))
        dst_env = self.__prepare_env_to_save(kwargs["dst_env"])

        with open(dst_file, 'w') as jf:
            json.dump(dst_env, jf
                , indent=self.env["indent_spaces_count"]
                , ensure_ascii=False
                , sort_keys=False)


    def __prepare_env_to_save(self, src_env):

        if "__export_list" in src_env:
            del src_env['__export_list']

        dst_env = [ {"--": "--"} ]

        for k, v in src_env.items():
            dst_env.append({k: v})

        dst_env.append({"--": "--"})
        return dst_env