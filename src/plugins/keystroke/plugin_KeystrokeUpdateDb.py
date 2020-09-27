import sqlite3

from plugin_Base import PluginBase


class KeystrokeUpdateDb(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        

    def process(self, param_map=None):
        self.__update_db()


    def __update_db(self):
        conn = sqlite3.connect(self.env["sl_slang_database_file"])
        cursor = conn.cursor()

        results_list = []

        for q in self.env["sql_queries_list"]:
            cursor.execute(q["query"], q["data"])
            results_list.append(cursor.fetchall())

        self.env["sql_query_results_list"] = results_list

        conn.commit()
        conn.close()


