# slang Documentation

**About:** this project should help you to study your language.
started at [2.02.2019]  


---

### [root readme](../README.md)
### [directory structure](directoryStructure.md)
### [TODO List](todoList.md)

---
projects:

## [anki](anki.md)
## [json collection maker](jsonCollectionMaker.md)

---

### dependencies

 * [pyton dependencies](python_dependencies.txt)
 * VLC
 * ffmpeg
 * Anki (desktop mobile version)


---
## [Slang data base](../data/templates/utils/data/database/slang_db_schema.sql)


## slang run

### load python dependencies
```
cd [slang]/doc
pip install -f python_dependencies.txt
```

### creating new project
```bash
cd [slang]/src
python3 slang.py -project-name [your_new_project_name] --create-project
```

### open project:
```bash
cd [slang]/src
python3 slang.py -project-name [your_project_name]
```


### creating/extending database with known words:
```bash
cd [slang]/src
python utils.py --update-known-words-db --language en-ru --description "first load" --input-file /c/Home/Temp/anki_deques/Video_en__video_en_youtube_001.apkg --tags movie 'Video_en__movie_war_dogs.apkg'
```
`--language en-ru` - defining languages (keysensitive values): 
 * __en__ - language of terms, 
 * __ru__ - language of definitions

`--description 'first load'` -some description about the imported deque
`--input-file /c/Home/Temp/anki_deques/Video_en__video_en_youtube_001.apkg` - file, deque exported from anki.

### import data from other database into the current.
Current database is defined in slang.env.json

python utils.py --import-db --input-file /c/Home/Temp/



### trainers

```bash
cd [slang]/src
python utils.py --keystroke --language en-ru
```


### ffmpeg

show stream info:
`ffprobe -i my_file.mkv`

extract sound track:
`ffmpeg -i my_file.mkv -map 0:2 -b:a 320k out.mp3`
`ffmpeg -i my_file.mkv -map 0:8 -b:a 64k -ac 2 out.mp3`

`ffmpeg -i file.mp4 -b:a 64k -ac 2 out.mp3`

extract from youtube:
`youtube-dl --all-subs -f best ...`
`ffmpeg -i my_file.mkv -b:a 64k -ac 2 out.mp3`

# queries

## SQLite

Select list of notes in order to show.
```sql
select
    n.id 
    , datetime(a.last_used_time, 'unixepoch') as last_used_time
    , datetime(a.last_used_time + a.pace_time, 'unixepoch') as next_use_time
    , datetime(a.last_used_time + a.pace_time, 'unixepoch') < datetime('now') as ex
    , a.pace_time
    , n.term
    , n.definition
from achievements a
join types t on t.id = a.item_type_id and t.name = 'note'
join notes n on n.id = a.item_id 
order by next_use_time
```

inserting note with avoid duplication of id
```sql
BEGIN;
    --PRAGMA temp_store = 2;
    CREATE TEMP TABLE _temp_note(
        id integer primary key, term text not null, definition text not null);
    
    INSERT INTO _temp_note(id, term, definition) VALUES (1586010650, 'a6', 'b6');
    
    INSERT INTO test_notes 
        SELECT 
        CASE 
            WHEN (
                select tn.id from _temp_note as tmpn 
                left outer join test_notes tn on tmpn.id = tn.id limit 1
                ) is NULL THEN id
            ELSE (select max(tn.id) + 1 from test_notes tn)
        END as id
        , term
        , definition 
        FROM _temp_note ORDER BY id LIMIT 1;
    
    DROP TABLE _temp_note;
END; 
```

```sql
    CREATE TABLE temp_vars(
        deque_id integer,
        base_category_name text,
        description text,
        current_scope_id integer
    );
    
    insert into temp_vars(deque_id, base_category_name, description)
    values(15, 'youtube', 'youtube_videos_002');
    
    insert into tags (name, description)
    values(
        (select file_name from deques where id=(select deque_id from temp_vars))
        , (select description from temp_vars)
    );
    
    update temp_vars set current_scope_id=(select max(key_id)+1 from scope);
    
    insert into scope(scope_type_id, key_id, value_id)
    values(
        (select id from types where name='tag')
        , (select current_scope_id from temp_vars)
        , (select id from tags where name=(select base_category_name from temp_vars))
    );
    
    insert into scope(scope_type_id, key_id, value_id)
    values(
        (select id from types where name='tag')
        , (select current_scope_id from temp_vars)
        , ( select t.id from tags t
            join deques d on d.file_name=t.name
            join temp_vars tv on tv.deque_id = d.id)
    );

    update deques set tags_scope_id=(select current_scope_id from temp_vars) where id=(select deque_id from temp_vars);
```

---
# other links
  * [Languages](languages.md)
  * [text operations](textOperations.md)
  * [otherRefs](references.md)

this documentation can be easily red in firefox with "GitLab Markdown viewer" add-on
