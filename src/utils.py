
"""
Study LANGuage project.

Copyright: Andridov and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""

import argparse
import os
import sys

from sl_logger import Logger
from sl_env import Env

sys.path.insert(1, './plugins')
sys.path.insert(1, './plugins/common')

from sl_pluginLoader import PluginLoader
from sl_pepProcessor import PluginEntryPointProcessor


# these variables needed to initialize log and start to parse slang.eng.json
# other variables should be loaded via *.env.json files
K_LOG_FILE = "../logs/utils.log"

# start looking for base env.folder in project folder, than use default
K_ENV_CONFIG_DIR_1 = "../data/projects/{}/config"
K_ENV_CONFIG_DIR_2 = "../data/config"
K_SOLUTION_DIR = "./.."



def do_argparse():
    parser = argparse.ArgumentParser(description='utils conmmand line')

    # base arguments/actions
    parser.add_argument('--extract-pm3'
         , dest='extract_mp3', action='store_true'
         , help="splits full mp3 sound track into multiple mp3, " \
            + "acordingly to subtitles intervals, save them to db \n" \
            + " \tlist of additional arguments:"
            + " \t  [--input-file]")

    parser.add_argument('--update-known-words-db'
         , dest='update_known_words_db', action='store_true'
         , help="updates base of known words and prases, " \
            + "acordingly to subtitles intervals, save them to db \n" \
            + " \tlist of additional arguments:"
            + " \t  [--input-file]")

    parser.add_argument('--keystroke'
         , dest='keystroke', action='store_true'
         , help=", " \
            + "acordingly to subtitles intervals, save them to db \n" \
            + " \tlist of additional arguments:"
            + " \t  [--input-file]")

    parser.add_argument('--create-audio-track'
         , dest='create_audio_track', action='store_true'
         , help="creates audio track witl phrases to lean \n" \
            + " \tlist of mandatroy arguments:"
            + " \t  [--output-file]")


    # auxilary arguments (could be used in combination with any base args)
    parser.add_argument('--project-name', metavar='n', type=str
        , help='the name of the project')

    parser.add_argument('--input-file', metavar='if', type=str
        , help='the name of the input file')

    parser.add_argument('--language', metavar='l', type=str
        , help='the term-definition languages, usage --language en-de')

    parser.add_argument('--description', metavar='d', type=str
        , help='the desctipton of input')

    parser.add_argument('--tags', metavar='t',  nargs='+', type=str
        , help='the desctipton of input')

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
    env['sl_project_name'] = known_args.project_name
    set_config_dir(env)
    env['cmd_known_args'] = known_args
    env['cmd_other_args'] = other_args
    
    # adding common slang.env envirionment
    env.append_env("{}/slang.env.json".format(env['sl_config_dir']))
    env.print_env()


    if env["cmd_known_args"].extract_mp3:
        PluginLoader(env, "SplitSoundTrack").process()
        return

    if env["cmd_known_args"].update_known_words_db:
        sys.path.insert(1, './plugins/known_words_db')
        pepp = PluginEntryPointProcessor(env, "sl_pep_UpdateKnownWordsDb")
        pepp.process()
        return

    if env["cmd_known_args"].keystroke:
        sys.path.insert(1, './plugins/keystroke')
        pepp = PluginEntryPointProcessor(env, "sl_pep_Keystroke")
        pepp.process()
        return

    if env["cmd_known_args"].create_audio_track:
        sys.path.insert(1, './plugins/audio_process')
        pepp = PluginEntryPointProcessor(env, "sl_pep_AudioTrackCreator")
        pepp.process()
        return

main()
