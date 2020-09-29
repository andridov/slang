import sqlite3

from plugin_Base import PluginBase


class QueryDB(PluginBase):
    def __init__(self, env, name, plugin_path):
        super().__init__(env, name, plugin_path=plugin_path)


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


