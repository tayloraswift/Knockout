from fonts import hb, SPACES

from itertools import accumulate
from bisect import bisect

from meredith.elements import Reverse, Fontpost, Line_break

from layout.textanalysis import bidir_levels, find_breakpoint

def cast_paragraph(linemaker, BLOCK, base):
    runs = bidir_levels(base, BLOCK.content, BLOCK)
    return runs[0][0], [line.fuse_glyphs(True) for line in cast_multi_line(runs, linemaker)]

def _HB_cast_glyphs(cp, cpstart, a, n, font, factor, runinfo, FSTYLE):
    HBB = hb.buffer_create()
    hb.buffer_add_codepoints(HBB, cp, a - cpstart, n)
    hb.buffer_guess_segment_properties(HBB)
    hb.shape(font, HBB, [])
    x = 0
    y = -FSTYLE['shift']
    tracking = FSTYLE['tracking']
    glyphs = []
    for N, P in zip(hb.buffer_get_glyph_infos(HBB), hb.buffer_get_glyph_positions(HBB)):
        gx = x + P.x_offset*factor
        x += P.x_advance*factor
        glyphs.append((N.codepoint, gx, x, y, N.cluster + cpstart))
        x += tracking
    if glyphs:
        x -= tracking
    return int(hb.buffer_get_direction(HBB)) - 4, x, glyphs
    
def shape_right_glyphs(cp, cpstart, a, b, glyphs, font, factor, runinfo, FSTYLE, limit):
    direction, x, glyphs = _HB_cast_glyphs(cp, cpstart, a, b - a, font, factor, runinfo, FSTYLE)
    if limit < x:
        if direction:
            I = bisect([g[1] for g in glyphs], x - limit)
        else:
            I = bisect([g[1] for g in glyphs], limit)
    else:
        I = None
    return glyphs, I
    
def shape_left_glyphs(cp, cpstart, a, b, glyphs, font, factor, runinfo, FSTYLE, sep=''):
    cp = cp[:b - cpstart]
    if sep:
        cp.append(ord(sep))
        b += 1
    direction, x, glyphs = _HB_cast_glyphs(cp, cpstart, a, b - a, font, factor, runinfo, FSTYLE) # this is the opposite of what it should be, direction should be dictated, not read
    return glyphs, x 

def _yield_line(LINE, i, FSTYLE):
    LINE['fstyle'] = FSTYLE
    LINE['j'] = i
    return LINE

def _next_line(linemaker, i):
    LINE = next(linemaker)
    LINE['i'] = i
    return LINE, LINE['width']

def cast_multi_line(runs, linemaker):
    i = 0
    LINE, space = _next_line(linemaker, i)
    
    newline = False
    R = 0
    RL = len(runs)
    while R < RL:
        l, is_text, V, runinfo, (FSTYLE, * fontinfo ) = runs[R]
        R += 1
        if is_text:
            font, factor, get_emoji = fontinfo
            
            i0 = i
            i_limit = i0 + len(V)
            CP = list(map(ord, V))
            
            r_glyphs = []
            
            while i0 <= i < i_limit:
                if newline:
                    yield _yield_line(LINE, i, FSTYLE)
                    LINE, space = _next_line(linemaker, i)
                    newline = False
                
                r_glyphs, I = shape_right_glyphs(CP, i0, i, i_limit, r_glyphs, font, factor, runinfo, FSTYLE, space)
                if I is None: # entire line fits
                    LINE.add_text(l, FSTYLE, r_glyphs, is_text == 1, get_emoji)
                    space -= r_glyphs[-1][2]
                    i = i_limit
                    break
                    
                else:
                    try:
                        searchlen = r_glyphs[I][4] - i0 - 1
                        if l % 2:
                            searchlen = min(len(V) - 1, searchlen + 2)
                    except IndexError:
                        if l % 2:
                            searchlen = 0
                        else:
                            searchlen = len(V) - 1
                    
                    is_first = not bool(LINE.L)
                    for breakpoint, sep in find_breakpoint(V, i - i0, searchlen, hyphenate=True, is_first=is_first):
                        if not is_first and not breakpoint:
                            # find last run to go back to
                            if is_text == 1:
                                backtrack = len(LINE.L) - 1 - next(r for r in range(len(LINE.L) - 1, -1, -1) if not (type(LINE.L[r][2]) is tuple and (-6 <= LINE.L[r][2][0] <= -4)))
                                if backtrack:
                                    del LINE.L[-backtrack:]
                                    i -= backtrack # only works because each zero width object is one char
                                    R -= 2
                            newline = True
                            break
                        l_glyphs, x = shape_left_glyphs(CP, i0, i, breakpoint + i0, r_glyphs, font, factor, runinfo, FSTYLE, sep)
                        
                        if x < space or not sep:
                            if l_glyphs:
                                LINE.add_text(l, FSTYLE, l_glyphs, is_text == 1, get_emoji)
                            i = breakpoint + i0
                            newline = True # this is necessary because whitespace chars at the end of the line are the only time we are allowed to “borrow” space from the end of the line.
                            break
        elif V is not None:
            fstat, = fontinfo
            if newline:
                yield _yield_line(LINE, i, FSTYLE)
                LINE, space = _next_line(linemaker, i)
                newline = False
            
            tV = type(V)
            if issubclass(tV, Fontpost):
                LINE.L.append((l, FSTYLE, (-5 + tV.countersign, 0, 0, 0, i)))
                i += 1
            elif tV is str:
                O = (SPACES[V], 0, FSTYLE['__spacemetrics__'][SPACES[V]], 0, i)
                while True:
                    if O[2] <= space:
                        LINE.L.append((l, FSTYLE, O))
                        i += 1
                        space -= O[2]
                        break
                    else:
                        yield _yield_line(LINE, i, FSTYLE)
                        LINE, space = _next_line(linemaker, i)
            elif tV is Line_break:
                LINE.L.append((l, FSTYLE, (-9, 0, 0, 0, i)))
                i += 1
                yield _yield_line(LINE, i, FSTYLE)
                LINE, space = _next_line(linemaker, i)
            elif tV is Reverse:
                LINE.L.append((l, FSTYLE, (-6, 0, 0, 0, i)))
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
                        yield _yield_line(LINE, i, FSTYLE)
                        LINE, space = _next_line(linemaker, i)
    
    LINE['fstyle'] = FSTYLE
    LINE['j'] = i + 1
    LINE.L.append((l, FSTYLE, (-3, 0, 0, 0, i))) # final </p> cap
    yield LINE

def cast_mono_line(PARENT, letters, runinfo, F=None, length_only=False):
    BLOCK = PARENT['BLOCK']
    LINE = OT_line({
            'i': 0,
            'j': len(letters),
      
            'leading': PARENT['leading'],
            
            'BLOCK': BLOCK,
            
            'l': PARENT['l'], 
            'c': PARENT['c'], 
            'page': PARENT['page']
            })

    for l, is_text, V, runinfo, (FSTYLE, * fontinfo ) in bidir_levels(runinfo, letters, BLOCK, F):
        if is_text:
            font, factor, get_emoji = fontinfo
            direction, x, glyphs = _HB_cast_glyphs(list(map(ord, V)), 0, 0, len(V), font, factor, runinfo, FSTYLE)
            LINE.add_text(l, FSTYLE, glyphs, is_text == 1, get_emoji)

        elif V is not None:
            fstat, = fontinfo
            tV = type(V)
            if issubclass(tV, Fontpost):
                LINE.L.append((l, FSTYLE, (-5 + tV.countersign, 0, 0, 0, -1)))
            elif tV is str:
                LINE.L.append((l, FSTYLE, (SPACES[V], 0, FSTYLE['__spacemetrics__'][SPACES[V]], 0, -1)))
            elif tV is Line_break:
                LINE.L.append((l, FSTYLE, (-6, 0, 0, 0, -1)))
            elif tV is Reverse:
                LINE.L.append((l, FSTYLE, (-8, 0, 0, 0, -1)))
            else:
                V.layout_inline(LINE, runinfo, fstat, FSTYLE)
                LINE.L.append((l, FSTYLE, (-89, 0, V.width, 0, -1, V)))
    
    LINE['fstyle'] = FSTYLE
    if length_only:
        return LINE.get_length()
    else:
        return LINE.fuse_glyphs()

class OT_line(dict):
    def __init__(self, * I, ** KI ):
        dict.__init__(self, * I, ** KI )
        self.L = []

        self._G   = []
        self._INL = []
        self._IMG = []
        self._ANO = []

    def add_text(self, l, FSTYLE, glyphs, is_not_emoji, get_emoji):
        if is_not_emoji:
            self.L.append((l, FSTYLE, glyphs))
        else:
            fontsize = FSTYLE['fontsize']
            self.L.extend((l, FSTYLE, (-22, 0, x2 - x1, y - fontsize, i, get_emoji(cp))) for cp, x1, x2, y, i in glyphs)
                        
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
    
    def get_length(self):
        return sum(glyphs[2] if type(glyphs) is tuple else glyphs[-1][2] for l, fontstyle, glyphs in self.L)
    
    def fuse_glyphs(self, editable=False):
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
            if type(glyphs) is tuple: # special char (text is lists)
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
        
        _IXF_ = []
        if editable and SEARCH:
            SEARCH.sort()
            i_p = self['i'] - 1
            for i, x, FSTYLE in SEARCH:
                if i - i_p == 1:
                    _IXF_.append((i, x, FSTYLE))
                elif i - i_p > 1:
                    r = i - i_p
                    x_p = _IXF_[-1][1]
                    unitgap = (x - x_p)/r
                    _IXF_.extend((i_p + j + 1, x_p + unitgap*(j + 1), FSTYLE) for j in range(r))
                i_p = i
            del _IXF_[self['j']:]
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
                i = self._ikey[bi - (x2 - x > x - x1)]
            except IndexError:
                i = self._ikey[-1]
        else:
            i = self._ikey[0]
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
        
        repository['_images'].extend((glyph[5], glyph[1] + dx + x, glyph[3] + y) for glyph, dx in self._IMG)
        repository['_annot'].extend((glyph[0], glyph[1] + dx + x, glyph[3] + y, BLOCK, FSTYLE) for glyph, FSTYLE, dx in self._ANO)

    def nail_to(self, x, y, k=None, align=1):
        if k is None:
            k = self['fstyle']['fontsize']*0.3
        if align:
            if align > 0:
                self['x'] = x - k
            else:
                self['x'] = x - self['advance'] + k
        else:
            self['x'] = x - self['advance']*0.5
        self['y'] = y + k
