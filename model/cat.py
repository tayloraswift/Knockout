import bisect
from itertools import groupby

from libraries.pyphen import pyphen
from bulletholes.counter import TCounter as Counter
from model.george import Swimming_pool
from style import styles
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image

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
    # glyphline is root, index
        return i + self['i']

    def deposit(self, repository, x=0, y=0):
        x += self['x']
        y += self['y']
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
                elif glyph[0] == -89:
                    glyph[6].deposit_glyphs(repository, x, y)
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
        PSTYLE = styles.PARASTYLES.project_p(PP)
        gap = False
    
    page = channel.page

    while True:
        if gap:
            try:
                i, container = next((a + i, v) for a, v in enumerate(LIQUID[i:]) if type(v) not in {str, OpenFontpost, CloseFontpost, Image})
            except StopIteration:
                # end of file
                break
            if type(container) is Paragraph:
                PP = container
                _p_i_ = i
                PSTYLE = styles.PARASTYLES.project_p(PP)
                
                F = Counter()
                R = 0
                K_x = None
                
                if l != INIT['l'] + 1: # prevent accumulating y error
                    y += PSTYLE['margin_top']
                y += PSTYLE['leading']

                gap = False

            else:
                try:
                    MOD = container.fill(channel, c, y)
                except RuntimeError:
                    break
                MOD['i'] = i
                MOD['j'] = i + 1
                MOD['l'] = l
                MOD['c'] = c
                MOD['page'] = page
                y = MOD['y']
                
                SLUGS.append(MOD)
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
                        PP,
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
                PP,
                F.copy(), 
                
                hyphenate = PSTYLE['hyphenate']
                )
        # stamp line data
        LINE['R'] = R # line number (within paragraph)
        LINE['left'] = x1
        if PSTYLE['align'] > 0:
            LINE['x'] = x1
        elif LINE['GLYPHS']:
            rag = LINE['width'] - LINE['GLYPHS'][-1][5]
            if PSTYLE['align']:
                LINE['x'] = x1 + rag
            else:
                LINE['x'] = x1 + rag/2
        else:
            LINE['x'] = x1
        LINE['y'] = y
        LINE['l'] = l
        LINE['c'] = c
        LINE['page'] = page

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

def cast_liquid_line(letters, startindex, width, leading, PP, F, hyphenate=False):
    LINE = Glyphs_line({
            'i': startindex,
            
            'width': width,           
            'leading': leading,

            'hyphen': None,
            
            'P_BREAK': False,
            'F': F,
            'PP': PP
            })
    
    # list that contains glyphs
    GLYPHS = []

    # retrieve font style
    fstat = F.copy()
    FSTYLE = styles.PARASTYLES.project_f(PP, F)
    x = 0
    y = -FSTYLE['shift']
    glyphwidth = 0

    for letter in letters:
        CT = type(letter)
        if CT is OpenFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] += 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            GLYPHS.append((-4, x, y, FSTYLE, fstat, x))
            
        elif CT is CloseFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] -= 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            GLYPHS.append((-5, x, y, FSTYLE, fstat, x))
            
        elif CT is Paragraph:
            if GLYPHS:
                break
            else:
                # we don’t load the style because the outer function takes care of that
                GLYPHS.append((
                        -2,                      # 0
                        x - leading,             # 1
                        y,                       # 2
                        
                        FSTYLE,                  # 3
                        fstat,                   # 4
                        x - leading              # 5
                        ))
        
        elif letter == '</p>':
            LINE['P_BREAK'] = True
            GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
            break
        
        elif letter == '<br/>':
            GLYPHS.append((-6, x, y, FSTYLE, fstat, x))
            break

        else:
            if CT is str:
                glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(letter) * FSTYLE['fontsize']
                GLYPHS.append((
                        FSTYLE['fontmetrics'].character_index(letter),  # 0
                        x,                                              # 1
                        y,                                              # 2
                        
                        FSTYLE,                                         # 3
                        fstat,                                          # 4
                        x + glyphwidth                                  # 5
                        ))
            
            elif CT is Image:
                glyphwidth = letter.width
                                                              # additional fields:  image object | scale ratio
                GLYPHS.append((-13, x, y - leading, FSTYLE, fstat, x + glyphwidth, (letter.image_surface, letter.factor)))

            else:
                try:
                    inline = letter.cast_inline(x, y, leading, PP, F, FSTYLE)
                    glyphwidth = inline.width                               #6. object
                    GLYPHS.append((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
                except AttributeError:
                    glyphwidth = leading
                    GLYPHS.append((-23, x, y, FSTYLE, fstat, x + leading))
            
            x += glyphwidth

            # work out line breaks
            if x > width:
                n = len(GLYPHS)
                CHAR = str(letter)
                if CHAR not in _BREAK_WHITESPACE:

                    LN = letters[:n]

                    try:
                        if CHAR in _BREAK_ONLY_AFTER:
                            i = next(i + 1 for i, v in zip(range(n - 2, 0, -1), reversed(LN[:-1])) if str(v) in _BREAK)
                        elif CHAR in _BREAK_AFTER_ELSE_BEFORE:
                            i = len(LN) - 1
                        else:
                            i = next(i + 1 for i, v in zip(range(n - 1, 0, -1), reversed(LN)) if str(v) in _BREAK)
                    
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
                            HFS = styles.PARASTYLES.project_f(PP, h_F)
                                
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

def cast_mono_line(letters, leading, PP, F):
    LINE = Glyphs_line({
            'i': 0,
      
            'leading': leading,
            
            'F': F,
            'PP': PP
            })
    
    # list that contains glyphs
    GLYPHS = []

    # retrieve font style
    fstat = F.copy()
    FSTYLE = styles.PARASTYLES.project_f(PP, F)
    x = 0
    y = -FSTYLE['shift']
    glyphwidth = 0

    for letter in letters:
        CT = type(letter)
        if CT is OpenFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] += 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            GLYPHS.append((-4, x, y, FSTYLE, fstat, x))
            
        elif CT is CloseFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] -= 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            GLYPHS.append((-5, x, y, FSTYLE, fstat, x))
            
        elif CT is Paragraph:
            GLYPHS.append((
                    -2,                      # 0
                    x - leading,             # 1
                    y,                       # 2
                    
                    FSTYLE,                  # 3
                    fstat,                   # 4
                    x - leading              # 5
                    ))
        
        elif letter == '</p>':
            GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
        
        elif letter == '<br/>':
            GLYPHS.append((-6, x, y, FSTYLE, fstat, x))

        else:
            if CT is str:
                glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(letter) * FSTYLE['fontsize']
                GLYPHS.append((
                        FSTYLE['fontmetrics'].character_index(letter),  # 0
                        x,                                              # 1
                        y,                                              # 2
                        
                        FSTYLE,                                         # 3
                        fstat,                                          # 4
                        x + glyphwidth                                  # 5
                        ))
            
            elif CT is Image:
                glyphwidth = letter.width
                                                              # additional fields:  image object | scale ratio
                GLYPHS.append((-13, x, y - leading, FSTYLE, fstat, x + glyphwidth, (letter.image_surface, letter.factor)))

            else:
                try:
                    inline = letter.cast_inline(x, y, leading, PP, F, FSTYLE)
                    glyphwidth = inline.width                               #6. object
                    GLYPHS.append((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
                except AttributeError:
                    glyphwidth = leading
                    GLYPHS.append((-23, x, y, FSTYLE, fstat, x + leading))
            
            x += glyphwidth + FSTYLE['tracking']

    LINE['j'] = len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    # cache x's
    LINE['_X_'] = [g[1] for g in GLYPHS]
    
    try:
        LINE['F'] = GLYPHS[-1][4]
    except IndexError:
        pass
    
    return LINE
