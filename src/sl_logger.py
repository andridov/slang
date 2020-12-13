# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


#*******************************************************************************
#Logger class (singleton)

import logging
import datetime
import os

from sl_singleton import Singleton


class Logger(metaclass=Singleton):
    pass

    logger = None

    def get_logger(self):
        if self.logger == None:
            raise Exception("Logger is not initialized!")
        return self.logger

    def __init__(self, log_file_name):
        dir = os.path.dirname(log_file_name)
        base = os.path.basename(log_file_name)
        name_ext = os.path.splitext(base)
        log_file_name = "{}/{}_{}{}".format(dir, name_ext[0]
            , datetime.datetime.now().strftime("_%Y_%m_%d"), name_ext[1])

        self.logger = logging.getLogger(log_file_name)
        self.fh = logging.FileHandler(log_file_name)
        logging.basicConfig(level = logging.DEBUG
            , format = u'%(asctime)s.%(msecs)03d [%(levelname)-8s] %(message)s'
            , datefmt="%H:%M:%S")

        self.formatter_f = logging.Formatter(
            u'%(asctime)-12s [%(levelname)-8s] %(message)s')
        self.fh.setFormatter(self.formatter_f)
        self.logger.addHandler(self.fh)
