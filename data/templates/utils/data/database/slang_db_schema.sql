-- 

CREATE TABLE languages (
    id                    integer primary key autoincrement,
    term_language         text not null,
    definition_language   text not null,
    UNIQUE(term_language, definition_language)
);


CREATE TABLE deques (
    id              integer primary key autoincrement, 
    file_name       text not null,
    language_id     integer not null,
    update_time     datetime not null DEFAULT 'now',
    version         integer DEFAULT 0, 
    description     text,
    tags_scope_id   integer DEFAULT NULL,
    UNIQUE(file_name, language_id)
);


CREATE TABLE tags(
    id                  integer primary key autoincrement,
    name                text not null,
    description         text,
    UNIQUE(name)
);


CREATE TABLE cards (
    id              integer primary key autoincrement,
    deque_id        integer not null,
    base_note_id    integer DEFAULT null,
    ex_1_note_id    integer DEFAULT null,
    ex_2_note_id    integer DEFAULT null,
    ex_3_note_id    integer DEFAULT null,
    ex_4_note_id    integer DEFAULT null,
    ex_5_note_id    integer DEFAULT null,
    UNIQUE(deque_id, base_note_id)
);


CREATE TABLE notes (
    id                  integer primary key autoincrement,
    card_id             integer not null,
    creation_time       integer not null,
    mod_time            integer not null,
    term                text not null,
    term_note           text,
    term_audio_id       integer,
    image_id            integer,
    definition          text not null,
    definition_note     text,
    definition_audio_id integer,
    times_used          integer,
    UNIQUE(card_id, term, definition)
);


CREATE TABLE media (
    id            integer primary key autoincrement,
    data          blob not null
);


-- utils tables


CREATE TABLE achievements(
    id                  integer primary key autoincrement,
    item_type_id        integer not null,
        -- note
    item_id             integer not null,

    last_used_time      integer not null DEFAULT 'now',
        -- epoch milliseconds when it was last time used
    pace_time           integer,
        -- time in milliseconds, interval till the next use. Next_use_time = last_used_time + pace_time

    learning_status_id  integer DEFAULT 0, 
        -- learning status: 0 - in progress, 
        --                  1 - excluded from learning,
        --                  other - not used now

    repeat_factor        real not null DEFAULT 1.0,
        --The ease factor 

    pace_factor          real not null,
        --the value for current item to evaluate the pece_time
        --     pace_factor = f(completion_rating, pace_factor) * repeat_factor
        --     pace_time = current_pace_time * pace_factor

    reviews_count        integer not null,

    UNIQUE(item_type_id, item_id)
);


CREATE TABLE exercises(
    id                  integer primary key autoincrement,
    exercise_type_id    integer not null,
    item_type_id        integer not null,
    item_scope_id       integer not null,
    completion_rating   real not null
);


CREATE TABLE types(
    id                  integer primary key autoincrement,
    name                text not null,
    description         text,
    UNIQUE(name)
);


CREATE TABLE scope(
    id                  integer primary key autoincrement,
    scope_type_id       integer not null,
    key_id              integer not null,
    value_id            integer not null
);
CREATE INDEX ix_scope_key on scope (scope_type_id, key_id);



CREATE TABLE speedTestHistory (
    id                  integer primary key autoincrement,
    start_time          datetime not null,
    end_time            datetime not null,
    notes_count         integer not null,
    note_ids_scope      integer not null,
    words_count         integer not null,
    symbols_count       integer not null,
    speed_wpm           real not null,
    speed_spm           real not null,
    err_notes_count     integer not null,
    err_note_ids_scope  integer,
    err_words_count     integer not null
);
