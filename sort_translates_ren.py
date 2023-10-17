import renpy

"""renpy
init python in translation_tools:
"""

from collections import defaultdict
import itertools
import os

def sort_translates(languages=None, leave_backup=True):
    """
    Puts the orphan translations at the end of the file they're in, and (as a side-effect)
    orders the non-obsolete translations in the order of the dialogue they're translating.

    If `languages` is given, only the translations for these languages are sorted.
    `languages` can be a single language name or a list of language names.
    """

    set_all = set(renpy.known_languages())

    # checking languages
    if languages is None:
        languages = set_all
    else:
        if isinstance(languages, str):
            languages = {languages}
        languages = set(languages)

        unknowns = languages - set_all
        if unknowns:
            raise ValueError("languages contains unknown languages : {}".format(unknowns))

    dialogue = {} # identifier : (filename, linenumber)
    trans = {lang : defaultdict(list) for lang in languages} # language : filename : list of nodes
    transstring = defaultdict(list) # filename : list of "translate strings" nodes (which are actually init nodes)
    for nod in renpy.game.script.all_stmts:
        if isinstance(nod, renpy.ast.Translate):
            if nod.language is None:
                dialogue[nod.identifier] = (nod.filename, nod.linenumber)
            elif nod.language in languages:
                if "/tl/"+nod.language+"/" in nod.filename:
                    trans[nod.language][nod.filename].append(nod)
        elif isinstance(nod, renpy.ast.Init) and all(isinstance(n, renpy.ast.TranslateString) for n in nod.block):
            if "/tl/" in nod.filename:
                transstring[nod.filename].append(nod)
    dialogue = sorted(dialogue, key=dialogue.get) # list of all dialogue identifiers in the base game, in appearance order

    headermarker = object()
    stringsmarker = object()
    warning_comment = "\n# TODO: The following nodes are orphans, trying to translate an identifier that's not in the game.\n"
    for subdict in trans.values():
        for fn, nodlist in sorted(subdict.items()):
            long_fn = os.path.join(renpy.config.basedir, fn)
            has_orphans = False

            with open(long_fn, "r", encoding = "utf-8") as f:
                lines = f.read().splitlines()

            boundaries = {} # linenumber : (language, identifier)
            for nod in itertools.chain(nodlist, transstring[fn]):
                linenumber = nod.linenumber-1

                while lines[linenumber-1].startswith("#"):
                    linenumber -= 1

                if isinstance(nod, renpy.ast.Translate):
                    boundaries[linenumber] = (nod.language, nod.identifier)
                    if (not has_orphans) and (nod.identifier not in dialogue):
                        has_orphans = True
                else:
                    boundaries[linenumber] = ("", stringsmarker)

            if not has_orphans:
                print("Skipping {} : no orphans".format(fn))
                continue

            blocks = {} # (language, identifier) : block of lines
            block = []
            key = ("", headermarker)
            for linenumber, line in enumerate(lines):
                if linenumber in boundaries:
                    if linenumber:
                        blocks[key] = "\n".join(block)
                    block = []
                    key = boundaries[linenumber]
                block.append(line)
            blocks[key] = "\n".join(block)
            blocks["", warning_comment] = warning_comment

            def block_sort_function(key):
                """
                First the start of the file, then the good translate nodes,
                then the strings, then the warning, then the orphan nodes.
                """

                (language, identifier), _block = key

                index = 0
                if identifier is headermarker:
                    group = 0
                elif identifier is stringsmarker:
                    group = 2
                elif identifier is warning_comment:
                    group = 3
                elif identifier in dialogue:
                    group = 1
                    index = dialogue.index(identifier)
                else:
                    group = 4

                return (group, index, language)

            orderedblocks = [block for _key, block in sorted(blocks.items(), key=block_sort_function)]

            print("Writing sorted file {}".format(fn))

            if leave_backup:
                with open(long_fn+".new", "w", encoding="utf-8") as f:
                    f.write("\n".join(orderedblocks))

                try:
                    os.unlink(long_fn + ".bak")
                except Exception:
                    pass

                os.rename(long_fn, long_fn + ".bak")
                os.rename(long_fn + ".new", long_fn)
            else:
                with open(long_fn, "w", encoding="utf-8") as f:
                    f.write("\n".join(orderedblocks))

def sort_translates_command():

    ap = renpy.arguments.ArgumentParser()

    ap.add_argument("languages", default=[], nargs='+', action="store", help="The translation languages to update.")
    ap.add_argument("--backup", "-k", default=False, action="store_true", help="Whether to keep obsolete translations.")

    args = ap.parse_args()

    print("Adding sources to languages {}".format(args.languages))
    sort_translates(args.languages, args.backup)

    exit(0)

renpy.store.renpy.arguments.register_command("sort_translates", sort_translates_command)
