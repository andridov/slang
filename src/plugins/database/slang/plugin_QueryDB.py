# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import sqlite3

from plugin_Base import PluginBase


class QueryDB(PluginBase):
    def __init__(self, env, name, plugin_path):
        # set logging=True if you need extra-logging
        self.logging = False
        self.__logger = None
        
        if self.logging == False and "logger" in env:
            self.__logger = env["logger"]
            del env["logger"]

        super().__init__(env, name, plugin_path=plugin_path)

        if self.logging == False and self.__logger:
            env["logger"] = self.__logger


    def process(self, **kwargs):
        return self.__update_db(**kwargs)


    def __update_db(self, **kwargs):

        queries_list = []
        cursor_created = False
        if "query" in kwargs and "data" in kwargs:
            queries_list = [{
                "query": kwargs["query"]
                , "data": kwargs["data"]
            }]
        elif "queries_list" in kwargs:
            queries_list = kwargs["queries_list"]
        else:
            raise Exception(
                "QueryDB: missing mandatory parameter: 'queries_list'")

        if "db_cursor" in kwargs:
            cursor = kwargs["db_cursor"]
        else:
            conn = sqlite3.connect(self.env["sl_slang_database_file"])
            cursor = conn.cursor()
            cursor_created = True

        results_list = []
        for q in queries_list:
            cursor.execute(q["query"], q["data"])
            results_list.append(cursor.fetchall())

        if cursor_created == True:
            conn.commit()
            conn.close()

        return results_list


