from fonts import hb, breaking_spaces

from itertools import chain, accumulate
from bisect import bisect
from re import finditer

from libraries.pyphen import pyphen

from edit.wonder import alphabet

from olivia.languages import directionality
from olivia import Tagcounter

from meredith.elements import Reverse, Fontpost, Line_break
from meredith import datablocks

pyphen.language_fallback('en_US')
hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = set(chain(' ', breaking_spaces))
_BREAK_ONLY_AFTER = set('-')
_BREAK_AFTER_ELSE_BEFORE = set('–—')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE

_APOSTROPHES = set("'’")

def find_breakpoint(string, start, n, hyphenate=False):
    CHAR = string[n]
    if CHAR in _BREAK_WHITESPACE:
        yield n + 1, ''
    else:
        try:
            if CHAR in _BREAK_ONLY_AFTER:
                i = n - 1 - next(i for i, v in enumerate(reversed(string[start:n - 1])) if v in _BREAK)
            elif CHAR in _BREAK_AFTER_ELSE_BEFORE:
                i = n - 1
            else:
                i = n - next(i for i, v in enumerate(reversed(string[start:n])) if v in _BREAK)
        
        except StopIteration:
            i = start
        
        ### AUTO HYPHENATION
        if hyphenate:
            try:
                j = i + next(i for i, v in enumerate(string[i:]) if v in _BREAK)
            except StopIteration:
                j = i + 1989
            except TypeError:
                j = i
            
            word = ''.join(c if c in alphabet else "'" if c in _APOSTROPHES else ' ' for c in string[i:j])

            leading_spaces = j - i - len(word.lstrip(' '))

            for pair in hy.iterate(word.strip(' ')):
                k = len(pair[0]) + leading_spaces
                # no sense checking hyphenations that don’t fit
                if k >= n - i:
                    continue
                # prevent too-short hyphenations
                elif sum(c != ' ' for c in pair[0]) < 2 or sum(c != ' ' for c in pair[1]) < 2:
                    continue
                
                yield i + k, '-'
        
        yield i, ''

def get_font_info(paragraph, F, post):
    F = F.copy()
    if post.countersign:
        F += post['class']
    else:
        F -= post['class']
    return F, datablocks.BSTYLES.project_t(paragraph, F)

def _raise_digits(string):
    ranges = list(chain((0,), * ((i, j) for i, j in (m.span() for m in finditer("[-+]?\d+[\.,]?\d*", string)) if j - i > 1) , (len(string),)))
    if ranges:
        return (string[i:j] for i, j in zip(ranges, ranges[1:]))
    else:
        return string,

def bidir_levels(base, text, BLOCK, F=None):
    if F is None:
        F = Tagcounter()
    else:
        F = F.copy()
    i = 0
    fontinfo = F, datablocks.BSTYLES.project_t(BLOCK, F)
    
    l = directionality[base]
    runinfo = (base,)
    runinfo_stack = [runinfo]
    RUNS = [(l, False, None, runinfo, fontinfo)]
    
    for j, v in chain((k for k in enumerate(text) if type(k[1]) is not str), ((len(text), None),) ):
        if j - i:
            if l % 2:
                RUNS.extend((l + i % 2, True, s, runinfo, fontinfo) for i, s in enumerate(_raise_digits(''.join(text[i:j]))) if s)
            else:
                RUNS.append((l, True, ''.join(text[i:j]), runinfo, fontinfo))
            
        if type(v) is Reverse:
            if v['language'] is None:
                if len(runinfo_stack) > 1:
                    runinfo_stack.pop()
                    runinfo = runinfo_stack[-1]
                    l -= 1
                    RUNS.append((l, False, v, runinfo, fontinfo))
            else:
                RUNS.append((l, False, v, runinfo, fontinfo))
                l += 1
                runinfo = (v['language'],)
                runinfo_stack.append(runinfo)
        elif v is not None:
            if isinstance(v, Fontpost):
                fontinfo = get_font_info(BLOCK, fontinfo[0], v)
            RUNS.append((l, False, v, runinfo, fontinfo))
        i = j + 1
    
    return RUNS

def cast_paragraph(linemaker, BLOCK, base):
    runs = bidir_levels(base, BLOCK.content, BLOCK)
    return runs[0][0], [line.fuse_glyphs() for line in shape_in_pieces(runs, linemaker)]

def _get_glyphs_entire(cp, cpstart, a, n, font, runinfo):
    HBB = hb.buffer_create()
    hb.buffer_add_codepoints(HBB, cp, a - cpstart, n)
    hb.buffer_guess_segment_properties(HBB)
    hb.shape(font, HBB, [])
    x = 0
    y = 0
    glyphs = []
    for N, P in zip(hb.buffer_get_glyph_infos(HBB), hb.buffer_get_glyph_positions(HBB)):
        gx = x + P.x_offset
        x += P.x_advance
        glyphs.append((N.codepoint, gx, x, y + P.y_offset, N.cluster + cpstart))
        y += P.y_advance
    return int(hb.buffer_get_direction(HBB)) - 4, x, glyphs
    
def shape_right_glyphs(cp, cpstart, a, b, glyphs, font, runinfo, limit):
    direction, x, glyphs = _get_glyphs_entire(cp, cpstart, a, b - a, font, runinfo)
    if limit < x:
        if direction:
            I = bisect([g[1] for g in glyphs], x - limit)
        else:
            I = bisect([g[1] for g in glyphs], limit)
    else:
        I = None
    return glyphs, I
    
def shape_left_glyphs(cp, cpstart, a, b, glyphs, font, runinfo, sep=''):
    cp = cp[:b - cpstart]
    if sep:
        cp.append(ord(sep))
        b += 1
    direction, x, glyphs = _get_glyphs_entire(cp, cpstart, a, b - a, font, runinfo) # this is the opposite of what it should be, direction should be dictated, not read
    return glyphs, x 

def shape_in_pieces(runs, linemaker):
    i = 0
    LINE = next(linemaker)
    LINE['i'] = i
    space = LINE['width']
    for l, is_text, V, runinfo, (fstat, FSTYLE) in runs:
        if is_text:
            i0 = i
            i_limit = i0 + len(V)
            CP = list(map(ord, V))
            font = FSTYLE['__hb_font__']
            
            r_glyphs = []
            
            while i < i_limit:
                r_glyphs, I = shape_right_glyphs(CP, i0, i, i_limit, r_glyphs, font, runinfo, space)
                if I is None: # entire line fits
                    LINE.L.append((l, FSTYLE, r_glyphs))
                    space -= r_glyphs[-1][2]
                    i = i_limit
                    break
                    
                else:
                    try:
                        searchlen = r_glyphs[I][4] - i0 - 1
                        if l % 2:
                            searchlen = min(len(V) - 1, searchlen + 2)
                    except IndexError:
                        searchlen = len(V) - 1
                    
                    for breakpoint, sep in find_breakpoint(V, i - i0, searchlen, True):
                        l_glyphs, x = shape_left_glyphs(CP, i0, i, breakpoint + i0, r_glyphs, font, runinfo, sep)
                        
                        if x < space or not sep:
                            if l_glyphs:
                                LINE.L.append((l, FSTYLE, l_glyphs))
                            i = breakpoint + i0
                            LINE['fstyle'] = FSTYLE
                            LINE['j'] = i
                            yield LINE
                            LINE = next(linemaker)
                            LINE['i'] = i
                            space = LINE['width']
                            break
        elif V is not None:
            if isinstance(V, Fontpost):
                LINE.L.append((l, FSTYLE, (-5 + type(V).countersign, 0, 0, 0, i)))
                i += 1
            elif type(V) is Line_break:
                LINE.L.append((l, FSTYLE, (-6, 0, 0, 0, i)))
                i += 1
            elif type(V) is Reverse:
                LINE.L.append((l, FSTYLE, (-8, 0, 0, 0, i)))
                i += 1
            else:
                while True:
                    V.layout_inline(LINE, runinfo, fstat, FSTYLE)
                    if V.width <= space:
                        LINE.L.append((l, FSTYLE, (-89, 0, V.width, 0, i, V)))
                        i += 1
                        space -= V.width
                        break
                    else:
                        LINE['fstyle'] = FSTYLE
                        LINE['j'] = i
                        yield LINE
                        LINE = next(linemaker)
                        LINE['i'] = i
                        space = LINE['width']
    
    LINE['fstyle'] = FSTYLE
    LINE['j'] = i
    yield LINE

class OT_line(dict):
    def __init__(self, * I, ** KI ):
        dict.__init__(self, * I, ** KI )
        self.L = []

        self._G   = []
        self._INL = []
        self._IMG = []
        self._ANO = []
    
    def _rearrange_line(self):
        line = self.L
        line_segments = [(l % 2, * k ) for l, * k in line]
        if len(line) < 1:
            return line_segments
        
        max_bidi_level = max(k[0] for k in line)
        first = line[0][0]
        steps = [[0] if l < first else [] for l in range(max_bidi_level)] # we omit the 0th level
        for i, (l1, l2) in enumerate((k1[0], k2[0]) for k1, k2 in zip(line, line[1:])):
            if l1 != l2:
                if l2 > l1: # step up
                    steps[l2 - 1].append(i + 1)
                else: # step down
                    steps[l1 - 1].append(i + 1)
        
        i_top = len(line)
        last = line[-1][0]
        for level in steps[:last]:
            level.append(i_top)
        if len(steps) > 1: # skip reversals that cancel each other out
            null_list = [0, i_top]
            try:
                change = next(i for i, level in enumerate(steps) if level != null_list)
            except StopIteration:
                change = len(steps)
            change = change - (change % 2)
            if change > 0:
                del steps[:change]
        
        for level in steps: # perform reversals
            jumps = iter(level)
            for a, b in zip(jumps, jumps):
                if b - a > 1:
                    line_segments[a:b] = reversed(line_segments[a:b])
        return line_segments
    
    def fuse_glyphs(self):
        segments = self._rearrange_line()
        G   = self._G
        INL = self._INL
        IMG = self._IMG
        ANO = self._ANO
        SEARCH = []
        dx = 0
        ascent, descent = self['fstyle']['__fontmetrics__']
        
        for direction, fontstyle, glyphs in segments:
            direction += 1
            if type(glyphs) is tuple: # special char
                SEARCH.append((glyphs[4], glyphs[direction] + dx, fontstyle))
                if glyphs[0] == -89:
                    E = glyphs[5]
                    INL.append((E, dx))
                    if E.ascent > ascent:
                        ascent = E.ascent
                    if E.descent < descent:
                        descent = E.descent
                elif glyphs[0] == -22:
                    IMG.append((glyphs, dx))
                else:
                    ANO.append((glyphs, fontstyle, dx))
                dx += glyphs[2]
            else:
                SEARCH.extend((glyph[4], glyph[direction] + dx, fontstyle) for glyph in glyphs)
                G.append((fontstyle['hash'], fontstyle, [(glyph[0], glyph[1] + dx, glyph[3]) for glyph in glyphs]))
                dx += glyphs[-1][2]
        
        self['advance'] = dx
        self['ascent'] = ascent
        self['descent'] = descent
        
        SEARCH.sort()
        
        i_p = self['i'] - 1
        _IXF_ = []
        for i, x, FSTYLE in SEARCH:
            if i - i_p > 1:
                r = i - i_p
                x_p = _IXF_[-1][1]
                unitgap = (x - x_p)/r
                _IXF_.extend((i_p + j + 1, x_p + unitgap*(j + 1), FSTYLE) for j in range(r))
            else:
                _IXF_.append((i, x, FSTYLE))
            i_p = i
        self.X = [k[1] for k in _IXF_]
        self.FS = [k[2] for k in _IXF_]
        IX = sorted(_IXF_, key=lambda k: k[1])
        self._ikey = [k[0] for k in IX]
        self._xkey = [k[1] for k in IX]
        return self
    
    def I(self, x):
        x -= self['x']
        bi = bisect(self._xkey, x)
        
        if bi:
            try:
                # compare before and after glyphs
                x1 = self._xkey[bi - 1]
                x2 = self._xkey[bi]
                if x2 - x > x - x1:
                    i = self._ikey[bi - 1]
                else:
                    i = self._ikey[bi]
            except IndexError:
                i = bi + self['i'] - 1
        else:
            i = bi + self['i']
        return i
    
    def deposit(self, repository, x=0, y=0):
        x += self['x']
        y += self['y']
        BLOCK = self['BLOCK']
        
        for N, FSTYLE, glyphs in self._G:
            KK = ((glyph[0], glyph[1] + x, glyph[2] + y) for glyph in glyphs)
            try:
                repository[N][1].extend(KK)
            except KeyError:
                repository[N] = (FSTYLE, list(KK))
        
        for inline, dx in self._INL:
            inline.deposit_glyphs(repository, dx + x, y)
        
        repository['_images'].extend((glyph[6], glyph[1] + dx + x, glyph[3] + y) for glyph, dx in self._IMG)
        repository['_annot'].extend((glyph[0], glyph[1] + dx + x, glyph[3] + y, BLOCK, FSTYLE) for glyph, FSTYLE, dx in self._ANO)

def cast_mono_line(PARENT, letters, runinfo, F=None):
    BLOCK = PARENT['BLOCK']
    LINE = OT_line({
            'i': 0,
      
            'leading': PARENT['leading'],
            
            'BLOCK': BLOCK,
            
            'l': PARENT['l'], 
            'c': PARENT['c'], 
            'page': PARENT['page']
            })

    for l, is_text, V, runinfo, (fstat, FSTYLE) in bidir_levels(runinfo[0], letters, BLOCK, F):
        if is_text:
            direction, x, glyphs = _get_glyphs_entire(list(map(ord, V)), 0, 0, len(V), FSTYLE['__hb_font__'], runinfo)
            LINE.L.append((l, FSTYLE, glyphs))

        elif V is not None:
            if isinstance(V, Fontpost):
                LINE.L.append((l, FSTYLE, (-4, 0, 0, 0, -1)))
            elif type(V) is Reverse:
                LINE.L.append((l, FSTYLE, (-8, 0, 0, 0, -1)))
            else:
                V.layout_inline(line, 0, 0, runinfo, fstat, FSTYLE) # reminder to remove x, y parameters later
                LINE.L.append((l, FSTYLE, (-89, 0, V.width, 0, -1, V)))
    LINE['fstyle'] = FSTYLE
    return LINE.fuse_glyphs()
