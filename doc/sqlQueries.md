# SQL
this is the most common quieris used for sland_db sqlite database.


### List of notes in study progress:
```sql
SELECT
    n.id 
    , datetime(a.last_used_time, 'unixepoch') AS last_used_time
    , datetime(a.last_used_time + a.pace_time, 'unixepoch') AS next_use_time
    , datetime(a.last_used_time + a.pace_time, 'unixepoch') < datetime('now') AS ex
    , a.pace_time
    , n.term
    , n.definition
FROM achievements a
JOIN types t ON t.id = a.item_type_id AND t.name = 'note'
JOIN notes n ON n.id = a.item_id 
ORDER BY next_use_time
```

### inserting note with avoid duplication of id (not used now)
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


### Adding new tags to deque
```sql
    CREATE TABLE temp_vars(
        deque_id integer,
        base_category_name text,
        description text,
        current_scope_id integer
    );
    
    insert into temp_vars(deque_id, base_category_name, description)
    --  deque_id, tag_name, tag_description
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

# removing duplicated note

```sql
--select notes to delete
select max(n.id), n.term as id_to_delete
from notes n
group by n.term having count(n.term) > 1

--delete this notes from achievements first
delete from achievements
where 
    item_id in (
        select max(n.id) as id_to_delete
        from notes n
        group by n.term having count(n.term) > 1)
    and item_type_id in (
        select id from types where name = 'note')
    
-- delete items from notes table
delete from notes
where id in(
    select max(n.id) as id_to_delete
        from notes n
        group by n.term having count(n.term) > 1)
```

# other links:

### [Index](Index.md)