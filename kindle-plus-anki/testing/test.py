# -*- coding: utf-8 -*-
# Copyright: Kyle Hwang <feathered.hwang@hotmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# for testing convenience
#


import logging
import os
import re

from collections import namedtuple

from PyQt5.QtWidgets import QAction
from aqt import mw
from aqt.utils import getFile, showInfo, showText
# import anki notes library
from anki import notes



def do_test():
    """
    For testing convenience
    """
    logging.info('Hello World!')
    import_clippings()


StdClipping = namedtuple('Clipping', ('title', 'author', 'quote'))


# TODO get page
CLIPPING_PATTERN = r'''(?P<title>.*)[ ][(](?P<author>.*)[)]
.*

(?P<quote>.*)'''


def import_clippings():
    # get the file to be imported
    path = getFile(mw, 'Open Kindle clippings', cb=None, filter='Clippings file (*.txt *.html)', key='KindleHighlights')
    if not path:
        return

    # get the lowered extension of the file
    ext = os.path.splitext(path)[1][1:].lower()
    if ext == 'txt':
        matched_ones, unmatched_ones = parse_text_clippings(path)
    elif ext == 'html':
        # TODO Import from html
        return
    else:
        raise RuntimeError(f'Unknown extension in path: {path!r}')

    # transfer to note type
    deck = mw.col.decks.byName('English')
    model = mw.col.models.byName('Plain Text')
    for std_clipping in matched_ones:
        note = notes.Note(mw.col, model)
        note.model()['did'] = deck['id']
        note['Mother Language'] = std_clipping.quote
        note['Provenance'] = std_clipping.title + ' by ' + std_clipping.author
        mw.col.addNote(note)

    if unmatched_ones:
        showText(
            f'The following {len(unmatched_ones)} clippings could not be parsed:\n\n' +
            '\n==========\n'.join(unmatched_ones)
        )


def parse_text_clippings(path):
    matched_ones = []
    unmatched_ones = []

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().replace(u'\ufeff', '')
        clippings = content.rsplit('\n==========\n')
        for clipping in clippings:
            # remove the empty one
            if not clipping:
                continue
            match = re.fullmatch(CLIPPING_PATTERN, clipping)
            if match:
                print(match.groupdict())
                std = StdClipping(**match.groupdict())
                logging.info(std)
                matched_ones.append(std)
            else:
                unmatched_ones.append(clipping)

    return matched_ones, unmatched_ones


test_action = QAction("TEST CLIPPINGS IMPORT", mw)
test_action.triggered.connect(do_test)
mw.form.menuTools.addAction(test_action)
