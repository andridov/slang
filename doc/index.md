# slang Documentation

**About:** this project should help you to study your language.
started at [2.02.2019]  


---

### [root readme](../README.md)
### [directory structure](directoryStructure.md)

### [SQLite queries](sqlQueries.md)
### [How to ...](howTo.md)
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


---
# other links
  * [Languages](languages.md)
  * [text operations](textOperations.md)
  * [otherRefs](references.md)

this documentation can be easily red in firefox with "GitLab Markdown viewer" add-on
