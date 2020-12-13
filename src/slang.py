# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import argparse
import os

from sl_logger import Logger
from sl_env import Env
from sl_pepProcessor import PluginEntryPointProcessor



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

    args, other_args = parser.parse_known_args()

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
    env.print_env()

    for epn in env["__entry_point"]["peps"]:
        pepp = PluginEntryPointProcessor(env, epn)
        pepp.process()




main()
