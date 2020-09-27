import os
import sys
import sqlite3


from plugin_Base import PluginBase

class WordsDbCreate(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        


    def process(self, param_map=None):
        if os.path.isfile(self.env["prj_database_file"]):
            self.logger.info("database file already exists: {}".format(
                self.env["prj_database_file"]))
            return

        self.__create_database()



    def __create_database(self):
        self.logger.info("creating database database: {}".format(
            self.env["prj_database_file"]))

        self.__conn = sqlite3.connect(self.env["prj_database_file"])
        self.__cursor = self.__conn.cursor()


        schema_q = open(
            self.env["prj_database_schema_file"], 'r', encoding="utf8").read()

        self.__cursor.executescript(schema_q)

        self.__conn.commit()
        self.__conn.close()
        self.logger.info("creating database is finished")
