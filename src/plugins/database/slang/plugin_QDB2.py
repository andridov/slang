# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import sqlite3

from plugin_Base import PluginBase


class QDB2(PluginBase):
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
            self.env["logger"] = self.__logger
            self.logger = self.__logger

    """
        db_cursor  - opened cursor to db
        query      - single query
        data       - data for single query
        query_list - list of items(dictionary) with queries(key) 
                         and their data(value)
    """
    def process(self, **kwargs):
        return self.__update_db(**kwargs)


    def __update_db(self, **kwargs):

        queries_list = []
        cursor_created = False

        if "query" in kwargs:
            data = kwargs["data"] if "data" in kwargs else ()
            queries_list = [{ kwargs["query"] : data }]
        elif "queries_list" in kwargs:
            queries_list = kwargs["queries_list"]
        else:
            raise Exception(
                "QDB2: missing mandatory parameter: 'queries_list'")

        if "db_cursor" in kwargs:
            cursor = kwargs["db_cursor"]
        else:
            conn = sqlite3.connect(self.env["sl_slang_database_file"])
            cursor = conn.cursor()
            cursor_created = True

        results_list = {}
        for q in queries_list:
            key = next(iter(q)) 
            cursor.execute(self.env[key], q[key])
            results_list[key] = cursor.fetchall()

        if cursor_created == True:
            conn.commit()
            conn.close()

        return results_list


