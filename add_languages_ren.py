import renpy

"""renpy
init python in translation_tools:
"""

from collections import defaultdict

def add_languages(target_langs, lang_list=None, remove_old = False, language_hint = True):
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

    import os

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

    basedir = renpy.config.basedir

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

            with open(os.path.join(basedir, nod.filename), 'r', encoding = "utf-8") as f:
                filelines = f.read().splitlines()

            good_lines = filelines[start:end+1]
            good_lines = [line.partition("#")[0].strip() for line in good_lines]
            good_lines = tuple(filter(None, good_lines))
            if good_lines:
                lines_to_copy[nod.identifier].append("\n".join("    # "+line for line in ((nod.language,) if language_hint else tuple())+good_lines))

    for nod in sorted(renpy.game.script.all_stmts, key=(lambda n:(n.filename, -n.linenumber))):
        if isinstance(nod, renpy.ast.Translate) and nod.language in target_langs:
            long_fn = os.path.join(basedir, nod.filename)
            with open(long_fn, 'r', encoding = "utf-8") as f:
                filelines = f.read().splitlines()

            line_offset = 1
            if remove_old:
                original_filelines_len = len(filelines)
                filelines = [
                    *filelines[:nod.linenumber],
                    *filter(
                        lambda x: not x.startswith("    #") and x.strip(),
                        filelines[nod.linenumber:nod.next.linenumber]
                    ),
                    *filelines[nod.next.linenumber:],
                ]
                line_offset += original_filelines_len-len(filelines)

            filelines.insert(
                nod.next.linenumber-line_offset,
                "\n" + "\n\n".join(lines_to_copy[nod.identifier]) + "\n",
            )

            filelines.append("")
            with open(long_fn, "w", encoding="utf-8") as f:
                f.write("\n".join(filelines))

def add_language_command():
    ap = renpy.arguments.ArgumentParser()

    ap.add_argument("languages", default=[], nargs='*', action="store", help="The translation languages to update.")
    ap.add_argument("--source-language", "-s", default=[], action="append", help="The commented-out language to add.")
    ap.add_argument("--cleanup", "-c", default=False, action="store_true", help="Whether to remove old translation hints.")
    ap.add_argument("--no-language", dest='language', default=True, action="store_false", help="Disable language name insertion when adding languages.")

    args = ap.parse_args()

    print("Adding sources to languages {}".format(args.languages))
    add_languages(args.languages, set(args.source_language) or None, args.cleanup, args.language)

    exit(0)

renpy.store.renpy.arguments.register_command("add_translation_source", add_language_command)
