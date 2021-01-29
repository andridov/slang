# Slang. Study LANGuage project. Tests
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import argparse
import os
import sys
import traceback
import shutil

from sl_logger import Logger
from sl_env import Env
from sl_pepProcessor import PluginEntryPointProcessor
from sl_pluginLoader import PluginLoader


# these variables needed to initialize log and start to parse slang.eng.json
# other variables should be loaded via *.env.json files
K_LOG_FILE = "../logs/slang.log"

# start looking for base env.folder in project folder, than use default
K_SOLUTION_DIR = "./.."
K_ENV_CONFIG_DIR = "../data/config"




def do_argparse():
    parser = argparse.ArgumentParser(description='Study LANGuage command line')

    parser.add_argument('-project-name', metavar='n', type=str, required=False
        , help='the name of the project')

    parser.add_argument('--create-project'
        , dest='create_project', action='store_true'
        , help="create project, if it does not exist")

    parser.add_argument('--delete-project'
        , dest='delete_project', action='store_true'
        , help="DELETE(without additional prompt!!!) project, if it is exist")

    args, other_args = parser.parse_known_args(["-project-name", "test"])

    return [args, other_args]






def main():
    [known_args, other_args] = do_argparse()

    logger = Logger(K_LOG_FILE).get_logger()
    logger.info("Logger is inited")
    logger.info("known cmd args: {}".format(known_args))
    logger.info("other cmd args: {}".format(other_args))

    env = Env()
    env['logger'] = logger
    # adding required/mandatory variables
    env['solution_dir'] = os.path.realpath(K_SOLUTION_DIR)
    env['sl_config_dir'] = os.path.realpath(K_ENV_CONFIG_DIR)
    env['cmd_known_args'] = known_args
    env['cmd_other_args'] = other_args
    
    env.append_env("{}/slang.env.json".format(env['sl_config_dir']))

    try:

        PluginLoader(env, "OpenProject").process()
        PluginLoader(env, "LoadProjectEnv").process()
        env.print_env()
        logger.info("==> definition_lang = {}".format(env["definition_lang"]))

        do_test(env)

    except Exception as e:
        logger.error("test, exception error: {}".format(e))
        logger.error(traceback.format_exc())
    except:
        logger.error("test, Unexpected error")
        logger.error(traceback.format_exc())


    

    # 


def do_test(env):
    logger = Logger(K_LOG_FILE).get_logger()

    # env.print_env()

    # subt_file_src = "{}/subt_src.srt".format(env["prj_temp_dir"])
    # subt_file = "{}/subt.srt".format(env["prj_temp_dir"])
    # if os.path.isfile(subt_file):
    #     os.remove(subt_file)

    # shutil.copyfile(subt_file_src, subt_file)

    # PluginLoader(env, "PreprocessSubtitleFile").process(subt_file=subt_file)

    import wx
    
    # env["last_played_file"] = ""
    # env.append_env("{}/ui_open.env.json".format(env["prj_config_local_dir"]))
    # env.append_env("{}/video.project.env.json".format(
    #     env["prj_config_local_dir"]))
    # app = wx.App(False)
   
    # env.print_env()

    # PluginLoader(env, "InitVideoParams").process(
    #     source="https://youtu.be/KvE9j2vTpSg"
    #     , directory=env["prj_temp_dir"])

    # result = PluginLoader(env, "YouglishLoad").process(
    #      url="https://youglish.com/getbyid/87917135/hilarious/english")
    # logger.info("==> result = {}".format(result))

    result = PluginLoader(env, "CheckDependencies").process()



main()
