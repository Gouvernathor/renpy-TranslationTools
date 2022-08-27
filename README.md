# renpy-TranslationTools

This contains various tools helping to manage translations in renpy.

## add_languages

This helps in a situation where you have a game in language A, say french, it's already been translated in B, a more franca
lingua, say english. You want to translate it further to C, a third language, say japanese. But there's nobody you can find
who speak both A and C, french and japanese. All you can find is B and C, translators between english and japanese.

Renpy will generate translation files for the translators to fill, and you can always give them pre-filled with the english
version, but you first have to replace every `translate english` with `translate japanese` in every file, which is tedious,
then once the translator has replaced the english with the japanese, there's nowhere for them to reread, make sure they
didn't make a mistake.

This tool adds commented-out versions of other translations than just the None one - the original dialogues - in the `translate`
blocks to fill.

Consider you have this in your `game/tl/sourcea` translation files:
```rpy
# TODO: Translation updated at 2022-13-32 00:60

# filename:1
translate sourcea start_1:

    # e "Premier message"
    e "Premier message in sourcea language"

# filename:2
translate sourcea start_2:

    # e "Deuxième message"
    e "Deuxième message in sourcea language"
```
It's the same for the `sourceb` translation.

The `target` translation has just been generated, it looks like this:
```rpy
# TODO: Translation updated at 2022-13-32 00:60

# filename:1
translate target start_1:

    # e "Premier message"
    e "Premier message"

# filename:2
translate target start_2:

    # e "Deuxième message"
    e "Deuxième message"
```

Calling `translation_tools.add_languages("target", ("sourcea", "sourceb"))` will turn the `target` translation into this:
```rpy
# TODO: Translation updated at 2022-13-32 00:60

# filename:1
translate target start_1:

    # e "Premier message"

    # sourcea
    # e "Premier message in sourcea language"

    # sourceb
    # e "Premier message in sourceb language"

    e "Premier message"

# filename:2
translate target start_2:

    # e "Deuxième message"

    # sourcea
    # e "Deuxième message in sourcea language"

    # sourceb
    # e "Deuxième message in sourceb language"

    e "Deuxième message"
```

To use it, simply frop the _ren.py file in your game's repository, generate from the launcher the "target" translations on
which you want to add these comments, the open the game, hit Shift+O (the letter) to open the console, and call
`translation_tools.add_languages()`. The first parameter should contain either the language or a list of languages you
want to receive the comments, and the second parameter should receive a list of languages whose transations will be added
as comments. If the second parameter is not given, all existing translations, except the target ones, will be added as
comments. You can then delete the _ren.py and the .rpyc files from your game.
