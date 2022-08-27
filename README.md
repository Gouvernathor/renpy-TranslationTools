# renpy-TranslationTools

This contains various tools helping to manage translations in renpy.

## sort_translates

This is a cleanup tool for your translation files.

When you add dialogue to your game, or when you edit dialogue lines without adding an `id` clause, then regenerate
translations from the launcher, the new dialogue lines are put at the end of the file, beneath the `translate strings` blocks -
if any.

This helps with that situation. It reorders every block in the translation files of the provided languages, so that you have :
- first the "good" translations of actually valid dialogue lines, which get sorted to reflect the order of the original dialogue,
- then the `translate strings` block(s),
- and at the end, the obsolete or orphan translation blocks, beneath a comment saying what they are.

The tools is careful to keep every line in the file, none is removed, they are only moved around. But be careful, comments or
other renpy code between translation blocks will be ignored and may be displaced along with their surroundings to random places
within the file. The orphan blocks are not removed, because you may want to use their content to translate the blocks they replaced, or to
add their `id` clauses to dialogue lines you edited.

Warning : to minimize risks of bugs, files with no orphan nodes are skipped, and their translate blocks are not ordered.
If you want to sort every file, remove the `if not has_orphans:` `continue` block in the function.

To use, simply drag the \_ren.py file in your game's `game/` folder, then open the console with Shift+O (the letter) and call
`translation_tools.sort_translates()`. You can optionally pass a language or list of languages as parameter.

The tool leaves by default a copy of the untouched file, renamed as .bkp. To disable this, pass `leave_backup=False` to the
function.

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

To use it, simply frop the \_ren.py file in your game's repository, generate from the launcher the "target" translations on
which you want to add these comments, the open the game, hit Shift+O (the letter) to open the console, and call
`translation_tools.add_languages()`. The first parameter should contain either the language or a list of languages you
want to receive the comments, and the second parameter should receive a list of languages whose transations will be added
as comments. If the second parameter is not given, all existing translations, except the target ones, will be added as
comments. You can then delete the \_ren.py and the .rpyc files from your game.
