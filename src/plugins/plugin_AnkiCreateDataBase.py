# Slang
# Copyright: Andridov and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import sqlite3
import time
import json

import random
import re
import shutil
from hashlib import sha1
from html.parser import HTMLParser

from plugin_Base import PluginBase


# ******************************************************************************




current_time = lambda: int(round(time.time() * 1000))

ANKI_MODEL_LATEX_PRE = """\\documentclass[12pt]{article}
\\special{papersize=3in,5in}
\\usepackage{amssymb,amsmath}
\\pagestyle{empty}
\\setlength{\\parindent}{0in}
\\begin{document}
"""

ANKI_MODEL_LATEX_POST = "\\end{document}"




class AnkiCreateDataBase(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)


    def process(self, **kwargs):
        self.__init_db()



    def __init_db(self):
        self.logger.info("initializing database...")

        db_file = self.env["prj_anki_db_file"]
        self.__conn = sqlite3.connect(db_file)
        self.__cursor = self.__conn.cursor()

        if not self.__is_db_empty():
            # self.env.append_env(self.env["prj_anki_env_file"])
            self.__close()
            return

        self.env["anki_db_next_media_id"] = 0
        self.env["anki_db_next_note_id"] = current_time()
        self.env["anki_db_next_card_id"] = current_time()
        self.last_card_due = current_time()


        schema_file = self.env["anki_data_dir"] + "/database/schema.sql"
        schema_q = open(schema_file, 'r', encoding="utf8").read()

        self.__cursor.executescript(schema_q)

        #database specific settings
        self.env["anki_db_desk_id"] = current_time()
        self.env["anki_db_model_id"] = current_time()

        self.__create_column_table_struct()
        self.__fill_col_table()

        self.__close()
        self.__save_db_stat_settings()
        self.logger.info("initializing database is finished")



    def __save_db_stat_settings(self):
        anki_settings = [
            { "anki_db_next_media_id": self.env["anki_db_next_media_id"] },
            { "anki_db_next_note_id": self.env["anki_db_next_note_id"] },
            { "anki_db_next_card_id": self.env["anki_db_next_card_id"] },
            { "anki_db_desk_id": self.env["anki_db_desk_id"]},
            { "anki_db_model_id": self.env["anki_db_model_id"] }
        ]
        with open(self.env["prj_anki_env_file"], 'w') as jf:
            json.dump(anki_settings, jf, 
                indent=2, ensure_ascii=False, sort_keys=False)


    def __is_db_empty(self):
        self.__cursor.execute("""SELECT name FROM sqlite_master 
            WHERE type='table' AND name='cards';""")
        result = self.__cursor.fetchall()
        return not result



    def __close(self):
        self.__conn.commit()
        self.__conn.close()



    def __read_file(self, file_name):
        with open(file_name, 'r', encoding="utf8")  as f:
            data=f.read()
            return data



    def __read_html_templates(self):
        self.__frontF2N_html = self.__read_file(self.env["mct_front_F2N"])
        self.__backF2N_html = self.__read_file(self.env["mct_back_F2N"])
        self.__frontN2F_html = self.__read_file(self.env["mct_front_N2F"])
        self.__backN2F_html = self.__read_file(self.env["mct_back_N2F"])
        self.__model_css = self.__read_file(self.env["mct_model_css"])


    def __create_column_table_struct(self):

        self.__read_html_templates()
        # value for table `col`: `desks`
        self.__col_desk = {
                "id": 1,
                "name": "Default",
                "conf": 1,
                "desc": "",
                "name": self.env["prj_name"],
                "extendRev": 50,
                "usn": -1,
                "collapsed": False,
                "newToday": [0, 0],
                "timeToday": [0, 0],
                "dyn": 0,
                "extendNew": 10,
                "conf": 1,
                "revToday": [0, 0],
                "lrnToday": [0, 0],
                #"id": self.__dbo.k_desk_id,
        }

        self.__col_model = {
            "vers": [],
            "name": self.env["prj_name"],
            "tags": [],
            "did":  self.env["anki_db_desk_id"],
            "usn": -1,
            "req": [
                [   
                    0, 
                    "any",
                    [
                         0,  1,  2,  3,  4,  5,  6,
                         7,  8,  9, 10, 11, 12, 13,
                        14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27,
                        28, 29, 30, 31, 32, 33, 34,
                        35, 36, 37, 38, 39, 40, 41
                    ]
                ],
                [   
                    1, 
                    "any",
                    [
                         0,  1,  2,  3,  4,  5,  6,
                         7,  8,  9, 10, 11, 12, 13,
                        14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27,
                        28, 29, 30, 31, 32, 33, 34,
                        35, 36, 37, 38, 39, 40, 41
                    ]
                ],
            ],

            "flds": [
                {"name": "term"                 , "rtl": False, "sticky": False, "media": [],  "ord":  0, "font": "Helvetica", "size": 22},
                {"name": "term_note"            , "rtl": False, "sticky": False, "media": [],  "ord":  1, "font": "Helvetica", "size": 15},
                {"name": "term_audio"           , "media": [],  "sticky": False, "rtl": False, "ord":  2, "font": "Helvetica", "size": 20},
                {"name": "image"                , "media": [],  "sticky": False, "rtl": False, "ord":  3, "font": "Helvetica", "size": 20},
                {"name": "definition"           , "rtl": False, "sticky": False, "media": [],  "ord":  4, "font": "Helvetica", "size": 22},
                {"name": "definition_note"      , "rtl": False, "sticky": False, "media": [],  "ord":  5, "font": "Helvetica", "size": 15},
                {"name": "definition_audio"     , "media": [],  "sticky": False, "rtl": False, "ord":  6, "font": "Helvetica", "size": 20},

                {"name": "ex1_term"             , "rtl": False, "sticky": False, "media": [],  "ord":  7, "font": "Helvetica", "size": 22},
                {"name": "ex1_term_note"        , "rtl": False, "sticky": False, "media": [],  "ord":  8, "font": "Helvetica", "size": 15},
                {"name": "ex1_term_audio"       , "media": [],  "sticky": False, "rtl": False, "ord":  9, "font": "Helvetica", "size": 20},
                {"name": "ex1_image"            , "media": [],  "sticky": False, "rtl": False, "ord": 10, "font": "Helvetica", "size": 20},
                {"name": "ex1_definition"       , "rtl": False, "sticky": False, "media": [],  "ord": 11, "font": "Helvetica", "size": 22},
                {"name": "ex1_definition_note"  , "rtl": False, "sticky": False, "media": [],  "ord": 12, "font": "Helvetica", "size": 15},
                {"name": "ex1_definition_audio" , "media": [],  "sticky": False, "rtl": False, "ord": 13, "font": "Helvetica", "size": 20},

                {"name": "ex2_term"             , "rtl": False, "sticky": False, "media": [],  "ord": 14, "font": "Helvetica", "size": 22},
                {"name": "ex2_term_note"        , "rtl": False, "sticky": False, "media": [],  "ord": 15, "font": "Helvetica", "size": 15},
                {"name": "ex2_term_audio"       , "media": [],  "sticky": False, "rtl": False, "ord": 16, "font": "Helvetica", "size": 20},
                {"name": "ex2_image"            , "media": [],  "sticky": False, "rtl": False, "ord": 17, "font": "Helvetica", "size": 20},
                {"name": "ex2_definition"       , "rtl": False, "sticky": False, "media": [],  "ord": 18, "font": "Helvetica", "size": 22},
                {"name": "ex2_definition_note"  , "rtl": False, "sticky": False, "media": [],  "ord": 19, "font": "Helvetica", "size": 15},
                {"name": "ex2_definition_audio" , "media": [],  "sticky": False, "rtl": False, "ord": 20, "font": "Helvetica", "size": 20},

                {"name": "ex3_term"             , "rtl": False, "sticky": False, "media": [],  "ord": 21, "font": "Helvetica", "size": 22},
                {"name": "ex3_term_note"        , "rtl": False, "sticky": False, "media": [],  "ord": 22, "font": "Helvetica", "size": 15},
                {"name": "ex3_term_audio"       , "media": [],  "sticky": False, "rtl": False, "ord": 23, "font": "Helvetica", "size": 20},
                {"name": "ex3_image"            , "media": [],  "sticky": False, "rtl": False, "ord": 24, "font": "Helvetica", "size": 20},
                {"name": "ex3_definition"       , "rtl": False, "sticky": False, "media": [],  "ord": 25, "font": "Helvetica", "size": 22},
                {"name": "ex3_definition_note"  , "rtl": False, "sticky": False, "media": [],  "ord": 26, "font": "Helvetica", "size": 15},
                {"name": "ex3_definition_audio" , "media": [],  "sticky": False, "rtl": False, "ord": 27, "font": "Helvetica", "size": 20},

                {"name": "ex4_term"             , "rtl": False, "sticky": False, "media": [],  "ord": 28, "font": "Helvetica", "size": 22},
                {"name": "ex4_term_note"        , "rtl": False, "sticky": False, "media": [],  "ord": 29, "font": "Helvetica", "size": 15},
                {"name": "ex4_term_audio"       , "media": [],  "sticky": False, "rtl": False, "ord": 30, "font": "Helvetica", "size": 20},
                {"name": "ex4_image"            , "media": [],  "sticky": False, "rtl": False, "ord": 31, "font": "Helvetica", "size": 20},
                {"name": "ex4_definition"       , "rtl": False, "sticky": False, "media": [],  "ord": 32, "font": "Helvetica", "size": 22},
                {"name": "ex4_definition_note"  , "rtl": False, "sticky": False, "media": [],  "ord": 33, "font": "Helvetica", "size": 15},
                {"name": "ex4_definition_audio" , "media": [],  "sticky": False, "rtl": False, "ord": 34, "font": "Helvetica", "size": 20},

                {"name": "ex5_term"             , "rtl": False, "sticky": False, "media": [],  "ord": 35, "font": "Helvetica", "size": 22},
                {"name": "ex5_term_note"        , "rtl": False, "sticky": False, "media": [],  "ord": 36, "font": "Helvetica", "size": 15},
                {"name": "ex5_term_audio"       , "media": [],  "sticky": False, "rtl": False, "ord": 37, "font": "Helvetica", "size": 20},
                {"name": "ex5_image"            , "media": [],  "sticky": False, "rtl": False, "ord": 38, "font": "Helvetica", "size": 20},
                {"name": "ex5_definition"       , "rtl": False, "sticky": False, "media": [],  "ord": 39, "font": "Helvetica", "size": 22},
                {"name": "ex5_definition_note"  , "rtl": False, "sticky": False, "media": [],  "ord": 40, "font": "Helvetica", "size": 15},
                {"name": "ex5_definition_audio" , "media": [],  "sticky": False, "rtl": False, "ord": 41, "font": "Helvetica", "size": 20}
            ],
            "sortf": 0,
            "latexPre": ANKI_MODEL_LATEX_PRE,
            "tmpls": [
                {
                    "name": "Card F2N",
                    "qfmt": self.__frontF2N_html,
                    "bsize": 12,
                    "bafmt": "",
                    "did": None,
                    "afmt": self.__backF2N_html,
                    "bfont": "Helvetica",
                    "ord": 0,
                    "bqfmt": ""
                },
                {
                    "name": "Card N2F",
                    "qfmt": self.__frontN2F_html,
                    "bsize": 12,
                    "bafmt": "",
                    "did": None,
                    "afmt": self.__backN2F_html,
                    "bfont": "Arial",
                    "ord": 1,
                    "bqfmt": ""
                }
            ],
            "latexPost": ANKI_MODEL_LATEX_POST,
            "type": 0,
            "id": str(self.env["anki_db_model_id"]),
            "css": self.__model_css,
            "mod": 1507067299
        }



    def __fill_col_table(self):
        # Create one row in table `col` with anki model data

        # arbitrary number since there is only one row
        col_id = 1 
        # timestamp of the creation date. It's correct up to the day. For V1
        # scheduler, the hour corresponds to starting a new day. By default, 
        # new day is 4.
        col_crt = current_time()
        #last modified in milliseconds
        col_mod = current_time()
        # schema mod time: time when "schema" was modified. 
        # If server scm is different from the client scm a full-sync is required
        col_scm = current_time()
        col_ver = 11
        col_dty = 0
        col_usn = 0
        col_ls = 0
        col_conf = json.dumps({})
        # Anki merges different models by their id in one structure
        col_model = json.dumps({self.env["anki_db_model_id"]: self.__col_model})
        # Same for desks
        self.__col_desk['mod'] = current_time()
        # col_decks = json.dumps({self.env["anki_db_model_id"]: self.__col_desk})
        col_decks = json.dumps({"1": self.__col_desk})
        self.logger.info(col_decks)
        # no additional config required
        col_dconf = json.dumps({})
        col_tags = json.dumps({})

        self.__cursor.execute(
            """INSERT INTO col (
                id, crt, mod, scm, ver, dty, usn
                , ls, conf, models, decks, dconf, tags)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (col_id
                , col_crt
                , col_mod
                , col_scm
                , col_ver
                , col_dty
                , col_usn
                , col_ls
                , col_conf
                , col_model
                , col_decks
                , col_dconf
                , col_tags))
