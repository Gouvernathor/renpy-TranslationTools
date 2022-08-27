import renpy

"""renpy
init python in translation_tools:
"""

from collections import defaultdict

def add_languages(target_langs, lang_list=None):
    """
    Adds commented-out translations in the `lang_list` languages
    for each translation of language `target_langs`.

    Generate translations from the launcher for the languages you want to target.
    Then, open the game and call this function with each language you want to target in `target_langs`,
    and the languages you want to be added in as comments in `lang_list`.
    Both of the parameters need to be either a language name, or a list of language names.
    If the second parameter is ommited, all the existing translations will be added as comments.
    """
    """
    This could be improved by first listing all files for target_langs and for lang_list
    in the first loop, then opening them all, and closing them all in the end.
    But time consumption is not a concern.
    """

    set_all = set(renpy.known_languages())

    # checking target_langs
    if isinstance(target_langs, str):
        target_langs = {target_langs}
    target_langs = set(target_langs)
    unknowns = target_langs - set_all
    if unknowns:
        raise ValueError("target_langs contains unknown languages : {}".format(unknowns))

    # checking lang_list
    if lang_list is None:
        lang_list = set_all
    else:
        if isinstance(lang_list, str):
            lang_list = {lang_list}
        lang_list = set(lang_list)

        unknowns = lang_list - set_all
        if unknowns:
            raise ValueError("lang_list contains unknown languages : {}".format(unknowns))
    lang_list -= target_langs

    basedir = renpy.config.basedir.replace("\\", "/") + "/"

    dic = defaultdict(list) # identifier : list of nodes
    for nod in renpy.game.script.all_stmts:
        if isinstance(nod, renpy.ast.Translate):
            if nod.language in lang_list:
                dic[nod.identifier].append(nod)

    lines_to_copy = defaultdict(list) # identifier : list of blocks of lines (list of str)
    for nodlist in dic.values():
        for nod in nodlist:
            next = nod
            while not isinstance(next.next, renpy.ast.EndTranslate):
                next = next.next
            start, end = nod.linenumber+1-1, next.linenumber-1

            with renpy.open_file(basedir + nod.filename, "utf-8") as f:
                filelines = f.read().splitlines()

            good_lines = filelines[start:end+1]
            good_lines = [line.partition("#")[0].strip() for line in good_lines]
            good_lines = tuple(filter(None, good_lines))
            if good_lines:
                lines_to_copy[nod.identifier].append("\n".join("    # "+line for line in (nod.language,)+good_lines))

    for nod in sorted(renpy.game.script.all_stmts, key=(lambda n:(n.filename, -n.linenumber))):
        if isinstance(nod, renpy.ast.Translate) and nod.language in target_langs:
            with renpy.open_file(basedir + nod.filename, "utf-8") as f:
                filelines = f.read().splitlines()

            filelines.insert(nod.next.linenumber-1, "\n" + "\n\n".join(lines_to_copy[nod.identifier]) + "\n")
            filelines.append("")
            with open(basedir + nod.filename, "w", encoding="utf-8") as f:
                f.write("\n".join(filelines))
