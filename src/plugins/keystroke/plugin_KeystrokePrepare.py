import os
import re
import sqlite3

from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase


class KeystrokePrepare(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)
        

    def process(self, param_map=None):
        self.__parse_language()
        self.__add_db_required_data()


    def __add_db_required_data(self):
        if not not os.path.isfile(self.env["sl_slang_database_file"]):
            self.logger.info("database {} is absent. See the doc/index.md "\
                "### creating/extending database with known words:".format(
                    self.env["sl_slang_database_file"]))

        sql_queries = []
        for data_map in self.env["db_insert_or_ignore_data"]:
            request = self.env["db_insert_or_ignore"]
            table = data_map["table"]
            columns = ", ".join("'{0}'".format(w) for w in data_map["columns"])
            values = ()
            for value in data_map["values"]:
                values += value,

            values_template = "({})".format(", ".join('?' for v in values))
            request = request.format(
                table=table, columns=columns, values=values_template)

            query_item = {}
            query_item["query"] = request
            query_item["data"] = values
            sql_queries.append(query_item)

        #delete notes with empty term field.
        query_item = {}
        query_item["query"] = self.env["sql_delete_empty_term_notes"]
        query_item["data"] = ()
        sql_queries.append(query_item)

        self.env["sql_queries_list"] = sql_queries
        PluginLoader(self.env, "KeystrokeUpdateDb").process()


        self.logger.info("preparing database is finished")


    def __parse_language(self):
        if 'language' not in self.env["cmd_known_args"]:
            self.logger.warning("the 'languade' argument is absent")
            return

        m = re.match(self.env["regex_language"]
            , self.env["cmd_known_args"].language)

        if not m:
            raise SlProgramStatus("Command line argument error:",
                "flag '--language' incorrect value, syntax: --language en-en")

        self.env["term_lang"] = m.group(1)
        self.env["definition_lang"] = m.group(2)


  




