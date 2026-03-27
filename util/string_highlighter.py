"""
A text highlighter for regex/string substitution.

Contains:
class StringVariableHighlighter
  highlightBlock

TODO:
- This was not my code, so I need to review it and textman to figure out exactly how all of this
  stuff was handled.

"""

from PyQt6 import QtGui
import re

import globals

class StringVariableHighlighter(QtGui.QSyntaxHighlighter):
    """
    This class highlights different string commands. These can be (though are not exclusively) 
    string substitutions (e.g. {HERO}, with the player's name for them being substituted into 
    dialogue).
    """
    def __init__(self, text):
        QtGui.QSyntaxHighlighter.__init__(self, text)

    def highlightBlock(self, text):

        good_bracket_format = QtGui.QTextCharFormat()
        good_bracket_format.setForeground(QtGui.QColor('white'))
        good_bracket_format.setBackground(QtGui.QColor('black'))

        regex_num = re.compile(r'{\w+}')
        match_iter = regex_num.finditer(text)
        for m in match_iter:
            self.setFormat(m.start(), m.end() - m.start(), good_bracket_format)

        # nned to check if same amount of { and }
        # if not, look further to see where the problem is
        # and highlight as incorrect
        # maybe I could take the above {abc} curly bracket positions I found above
        # remove the { } chars at those start+end positions from the temp string
        # and then flag any further { } I find... sounds good I think
        # oh actually, changing the temp string is a problem because the length would be wrong, used for applying the format.
        # i can just skip the 'good' { } positions when going through the bad ones/going through all of them... no issue.
        # or, if I remove {} from the allowed chars, they will be highlighted red, but then I can after highlight good ones black..

        # check to make sure only legal characters are entered
        # don't simply check whether an illegal char exists... find where it is!
        # does this handle emoji? 😀 came up as 2 boxes (only first was highlighted) - but they are joined/grouped.. maybe the font?
        # but when adding a character/illegal char after it, it showed up properly (when formatted, shows up due to now html...?)
        # probably nothing to worry about
        allowed_chars = 'ABCDEFGHIJKLMONPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{} '
        allowed_chars += globals.my_textman.hiragana_string
        allowed_chars += globals.my_textman.katakana_string
        allowed_chars += globals.my_textman.kanji_list
        allowed_chars += globals.my_textman.jp_chars
        allowed_chars += 'ー'

        illegal_char_format = QtGui.QTextCharFormat()
        illegal_char_format.setBackground(QtGui.QColor('red'))

        regex_num = re.compile(f'[^{allowed_chars}]')
        match_iter = regex_num.finditer(text)
        for m in match_iter:
            self.setFormat(m.start(), m.end() - m.start(), illegal_char_format)