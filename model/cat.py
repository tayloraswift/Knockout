import bisect
from itertools import groupby
from bulletholes.counter import TCounter as Counter
from model.wonder import character
from model.george import Swimming_pool
from fonts import styles

from pyphen import pyphen
pyphen.language_fallback('en_US')

hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = set((' '))
_BREAK_ONLY_AFTER = set('-.,/')
_BREAK_AFTER_ELSE_BEFORE = set('–—')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE

_BREAK_P = _BREAK | set(('</p>',))

_APOSTROPHES = set("'’")

class Glyphs_line(dict):
    def I(self, x, y):
        x -= self['x']
        y -= self['y']
        i = bisect.bisect(self['_X_'], x)
        if i:
            try:
                # compare before and after glyphs
                x1, x2 = self['_X_'][i - 1 : i + 1]
                if x2 - x > x - x1:
                    i -= 1
            except ValueError:
                i -= 1
        return i + self['i']

    def deposit(self, repository):
        x = self['x']
        y = self['y']
        PP = self['PP']
        hyphen = self['hyphen']

        if hyphen is not None:
            glyphs = self['GLYPHS'] + [hyphen]
        else:
            glyphs = self['GLYPHS']
        
        for glyph in glyphs:
            if glyph[0] < 0:
                if glyph[0] == -6:
                    repository['_annot'].append( (glyph[0], x, y + self['leading'], PP, glyph[3]))
                elif glyph[0] == -13:
                    repository['_images'].append( (glyph[6], glyph[1] + x, glyph[2] + y) )
                else:
                    repository['_annot'].append((glyph[0], glyph[1] + x, glyph[2] + y) + (PP, glyph[3]))
            else:
                K = (glyph[0], glyph[1] + x, glyph[2] + y)
                N = glyph[3]['hash']
                try:
                    repository[N][1].append(K)
                except KeyError:
                    repository[N] = (glyph[3], [K])

class LContainer(Swimming_pool):
    def __init__(self, SP):
        Swimming_pool.__init__(self, SP.railings, SP.page)
    
    def bounds(self, y):
        return self.edge(0, y)[0], self.edge(1, y)[0]

def typeset_chained(channels, LIQUID, c=0, y=None, LASTLINE = Glyphs_line({'j': 0, 'l': -1, 'P_BREAK': True})):
    SLUGS = []
    rchannels = channels[c:]
    rlen = len(rchannels) - 1
    c_leak = False
    for c_number, channel in enumerate(LContainer(rc) for rc in rchannels):
        i = LASTLINE['j']
        if i >= len(LIQUID):
            break
        if y is None:
            y = channel.railings[0][0][1]
        if c_number == rlen:
            c_leak = True
        SLUGS += typeset_liquid(channel, LIQUID, LASTLINE, i, y, c_number + c, c_leak, root=True)
        y = None
        
        if SLUGS:
            LASTLINE = SLUGS[-1]

    return SLUGS

def typeset_liquid(channel, LIQUID, INIT, i, y, c, c_leak, root=False):
    SLUGS = []
    l = INIT['l'] + 1
    if INIT['P_BREAK']:
        gap = True
    else:
        PP = INIT['PP']
        F = INIT['F'].copy()
        R = INIT['R'] + 1
        K_x = None
        PSTYLE = styles.PARASTYLES.project_p(PP[1])
        gap = False
    
    page = channel.page

    while True:
        if gap:
            try:
                i, container = next((a + i, v) for a, v in enumerate(LIQUID[i:]) if character(v) in {'<p>', '<table>'})
            except StopIteration:
                # end of file
                break
            if container[0] == '<p>':
                PP = container
                _p_i_ = i
                PSTYLE = styles.PARASTYLES.project_p(PP[1])
                
                F = Counter()
                R = 0
                K_x = None
                
                y += PSTYLE['margin_top'] + PSTYLE['leading']

                gap = False

            elif container[0] == '<table>':
                TBL = container
                try:
                    TBL.fill(channel, c, y)
                except RuntimeError:
                    break
                TBL['i'] = i
                TBL['j'] = i + 1
                TBL['l'] = l
                TBL['c'] = c
                TBL['page'] = page
                y = TBL['y']
                
                SLUGS.append(TBL)
                l += 1
                i += 1
                continue
        else:
            y += PSTYLE['leading']
        
        # see if the lines have overrun the portal
        if y > channel.railings[1][-1][1] and not c_leak:
            if not root:
                raise RuntimeError
            break
            
        x1, x2 = channel.bounds(y)

        # calculate indentation

        if R in PSTYLE['indent_range']:
            D, SIGN, K = PSTYLE['indent']
            if K:
                if K_x is None:
                    INDLINE = cast_liquid_line(
                        LIQUID[_p_i_ : _p_i_ + K + 1], 
                        0, 
                        
                        1989, 
                        0,
                        PP[1],
                        F.copy(), 
                        
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
        x1 += L_indent
        x2 -= R_indent
        if x1 > x2:
            x1, x2 = x2, x1
        LINE = cast_liquid_line(
                LIQUID[i : i + 1989], 
                i, 
                
                x2 - x1, 
                PSTYLE['leading'],
                PP[1],
                F.copy(), 
                
                hyphenate = PSTYLE['hyphenate']
                )
        # stamp line data
        LINE['R'] = R # line number (within paragraph)
        LINE['x'] = x1
        LINE['y'] = y
        LINE['l'] = l
        LINE['c'] = c
        LINE['page'] = page
        LINE['PP'] = PP

        l += 1
        SLUGS.append(LINE)

        # get the index of the last glyph printed so we know where to start next time
        i = LINE['j']
        
        if LINE['P_BREAK']:
            y += PSTYLE['margin_bottom']
            gap = True
        else:
            F = LINE['F']
            R += 1

    return SLUGS

def cast_liquid_line(letters, startindex, width, leading, P, F, hyphenate=False):
    LINE = Glyphs_line({
            'i': startindex,
            
            'width': width,           
            'leading': leading,

            'hyphen': None,
            
            'P_BREAK': False,
            'F': F
            })
    
    # list that contains glyphs
    GLYPHS = []
    x = 0
    y = 0

    # retrieve font style
    fstat = F.copy()
    FSTYLE = styles.PARASTYLES.project_f(P, F)

    # blank pegs
    glyphwidth = 0
    gx = 0
    gy = 0
    effective_peg = None
    
    # style brackets
    brackets = {}
    for f, count in F.items():
        for V in [f.name] + f.groups:
            if V not in brackets:
                brackets[V] = [[0, False] for c in range(count)]
            else:
                brackets[V] += [[0, False] for c in range(count)]

    root_for = set()
    front = x

    for letter in letters:
        CHAR = character(letter)

        if CHAR == '<f>':
            T = letter[1]
            TAG = T.name
            
            # increment tag count
            F[T] += 1
            fstat = F.copy()
            
            # calculate pegging
            G = FSTYLE['pegs'].elements
            if T in G:                
                gx, gy = G[T]
                gx = gx * glyphwidth
                gy = gy * leading
                effective_peg = T
                
                y -= gy
                x += gx
            
            elif effective_peg not in G:
                effective_peg = None
            
            if root_for:
                for group in T.groups:
                    if group in root_for:
                        x = brackets[group][-1][0]
                        root_for = set()
            
            # collapsibility
            for V in [TAG] + T.groups:
                if V not in brackets:
                    brackets[V] = [[x, False]]
                else:
                    brackets[V].append([x, False])
            
            FSTYLE = styles.PARASTYLES.project_f(P, F)
            GLYPHS.append((-4, x, y, FSTYLE, fstat, x))
            
        elif CHAR == '</f>':
            T = letter[1]
            TAG = T.name
            
            # increment tag count
            F[T] -= 1
            fstat = F.copy()

            # depeg
            if T is effective_peg:
                y += gy

            for V in [TAG] + T.groups:
                try:
                    if brackets[V][-1][1]:
                        del brackets[V][-1]
                    brackets[V][-1][1] = True
                except (IndexError, KeyError):
                    print('line begins with close tag character')
            root_for.update(set(T.groups))
            
            # calculate pegging
            G = FSTYLE['pegs'].elements
            if TAG in G:
                if front > x:
                    x = front
                else:
                    front = x
            
            FSTYLE = styles.PARASTYLES.project_f(P, F)
            GLYPHS.append((-5, x, y, FSTYLE, fstat, x))
            
        elif CHAR == '<p>':
            if GLYPHS:
                break
            else:
                # we don’t load the style because the outer function takes care of that
                GLYPHS.append((
                        -2,                      # 0
                        x - FSTYLE['fontsize'],  # 1
                        y,                       # 2
                        
                        FSTYLE,                  # 3
                        fstat,                   # 4
                        x - FSTYLE['fontsize']   # 5
                        ))
        
        elif CHAR == '</p>':
            LINE['P_BREAK'] = True
            GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
            break
        
        elif CHAR == '<br>':
            root_for = set()
            GLYPHS.append((-6, x, y, FSTYLE, fstat, x))
            break

        else:
            root_for = set()
            if CHAR == '<image>':
                IMAGE = letter[1]
                glyphwidth = IMAGE[1]
                                                                 # additional fields
                GLYPHS.append((-13, x, y - leading, FSTYLE, fstat, x + glyphwidth, IMAGE))

            else:
                glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(CHAR) * FSTYLE['fontsize']
                GLYPHS.append((
                        FSTYLE['fontmetrics'].character_index(CHAR),    # 0
                        x,                                              # 1
                        y,                                              # 2
                        
                        FSTYLE,                                         # 3
                        fstat,                                          # 4
                        x + glyphwidth                                  # 5
                        ))
            
            x += glyphwidth

            # work out line breaks
            if x > width:
                n = len(GLYPHS)
                if CHAR not in _BREAK_WHITESPACE:

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
                        except TypeError:
                            j = i
                        
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
                            HFS = styles.PARASTYLES.project_f(P, h_F)
                                
                            if GLYPHS[i - 1 + k][5] + HFS['fontmetrics'].advance_pixel_width('-') * HFS['fontsize'] < width:
                                i = i + k

                                LINE['hyphen'] = (
                                        HFS['fontmetrics'].character_index('-'), 
                                        GLYPHS[i - 1][5], # x
                                        GLYPHS[i - 1][2], # y
                                        HFS,
                                        h_F
                                        )
                                break
                    ####################
                    if i:
                        del GLYPHS[i:]

                elif letters[n] == '</p>':
                    continue
                break
                
            else:
                x += FSTYLE['tracking']

    LINE['j'] = startindex + len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    # cache x's
    LINE['_X_'] = [g[1] for g in GLYPHS]
    
    try:
        LINE['F'] = GLYPHS[-1][4]
    except IndexError:
        pass
    
    return LINE
