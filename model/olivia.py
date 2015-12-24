import bisect

from itertools import chain, groupby

from pyphen import pyphen
pyphen.language_fallback('en_US')

from fonts import fonttable, fonts

from state import noticeboard

from model import kevin
from model import errors
from model.wonder import words, character, _breaking_chars

hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = set((' ', '<image>'))
_BREAK_ONLY_AFTER = set('-')
_BREAK_AFTER_ELSE_BEFORE = set('–—')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE

_BREAK_P = _BREAK | set(('</p>',))

_APOSTROPHES = set("'’")


def outside_tag(sequence):
    for i in reversed(range(len(sequence) - 1)):

        if (character(sequence[i]), sequence[i + 1]) == ('<p>', '</p>'):
            del sequence[i:i + 2]

    return sequence

def _retrieve_paragraphclass(P, l):
    try:
        PSTYLE = fonttable.p_table.get_paragraph(P)
    except KeyError:
        # happens if requested style is not defined
        errors.styleerrors.add_style_error((P,), l)
        PSTYLE = fonttable.p_table.get_paragraph(('P', '_interface'))
    
    return PSTYLE

def _retrieve_fontclass(F, FONTCLASSES, l):
    F = tuple(F)
    try:
        N = FONTCLASSES[F]
        FSTYLE = fonttable.table.get_font(N)
    except KeyError:
        # happens if requested style is not defined
        errors.styleerrors.add_style_error(F, l)
        FSTYLE = fonttable.table.get_font('_interface:REGULAR')
        N = '_undefined'
    
    return N, FSTYLE
            
def _assemble_line(letters, startindex, l, anchor, stop, y, leading, COLLAPSE, FONTCLASSES, F, hyphenate=False):
    LINE = {
            'l': l,
            'i': startindex,
            
            'anchor': anchor,
            'stop': stop,
            'y': y,
            'leading': leading,
            
            'hyphen': None,
            
            'P_BREAK': False,
            'F': tuple(F)
            }
    
    # list that contains glyphs
    GLYPHS = []
    
    # start on the anchor
    x = anchor

    # retrieve font style
    N, FSTYLE = _retrieve_fontclass(F, FONTCLASSES, l)

    # blank pegs
    glyphwidth = 0
    gx = 0
    gy = 0
    effective_peg = None
    
    root = x
    root_for = set()
    front = x

    for letter in letters:
        CHAR = character(letter)

        if CHAR == '<f>':
            TAG = letter[1]
            # look for negative classes
            if '~' + TAG in F:
                F.remove('~' + TAG)
            else:
                F.append(TAG)
                F.sort()
            
            N, FSTYLE = _retrieve_fontclass(F, FONTCLASSES, l)
            
            # calculate pegging
            G = FSTYLE['pegs']
            if TAG in fonts.PEGS[G]:
                if TAG in COLLAPSE[0]:
                    if TAG in root_for:
                        x = root
                    else:
                        root = x
                
                gx, gy = fonts.PEGS[G][TAG]
                gx = gx * glyphwidth
                gy = gy * leading
                effective_peg = letter[1]
                
                y -= gy
                x += gx
            
            GLYPHS.append((-4, x, y,  N, tuple(F), x))
            
        elif CHAR == '</f>':
            TAG = letter[1]
            try:
                F.remove(TAG)
            except ValueError:
                F.append('~' + TAG)
                F.sort()

            N, FSTYLE = _retrieve_fontclass(F, FONTCLASSES, l)

            # depeg
            if TAG == effective_peg:
                y += gy

            # calculate pegging
            G = FSTYLE['pegs']
            if TAG in fonts.PEGS[G] and TAG in COLLAPSE[0]:
                root_for = set(chain.from_iterable(s for s in COLLAPSE[1] if TAG in s))
                if front > x:
                    x = front
                else:
                    front = x
            GLYPHS.append((-5, x, y,  N, tuple(F), x))
            
        elif CHAR == '<p>':
            if GLYPHS:
                break
            else:
                # we don’t load the style because the outer function takes care of that
                GLYPHS.append((
                        -2,                     # 0
                        x - FSTYLE['fontsize'], # 1
                        y,                      # 2
                        
                        N,                      # 3
                        tuple(F),               # 4
                        x - FSTYLE['fontsize']  # 5
                        ))
        
        elif CHAR == '</p>':
            LINE['P_BREAK'] = True
            GLYPHS.append((-3, x, y,  N, tuple(F), x))
            break
        
        elif CHAR == '<br>':
            root_for = set()
            GLYPHS.append((-6, x, y,  N, tuple(F), x))
            break
        
        elif CHAR == '<image>':
            root_for = set()
            IMAGE = letter[1]
                                                                                # additional fields
            GLYPHS.append((-13, x, y - leading,  N, tuple(F), x + IMAGE[1], IMAGE ))
            x += IMAGE[1]
        
        else:
            root_for = set()
            glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(CHAR) * FSTYLE['fontsize']
            
            GLYPHS.append((
                    FSTYLE['fontmetrics'].character_index(CHAR),    # 0
                    x,                                              # 1
                    y,                                              # 2
                    
                    N,                                              # 3
                    tuple(F),                                       # 4
                    x + glyphwidth                                  # 5
                    ))

            
            x += glyphwidth

            # work out line breaks
            if x > stop:
                if CHAR not in _BREAK_WHITESPACE:
                
                    n = len(GLYPHS)
                    LN = letters[:n]

                    try:
                        if CHAR in _BREAK_ONLY_AFTER:
                            i = next(i + 1 for i, v in zip(range(n - 2, 0, -1), reversed(LN[:-1])) if v in _BREAK)
                        elif CHAR in _BREAK_AFTER_ELSE_BEFORE:
                            i = len(LN) - 1
                        else:
                            i = next(i + 1 for i, v in zip(range(n - 1, 0, -1), reversed(LN)) if v in _BREAK)
                    
                    except StopIteration:
                        del GLYPHS[-1]
                        i = 0
                    
                    ### AUTO HYPHENATION
                    if hyphenate:
                        try:
                            j = i + next(i for i, v in enumerate(letters[i:]) if v in _BREAK_P)
                        except StopIteration:
                            j = i + 1989
                        
                        word = ''.join([c if len(c) == 1 and c.isalpha() else "'" if c in _APOSTROPHES else ' ' for c in letters[i:j] ])

                        leading_spaces = len(word) - len(word.lstrip(' '))

                        for pair in hy.iterate(word.strip(' ')):
                            k = len(pair[0]) + leading_spaces
                            # no sense checking hyphenations that don’t fit
                            if k >= n - i:
                                continue
                            # prevent too-short hyphenations
                            elif len(pair[0].replace(' ', '')) < 2 or len(pair[1].replace(' ', '')) < 2:
                                continue
                            
                            # check if the hyphen overflows

                            h_F = GLYPHS[i - 1 + k][4]
                            
                            h_N, HFS = _retrieve_fontclass( h_F , FONTCLASSES, l)
                                
                            if GLYPHS[i - 1 + k][5] + HFS['fontmetrics'].advance_pixel_width('-') * HFS['fontsize'] < stop:
                                i = i + k

                                LINE['hyphen'] = (
                                        HFS['fontmetrics'].character_index('-'), 
                                        GLYPHS[i - 1][5], # x
                                        GLYPHS[i - 1][2], # y
                                        h_N,
                                        h_F
                                        )
                                break
                    ####################
                    del GLYPHS[i:]

                break
                
            else:
                x += FSTYLE['tracking']
    # n changes
    LINE['j'] = startindex + len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    try:
        LINE['F'] = GLYPHS[-1][4]
    except:
        pass
    
    return LINE


class Cursor(object):
    def __init__(self, i):
        self.cursor = i
    
    def skip(self, jump, text):
        self.cursor += jump
        # prevent overruns
        if self.cursor > len(text) - 1:
            self.cursor = len(text) - 1
        if character(text[self.cursor]) == '<p>':
            direction = 1
            if jump < 0:
                direction = -1
            while True:
                self.cursor += direction
                if character(text[self.cursor]) != '<p>':
                    break

    def set_cursor(self, index, text):
        self.cursor = index
        self.skip(0, text)

class Text(object):
    def __init__(self, text, channels, cursor, select):
        self.text = kevin.deserialize(text)
        self.channels = channels
        
        self._glyphs = []
        
        self._page_intervals = {}
        # STRUCTURE:
        # PAGE_INTERVALS = {PAGE: [(a, b) u (c, d) u (e, f)] , PAGE: [(g, h) u (i, j)]}
        
        self._sorted_pages = {}
        
        # create cursor objects
        self.cursor = Cursor(cursor)
        self.select = Cursor(select)
        
        # STATS
        self.word_count = '—'
        self.misspellings = []
    
    def _TYPESET(self, l, i):
        if not l:
            self._glyphs = []
            # which happens if nothing has yet been rendered
            c = 0
            P = self.text[0][1]
            P_i = 0
            F = []
            
            R = 0
            
            PSTYLE = _retrieve_paragraphclass(P, l)
            y = self.channels.channels[c].railings[0][0][1]
        
        else:
            # ylevel is the y position of the first line to print
            # here we are removing the last existing line so we can redraw that one as well
            CURRENTLINE = self._glyphs.pop()
            LASTLINE = self._glyphs[-1]
            
            if LASTLINE['P_BREAK']:
                P = self.text[i][1]
                P_i = i
                F = []

            else:
                P, P_i = LASTLINE['PP']
                F = list(LASTLINE['F'])
            
            PSTYLE = _retrieve_paragraphclass(P, l)
            
            R = CURRENTLINE['R']
            
            c = CURRENTLINE['c']
            y = CURRENTLINE['y'] - PSTYLE['leading']
        
        page = self.channels.channels[c].page
        page_start_l = l
        K_x = None
        
        displacement = PSTYLE['leading']

        while True:
            y += displacement
            
            # see if the lines have overrun the portals
            if y > self.channels.channels[c].railings[1][-1][1] and c < len(self.channels.channels) - 1:
                c += 1
                # jump to new entrance
                y = self.channels.channels[c].railings[0][0][1]
                
                # PAGINATION
                page_new = self.channels.channels[c].page
                if page_new != page:
                    if page not in self._page_intervals:
                        self._page_intervals[page] = [ (page_start_l, l) ]
                        
                    elif type(self._page_intervals[page][-1]) is int:
                        self._page_intervals[page][-1] = (self._page_intervals[page][-1], l)
                        
                    else:
                        self._page_intervals[page].append( (page_start_l, l) )
                    
                    page = page_new
                    page_start_l = l
                #############
                continue

            # calculate indentation

            if R in PSTYLE['indent_range']:
                D, SIGN, K = PSTYLE['indent']
                if K:
                    if K_x is None:
                        INDLINE = _assemble_line(
                            self.text[P_i : P_i + K + 1], 
                            0, 
                            l, 
                            
                            0, 
                            1989, 
                            0, 
                            0, 
                            
                            PSTYLE['collapsible'],
                            PSTYLE['stylemap'],
                            F[:], 
                            
                            hyphenate = False
                            )
                        K_x = INDLINE['GLYPHS'][-1][5] * SIGN
                    
                    L_indent = PSTYLE['margin_left'] + D + K_x
                else:
                    L_indent = PSTYLE['margin_left'] + D
            else:
                L_indent = PSTYLE['margin_left']
            
            R_indent = PSTYLE['margin_right']

            # generate line objects
            LINE = _assemble_line(
                    self.text[i : i + 1989], 
                    i, 
                    l, 
                    
                    self.channels.channels[c].edge(0, y)[0] + L_indent, 
                    self.channels.channels[c].edge(1, y)[0] - R_indent, 
                    y, 
                    PSTYLE['leading'], 
                    
                    PSTYLE['collapsible'],
                    PSTYLE['stylemap'],
                    F, 
                    
                    hyphenate = PSTYLE['hyphenate']
                    )
            # stamp R line number
            LINE['R'] = R
            LINE['PP'] = (P, P_i)
            LINE['c'] = c
            
            # get the index of the last glyph printed so we know where to start next time
            i = LINE['j']
            
            if LINE['P_BREAK']:

                if i > len(self.text) - 1:
                    self._glyphs.append(LINE)
                    # this is the end of the document
                    break
                
                y += PSTYLE['margin_bottom']

                P = self.text[i][1]
                P_i = i
                F = []
                R = 0
                K_x = None
                
                PSTYLE = _retrieve_paragraphclass(P, l)
                
                y += PSTYLE['margin_top']
                
                displacement = PSTYLE['leading']

            else:
                F = list(LINE['F'])
                R += 1
            
            l += 1
            self._glyphs.append(LINE)

        if page not in self._page_intervals:
            self._page_intervals[page] = [ (page_start_l, l + 1) ]
            
        elif type(self._page_intervals[page][-1]) is int:
            self._page_intervals[page][-1] = (self._page_intervals[page][-1], l + 1)
            
        else:
            self._page_intervals[page].append( (page_start_l, l + 1) )


        self._line_startindices = [line['i'] for line in self._glyphs]
        self._line_yl = { cc: list(h[:2] for h in list(g)) for cc, g in groupby( ((LINE['y'], LINE['l'], LINE['c']) for LINE in self._glyphs if LINE['GLYPHS']), key=lambda k: k[2]) }

    def _recalculate(self):
        # clear sorts
        self._sorted_pages = {}
        
        # avoid recalculating lines that weren't affected
        try:
            l = self.index_to_line( min(self.select.cursor, self.cursor.cursor) ) - 1
            
            if l < 0:
                l = 0
            
            self._page_intervals = { page: [I for I in 
                    [ interval if interval[1] <= l else interval[0] if interval[0] <= l else None for interval in intervals]
                    if I is not None] for page, intervals in self._page_intervals.items() if intervals[0][0] < l}    
            
            i = self._glyphs[l]['i']
            self._glyphs = self._glyphs[:l + 1]
            self._TYPESET(l, i)
        except AttributeError:
            self.deep_recalculate()
        
        # tally errors
        errors.styleerrors.update(l)

    def deep_recalculate(self):
        # clear sorts
        self._glyphs = []
        self._sorted_pages = {}
        self._page_intervals = {}
        
        self._TYPESET(0, 0)
        
        # tally errors
        errors.styleerrors.update(0)


    def _target_line(self, x, y, c):
        
        yy, ll = zip( * self._line_yl[c])
        # find the clicked line
        lineindex = None
        if y >= yy[-1]:
            lineindex = len(yy) - 1
        else:
            lineindex = bisect.bisect(yy, y)

        return ll[lineindex]
    
    def target_glyph(self, x, y, l=None, c=None):

        if l is None:
            l = self._target_line(x, y, c)

        # find first glyph to the right of click spot
        glyphindex = bisect.bisect([glyph[1] for glyph in self._glyphs[l]['GLYPHS']], x )
        
        # determine x position of glyph before it
        glyphx = self._glyphs[l]['GLYPHS'][glyphindex - 1][1]
        # if click is closer to it, shift glyph index left one
        try:
            if abs(x - glyphx) < abs(x - self._glyphs[l]['GLYPHS'][glyphindex][1]):
                glyphindex += -1
        except IndexError:
            glyphindex = len(self._glyphs[l]['GLYPHS']) - 1
            
        return glyphindex + self._glyphs[l]['i']

    # get line number given character index
    def index_to_line(self, index):
        return bisect.bisect(self._line_startindices, index) - 1

    def take_selection(self):
        if self.cursor.cursor == self.select.cursor:
            return False
        else:
            self._sort_cursors()

            return self.text[self.cursor.cursor:self.select.cursor]

    def delete(self, start=None, end=None, da=0, db=0):

        self._sort_cursors()

        if start is None:
            start = self.cursor.cursor + da
            
        if end is None:
            end = self.select.cursor + db


        if [character(e) for e in self.text[start:end]] == ['</p>', '<p>']:
            del self.text[start:end]
            
            offset = start - end
        
        else:
            # delete every PAIRED paragraph block
            ptags = [ e for e in self.text[start:end] if character(e) in ('<p>', '</p>') ]
            del self.text[start:end]

            outside = outside_tag(ptags)
            if outside:
                if (outside[0], character(outside[1])) == ('</p>', '<p>'):
                    style = next(c[1] for c in self.text[start::-1] if character(c) == '<p>')
                    if style == outside[1][1]:
                        del outside[0:2]
                        
                self.text[start:start] = outside

            offset = start - end + len(outside)
        
        # fix spelling lines
        self.misspellings = [pair if pair[1] < start else (pair[0] + offset, pair[1] + offset, pair[2]) if pair[0] > end else (0, 0, None) for pair in self.misspellings]

        self._recalculate()
        self.cursor.set_cursor(start, self.text)
        self.select.cursor = self.cursor.cursor

    def insert(self, segment):
        if self.take_selection():
            self.delete(self.cursor.cursor, self.select.cursor)
        
        s = len(segment)
        self.text[self.cursor.cursor:self.cursor.cursor] = segment
        self._recalculate()
        self.cursor.skip(s, self.text)
        self.select.cursor = self.cursor.cursor
        
        # fix spelling lines
        self.misspellings = [pair if pair[1] < self.cursor.cursor else (pair[0] + s, pair[1] + s, pair[2]) if pair[0] > self.cursor.cursor else (pair[0], pair[1] + s, pair[2]) for pair in self.misspellings]
    
    def bridge(self, tag, sign):
        S = self.take_selection()
        if S and '</p>' not in S:
            
            DA = 0
            
            I = self.cursor.cursor
            J = self.select.cursor

            P_1 = I - next(i for i, c in enumerate(self.text[I - 1::-1]) if character(c) == '<p>')
            P_2 = J + self.text[J:].index('</p>') + 1

            if sign:
                CAP = ('</f>', '<f>')
                
                self.text.insert(P_1, (CAP[0], tag))
                DA += 1
                
                P_2 += 1
                I += 1
                J += 1
            else:
                CAP = ('<f>', '</f>')
            
            paragraph = self.text[P_1:P_2]
            
            # if selection falls on top of range
            if character(self.text[I - 1]) == CAP[0]:
                I -= next(i for i, c in enumerate(self.text[I - 2::-1]) if character(c) != CAP[0]) + 1

            if character(self.text[J]) == CAP[1]:
                J += next(i for i, c in enumerate(self.text[J + 1:]) if character(c) != CAP[1]) + 1

            if sign:
                ftags = [(i + P_1, e[0]) for i, e in enumerate(paragraph) if e == (CAP[1], tag) or e == (CAP[0], tag)] + [(P_2, CAP[1])] + [(None, None)]
            else:
                ftags = [(i + P_1, e[0]) for i, e in enumerate(paragraph) if e == (CAP[1], tag) or e == (CAP[0], tag)] + [(None, None)]
            
            pairs = []
            for i in reversed(range(len(ftags) - 2)):
                if (ftags[i][1], ftags[i + 1][1]) == CAP:
                    pairs.append((ftags[i][0], ftags[i + 1][0]))
                    del ftags[i:i + 2]
            
            # ERROR CHECKING
            if ftags != [(None, None)]:
                print ('INVALID TAG SEQUENCE, REMNANTS: ' + str(ftags))
            
            instructions = []
            drift_i = 0
            drift_j = 0

            for pair in pairs:
                if pair[1] <= I or pair[0] >= J:
                    pass
                elif pair[0] >= I and pair[1] <= J:
                    instructions += [(pair[0], False), (pair[1], False)]
                    DA -= 2
                    
                    drift_j += -2
                elif I < pair[1] <= J:
                    instructions += [(pair[1], False), (I, True, (CAP[1], tag) )]
                    if not sign:
                        drift_i += 1
                elif I <= pair[0] < J:
                    instructions += [(pair[0], False), (J, True, (CAP[0], tag) )]
                    if not sign:
                        drift_j += -1
                elif pair[0] < I and pair[1] > J:
                    instructions += [(I, True, (CAP[1], tag) ), (J, True, (CAP[0], tag) )]
                    DA += 2
                    
                    if sign:
                        drift_j += 2
                    else:
                        drift_i += 1
                        drift_j += 1

            if instructions:
                activity = True
                
                instructions.sort(reverse=True)
                for instruction in instructions:
                    if instruction[1]:
                        self.text.insert(instruction[0], instruction[2])
                    else:
                        del self.text[instruction[0]]
            else:
                activity = False
            
            if sign:
                if self.text[P_1] == (CAP[0], tag):
                    del self.text[P_1]
                    DA -= 1
                    
                    drift_i -= 1
                    drift_j -= 1

                else:
                    self.text.insert(P_1, (CAP[1], tag) )
                    DA += 1
                    
                    drift_j += 1

            
            if activity:
                self.cursor.cursor = I + drift_i
                self.select.cursor = J + drift_j
                
                self._recalculate()
                
                # redo spelling for this paragraph
                self.misspellings = [pair if pair[1] < P_1 else
                        (pair[0] + DA, pair[1] + DA, pair[2]) if pair[0] > P_2 else
                        (0, 0, 0) for pair in self.misspellings ]
                # paragraph has changed
                self.misspellings += words(self.text[P_1:P_2 + DA] + ['</p>'], startindex=P_1, spell=True)[1]
                
                return True
            else:
                return False
                
    def _sort_cursors(self):
        if self.cursor.cursor > self.select.cursor:
            self.cursor.cursor, self.select.cursor = self.select.cursor, self.cursor.cursor
    
    def expand_cursors(self):
        # order
        self._sort_cursors()
        
        if character(self.text[self.cursor.cursor - 1]) == '<p>' and character(self.text[self.select.cursor]) == '</p>':
            self.cursor.cursor = 1
            self.select.cursor = len(self.text) - 1
        else:
            self.select.cursor += self.text[self.select.cursor:].index('</p>')
            self.cursor.cursor = self.text_index_location(self.cursor.cursor)[2][1] + 1
    
    def expand_cursors_word(self):

        try:
            # select block of spaces
            if self.text[self.select.cursor] == ' ':
                I = next(i for i, c in enumerate(self.text[self.select.cursor::-1]) if c != ' ') - 1
                self.cursor.cursor -= I
                
                J = next(i for i, c in enumerate(self.text[self.select.cursor:]) if c != ' ')
                self.select.cursor += J
            
            # select block of words
            elif character(self.text[self.select.cursor]) not in _breaking_chars:
                I = next(i for i, c in enumerate(self.text[self.select.cursor::-1]) if character(c) in _breaking_chars) - 1
                self.cursor.cursor -= I
                
                J = next(i for i, c in enumerate(self.text[self.select.cursor:]) if character(c) in _breaking_chars)
                self.select.cursor += J
            
            # select block of punctuation
            else:
                I = next(i for i, c in enumerate(self.text[self.select.cursor::-1]) if character(c) not in _breaking_chars or c == ' ') - 1
                self.cursor.cursor -= I
                
                # there can be only breaking chars at the end (</p>)
                try:
                    J = next(i for i, c in enumerate(self.text[self.select.cursor:]) if character(c) not in _breaking_chars or c == ' ')
                    self.select.cursor += J
                except StopIteration:
                    self.select.cursor = len(self.text) - 1

        except ValueError:
            pass


    ### FUNCTIONS USEFUL FOR DRAWING AND INTERFACE
    
    def line_indices(self, l):
        return self._glyphs[l]['i'], self._glyphs[l]['j']

    # get location of specific glyph
    def text_index_location(self, index, ahead=False):
        l = self.index_to_line(index)
        try:
            glyph = self._glyphs[l]['GLYPHS'][index - self._glyphs[l]['i']]
        except IndexError:
            glyph = self._glyphs[l]['GLYPHS'][-1]
            print ('ahead')
            ahead = True

        return glyph[1:3]

    def stats(self, spell):
        if spell:
            self.word_count, self.misspellings = words(self.text, spell=True)
        else:
            self.word_count = words(self.text)

    def line_data(self, l):
        anchor = self._glyphs[l]['anchor']
        stop = self._glyphs[l]['stop']
        leading = self._glyphs[l]['leading']
        y = self._glyphs[l]['y']
        return anchor, stop, leading, y
    
    def pp_at(self, i):
        return self._glyphs[self.index_to_line(i)]['PP']

    def extract_glyphs(self, refresh=False):

        if refresh:
            self._sorted_pages = {}

        if not self._sorted_pages:

            for page, intervals in self._page_intervals.items():
                sorted_page = {('_annot',): [], ('_images',): [], ('_intervals',): intervals}
                
                for line in chain.from_iterable(self._glyphs[slice( * interval)] for interval in intervals):

                    p_name, p_i = line['PP']
                    hyphen = line['hyphen']
                    
                    for glyph in line['GLYPHS']:
                        
                        if glyph[0] < 0:
                            if glyph[0] == -6:
                                sorted_page[('_annot',)].append( (glyph[0], line['anchor'], line['y'] + line['leading'], p_i, glyph[3]))
                            elif glyph[0] == -13:
                                sorted_page[('_images',)].append( (glyph[6], glyph[1], glyph[2]) )
                            else:
                                sorted_page[('_annot',)].append(glyph[:3] + (p_i, glyph[3]))
                        else:
                            K = glyph[0:3]
                            f = glyph[3]
                            try:
                                sorted_page[f].append(K)
                            except KeyError:
                                sorted_page[f] = [K]

                    if hyphen is not None:
                        try:
                            sorted_page[hyphen[3]].append((hyphen[0:3]))
                        except KeyError:
                            sorted_page[hyphen[3]] = []
                            sorted_page[hyphen[3]].append((hyphen[0:3]))
                
                self._sorted_pages[page] = sorted_page
        return self._sorted_pages
