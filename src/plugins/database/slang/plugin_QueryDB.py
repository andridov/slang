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
        if not "queries_list" in kwargs:
            raise Exception(
                "QueryDB: missing mandatory parameter: 'queries_list'")

        return self.__update_db(**kwargs)


    def __update_db(self, **kwargs):
        conn = sqlite3.connect(self.env["sl_slang_database_file"])
        cursor = conn.cursor()

        results_list = []

        for q in kwargs["queries_list"]:
            cursor.execute(q["query"], q["data"])
            results_list.append(cursor.fetchall())

        conn.commit()
        conn.close()

        return results_list


