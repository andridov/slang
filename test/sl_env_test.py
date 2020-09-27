import sys

sys.path.insert(1, '../src')

from sl_logger import Logger
from sl_env import Env


def some_use(env_parent):
	env = env_parent.get_env_obj()
	env['new_item'] = 'this is test'
	env['__export'] = 'new_item'


def sl_env_test():
	logger = Logger("../logs/new.env.log").get_logger()
	logger.info('Logger is inited')
	
	env = Env()
	env.append_env("../data_new/test/new.env.json")
	env.print_env()

	some_use(env)
	env.print_env()




sl_env_test()