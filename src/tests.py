
"""
Study LANGuage project. Tests
Copyright: Andridov and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""

import argparse
import os
import sys

from sl_logger import Logger
from sl_env import Env

sys.path.insert(1, './plugins')
sys.path.insert(2, './plugins/common')
sys.path.insert(3, './test/plugins/config')
sys.path.insert(1, './test/plugins/src')

from sl_pluginLoader import PluginLoader
from sl_pepProcessor import PluginEntryPointProcessor


# these variables needed to initialize log and start to parse slang.eng.json
# other variables should be loaded via *.env.json files
K_LOG_FILE = "../logs/tests.log"

# start looking for base env.folder in project folder, than use default
K_ENV_CONFIG_DIR_1 = "../data/projects/{}/config"
K_ENV_CONFIG_DIR_2 = "../data/config"
K_SOLUTION_DIR = "./.."
K_PROJECT_NAME = "Tests"



def do_argparse():
    parser = argparse.ArgumentParser(description='utils conmmand line')

    # base arguments/actions
    parser.add_argument('--extract-pm3'
         , dest='extract_mp3', action='store_true'
         , help="splits full mp3 sound track into multiple mp3, " \
            "acordingly to subtitles intervals, save them to db \n" \
            " \tlist of additional arguments:"
            " \t  [--input-file]")

    # auxilary arguments (could be used in combination with any base args)
    # parser.add_argument('--project-name', metavar='n', type=str
    #     , help='the name of the project')


    parser.add_argument

    args, other_args = parser.parse_known_args()

    return [args, other_args]



def set_config_dir(env):
    config_dir = K_ENV_CONFIG_DIR_1.format(env['sl_project_name'])
    if not os.path.isdir(config_dir):
        config_dir = K_ENV_CONFIG_DIR_2
    env['sl_config_dir'] = config_dir



def main():
    [known_args, other_args] = do_argparse()

    logger = Logger(K_LOG_FILE).get_logger()
    logger.info("Logger is inited")
    logger.info("known cmd args: {}".format(known_args))
    logger.info("other cmd args: {}".format(other_args))

    env = Env()
    env['logger'] = logger
    # adding required/mandatory variables
    env['solution_dir'] = K_SOLUTION_DIR
    env['sl_project_name'] = K_PROJECT_NAME
    set_config_dir(env)
    env['cmd_known_args'] = known_args
    env['cmd_other_args'] = other_args

    # adding common slang.env envirionment
    env.append_env("{}/slang.env.json".format(env['sl_config_dir']))
    # override config dir and save the main before
    env['sl_cfg_plugin_dir_main'] = env['sl_cfg_plugin_dir'] 
    env['sl_cfg_plugin_dir'] = '../test/plugins/config'
    env['sl_testing_plugin_dir'] = '../test/plugins/src'
    env.print_env()


    sys.path.insert(1, os.path.realpath(env["sl_testing_plugin_dir"]))


    # if env["cmd_known_args"].extract_mp3:
    #     PluginLoader(env, "SplitSoundTrack").process()
    #     return

    # if env["cmd_known_args"].update_known_words_db:
    #     sys.path.insert(1, './plugins/known_words_db')
    #     pepp = PluginEntryPointProcessor(env, "sl_pep_UpdateKnownWordsDb")
    #     pepp.process()
    #     return


    # run all tests
    # sys.path.insert(1, './test')
    # pepp = PluginEntryPointProcessor(env, "sl_pep_Tests")
    # pepp.process()
    # return


main()
