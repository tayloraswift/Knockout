from bisect import bisect
from itertools import chain

from libraries.pyphen import pyphen

from meredith import datablocks
from meredith.elements import PosFontpost, NegFontpost, Line_break

pyphen.language_fallback('en_US')
hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = set((' '))
_BREAK_ONLY_AFTER = set('-')
_BREAK_AFTER_ELSE_BEFORE = set('–—')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE

_BREAK_P = _BREAK | set(('</p>',))

_APOSTROPHES = set("'’")

class Glyphs_line(dict):
    def I(self, x):
        x -= self['x']
        i = bisect(self['_X_'], x)
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
        BLOCK = self['BLOCK']
        
        for glyph in self['GLYPHS']:
            if glyph[0] < 0:
                if glyph[0] == -6:
                    repository['_annot'].append( (glyph[0], glyph[1] + x, glyph[2] + y, BLOCK, glyph[3]))
                elif glyph[0] == -89:
                    glyph[6].deposit_glyphs(repository, x, y)
                else:
                    repository['_annot'].append((glyph[0], glyph[1] + x, glyph[2] + y, BLOCK, glyph[3]))
            else:
                K = (glyph[0], glyph[1] + x, glyph[2] + y)
                N = glyph[3]['hash']
                try:
                    repository[N][1].append(K)
                except KeyError:
                    repository[N] = (glyph[3], [K])

def cast_liquid_line(LINE, letters, startindex, width, leading, BLOCK, F, hyphenate=False):
    LINE['i'] = startindex
    LINE['width'] = width
    LINE['leading'] = leading
    LINE['F'] = F
    LINE['BLOCK'] = BLOCK
    
    # list that contains glyphs
    GLYPHS = []
    glyphappend = GLYPHS.append

    # retrieve font style
    fstat = F.copy()
    FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
    F_advance_width = FSTYLE['fontmetrics'].advance_pixel_width
    F_char_index = FSTYLE['fontmetrics'].character_index
    F_kern = FSTYLE['fontmetrics'].kern
    kern_available = FSTYLE['fontmetrics'].has_kerning
    
    x = 0
    y = -FSTYLE['shift']
    caps = FSTYLE['capitals']
    glyphwidth = 0
    GI = -1
    cap = True

    for letter in letters:
        CT = type(letter)
        if CT is str:
            if caps:
                letter = letter.upper()
            glyphwidth = F_advance_width(letter) * FSTYLE['fontsize']
            # kern
            if GI > 0 and kern_available:
                new_GI = F_char_index(letter)
                kdx, kdy = F_kern(GI, new_GI)
                x += kdx
                y += kdy
                GI = new_GI
            else:
                GI = F_char_index(letter)
            glyphappend((
                    GI,             # 0
                    x,              # 1
                    y,              # 2
                    
                    FSTYLE,         # 3
                    fstat,          # 4
                    x + glyphwidth  # 5
                    ))
        
        elif CT is PosFontpost:            
            # increment tag count
            F += letter['class']
            fstat = F.copy()
            
            FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
            F_advance_width = FSTYLE['fontmetrics'].advance_pixel_width
            F_char_index = FSTYLE['fontmetrics'].character_index
            F_kern = FSTYLE['fontmetrics'].kern
            kern_available = FSTYLE['fontmetrics'].has_kerning
            
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            
            glyphappend((-4, x, y, FSTYLE, fstat, x))
            GI = -4
            continue
            
        elif CT is NegFontpost:
            glyphappend((-5, x, y, FSTYLE, fstat, x))
            
            # increment tag count
            F -= letter['class']
            fstat = F.copy()
            
            FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
            F_advance_width = FSTYLE['fontmetrics'].advance_pixel_width
            F_char_index = FSTYLE['fontmetrics'].character_index
            F_kern = FSTYLE['fontmetrics'].kern
            kern_available = FSTYLE['fontmetrics'].has_kerning
            
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            GI = -5
            continue
        
        elif CT is Line_break:
            glyphappend((-6, x, y, FSTYLE, fstat, x))
            cap = False
            break
        
        else:
            inline = letter.cast_inline(LINE, x, y, BLOCK, F, FSTYLE)
            glyphwidth = inline.width                               #6. object
            glyphappend((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
            GI = -89
        
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
                        i = n - next(i for i, v in enumerate(reversed(LN)) if str(v) in _BREAK)
                
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
                    
                    word = ''.join(c if len(c) == 1 and c.isalpha() else "'" if c in _APOSTROPHES else ' ' for c in letters[i:j])

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
                        HG = GLYPHS[i - 1 + k]
                        HFS = HG[3]
                        h_F = HG[4]
                        
                        if HG[5] + HFS['fontmetrics'].advance_pixel_width('-') * HFS['fontsize'] <= width:
                            i = i + k
                            LINE['observer'] = [(
                                    HFS['fontmetrics'].character_index('-'), 
                                    HG[5], # x
                                    HG[2], # y
                                    HFS,
                                    h_F)]
                            break
                ####################
                if i:
                    del GLYPHS[i:]
            cap = False
            break
            
        else:
            x += FSTYLE['tracking']
    
    LINE['fstyle'] = FSTYLE
    try:
        LINE['F'] = GLYPHS[-1][4]
        LINE['advance'] = GLYPHS[-1][5]
    except IndexError:
        LINE['advance'] = 0
    
    if cap:
        GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
    
    LINE['j'] = startindex + len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    LINE['_X_'] = [g[1] for g in GLYPHS]

def cast_mono_line(PARENT, letters, leading, BLOCK, F):
    F = F.copy()
    LINE = Glyphs_line({
            'i': 0,
      
            'leading': leading,
            
            'F': F,
            'BLOCK': BLOCK,
            
            'observer': [],
            
            'l': PARENT['l'], 
            'c': PARENT['c'], 
            'page': PARENT['page']
            })
    
    # list that contains glyphs
    GLYPHS = []
    glyphappend = GLYPHS.append

    # retrieve font style
    fstat = F.copy()
    FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
    F_advance_width = FSTYLE['fontmetrics'].advance_pixel_width
    F_char_index = FSTYLE['fontmetrics'].character_index
    F_kern = FSTYLE['fontmetrics'].kern
    kern_available = FSTYLE['fontmetrics'].has_kerning

    x = 0
    y = -FSTYLE['shift']
    caps = FSTYLE['capitals']
    glyphwidth = 0
    GI = -1

    for letter in letters:
        CT = type(letter)
        if CT is str:
            if caps:
                letter = letter.upper()
            glyphwidth = F_advance_width(letter) * FSTYLE['fontsize']
            # kern
            if GI > 0 and kern_available:
                new_GI = F_char_index(letter)
                kdx, kdy = F_kern(GI, new_GI)
                x += kdx
                y += kdy
                GI = new_GI
            else:
                GI = F_char_index(letter)
            glyphappend((
                    GI,             # 0
                    x,              # 1
                    y,              # 2
                    
                    FSTYLE,         # 3
                    fstat,          # 4
                    x + glyphwidth  # 5
                    ))
        
        elif CT is PosFontpost:            
            # increment tag count
            F += letter['class']
            fstat = F.copy()
            
            FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
            F_advance_width = FSTYLE['fontmetrics'].advance_pixel_width
            F_char_index = FSTYLE['fontmetrics'].character_index
            F_kern = FSTYLE['fontmetrics'].kern
            kern_available = FSTYLE['fontmetrics'].has_kerning
            
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            
            glyphappend((-4, x, y, FSTYLE, fstat, x))
            GI = -4
            continue
            
        elif CT is NegFontpost:
            glyphappend((-5, x, y, FSTYLE, fstat, x))
            
            # increment tag count
            F -= letter['class']
            fstat = F.copy()
            
            FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
            F_advance_width = FSTYLE['fontmetrics'].advance_pixel_width
            F_char_index = FSTYLE['fontmetrics'].character_index
            F_kern = FSTYLE['fontmetrics'].kern
            kern_available = FSTYLE['fontmetrics'].has_kerning
            
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            GI = -5
            continue
        
        elif CT is Line_break:
            glyphappend((-6, x, y, FSTYLE, fstat, x))
            break
        
        else:
            inline = letter.cast_inline(LINE, x, y, BLOCK, F, FSTYLE)
            glyphwidth = inline.width                               #6. object
            glyphappend((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
            GI = -89
        
        x += glyphwidth + FSTYLE['tracking']
    
    LINE['fstyle'] = FSTYLE
    try:
        LINE['F'] = GLYPHS[-1][4]
        LINE['advance'] = GLYPHS[-1][5]
    except IndexError:
        LINE['advance'] = 0
    
    LINE['j'] = len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    LINE['_X_'] = [g[1] for g in GLYPHS]
        
    return LINE
