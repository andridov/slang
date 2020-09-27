# anki

this sub_project needed for creating and extending [anki](https://en.wikipedia.org/wiki/Anki_(software)) cards   
see https://apps.ankiweb.net for more about anki.

### Project data loading

All curent anki project data contains in $(anki_project_dir) directory, see [anki.settings.json](../config/anki.settings.json)
Project directory structure is:

```
project_name
    │
    ├── data               $(anki_project_data_dir)   Specific project data
    |   | 
    |   └── sl_tmp         $(anki_project_tmp_dir)    This is temprorary folder. could be deleted at the beginning of work
    |
    └── media              $(anki_media_dir)          All mdia content that needed for project
        |
        ├── audios         $(anki_audios_dir)         Audio data needed for creating cards
        |
        └── images         $(anki_audios_dir)         Images data, needed for cards
    cards.json                                        Json with card items. 
```

#### Json card-item description
```json
{
	"card_items": [
		{
			"term": "anki_card",
			"term_note": "some additional info about term",
			"term_audio": "audio_term_example.mp3",
			"image": "my_theme/example_image.jpg",
			"definition": "A question and answer pair is called a card. This is based on a paper flashcard with a question on one side and the answer on the back.",
			"definition_note": "additional info about definition termin, showed with smaller font",
			"definition_audio": "definition_audio.mp3",
			"examples": [
				{
					"term": "example_1",
					"term_note": "additional info",
					"term_audio": "audio_term_example.mp3",
					"image": "my_theme/examples/example_image.jpg",
					"definition": "definition for example",
					"definition_note": "additional info",
					"definition_audio": "definition_audio.mp3"
				},
				{
					"term": "example_2",
					"term_note": "additional info",
					"term_audio": "audio_term_example_233.mp3",
					"image": "other/examples/example_image_1.jpg",
					"definition": "definition for example 2",
					"definition_note": "additional info",
					"definition_audio": "definition_audio.mp3"
				},
			]
		}
	]
}
```
* **term** - is the word/sentence to study
* **term_note** - additional info about the word/sentence to study
* **image** - the image, that is shown on the back side of card. image must be placed in $(anki_images_dir) folder see [anki.settings.json](../config/anki.settings.json)
* **term_audo** - soud, related with term, audio file must be placed in $(anki_audios_dir) folder see [anki.settings.json](../config/anki.settings.json)
* **definition** - is meaning of term you whant to see in answer(other side of card)
* **definition_note** - note about definition, as usual is showed smaller fonts than oter
* **definition_audio** - soud, related with term
* **examples** - node of examples. Could contain up to **5** items.

!!! *__term__, __definition__ could be HTML text wich could be pcaced instead of traditional* 

#### HTML card templates
+ Foreign -> Native
	* [front](../data/anki/data/modelCardTemplates/front1.html)
	* [back](../data/anki/data/modelCardTemplates/back1.html)
+ Native -> Foreighn
	* [front](../data/anki/data/modelCardTemplates/front2.html)
	* [back](../data/anki/data/modelCardTemplates/back2.html)

examples: [front](../data/anki/data/modelCardTemplates/examples/front.html), [back](../data/anki/data/modelCardTemplates/examples/back.html)

## Anki database
[database structure on gitHub](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure)


#### Anki Package folder structure 

Anki uses one single sqlite database to store information of multiple decks, templates, fields and cards. This file can be found inside the Anki package file (.apkg file) 
```
    .
    ├── example
    │   ├── example.anki2
    │   └── media
    └── example.apkg
```

Anki contains bascially the following types:

 * Cards
 * Decks
 * Notes
 * Templates
 * Collection


