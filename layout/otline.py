from itertools import chain

from fonts import hb, breaking_spaces, SPACES

from bisect import bisect, bisect_left

from meredith.elements import Reverse, Fontpost, Line_break

from layout.textanalysis import bidir_levels, find_breakpoint

def _unpack_hb_buffer(HBB):
    return ((N.cluster, N.codepoint, P.x_advance, P.x_offset) for N, P in zip(hb.buffer_get_glyph_infos(HBB), hb.buffer_get_glyph_positions(HBB)))

def _compose_glyphs(G, factor, vshift, tracking):
    x = 0
    y = -vshift
    glyphs = []
    for cluster, codepoint, x_advance, x_offset in G:
        gx = x + x_offset*factor
        x += x_advance*factor
        glyphs.append((codepoint, gx, x, y, cluster))
        x += tracking
    if glyphs:
        x -= tracking
    return glyphs, x

class _Glyph_template(object):
    def __init__(self, cp, a, b, runinfo, fontinfo):
        self._cp      = cp
        self._font    = font = fontinfo[1]
        self._compose = fontinfo[2], fontinfo[0]['shift'], fontinfo[0]['tracking']
        self._HBB     = hb.buffer_create()
        self._runinfo = runinfo
        self._d       = runinfo[0]
        self._glyphs = list(self._reshape(cp, a, b))
        if self._d:
            self._logical_glyphs = list(reversed(self._glyphs))
        else:
            self._logical_glyphs = self._glyphs
        self._present = [G[0] for G in self._logical_glyphs]
        self._present.append(b)
        
        self._RIGHT_CACHE = {a: (self._logical_glyphs, 0, 0)}
        
    def _reshape(self, cp, a, b):
        hb.buffer_clear_contents(self._HBB)
        hb.buffer_set_direction(self._HBB, self._runinfo[1])
        hb.buffer_set_script(self._HBB, self._runinfo[2])
        hb.buffer_add_codepoints(self._HBB, cp, a, b - a)
        hb.shape(self._font, self._HBB, [])
        return _unpack_hb_buffer(self._HBB)

    def _slice_glyphs_right(self, a):
        gp = bisect_left(self._present, a)
        p  = self._present[gp]
        
        if a == p:
            if not gp:
                return self._glyphs
            else:
                glyphs = self._logical_glyphs[gp:]
                self._RIGHT_CACHE[a] = glyphs, gp, gp

        else:
            k = self._present[gp + 1]
            glyphs = [G for G in self._reshape(self._cp, a, k) if G[0] < p]
            reshaped_len = len(glyphs)
            glyphs += self._logical_glyphs[gp:]
            self._RIGHT_CACHE[a] = glyphs, gp, gp - reshaped_len
        if self._d:
            glyphs = reversed(glyphs)
        return glyphs

    def _slice_glyphs_left(self, cp, a, b, b2):
        subglyphs_right, right_safe, right_start = self._RIGHT_CACHE[a]
        gq = bisect(self._present, b) - 2 # floors it
        if gq > right_safe:
            q  = self._present[gq]
            glyphs = subglyphs_right[:gq - right_start]
            if self._d:
                glyphs = reversed(glyphs)
            if b2 != q:
                reshaped = self._reshape(cp, q, b2)
                if self._d:
                    glyphs = chain(reshaped, glyphs)
                else:
                    glyphs = chain(glyphs, reshaped)
            return glyphs
        else:
            return self._reshape(cp, a, b2)
    
    def seg_right(self, a, limit):
        glyphs, x = _compose_glyphs(self._slice_glyphs_right(a), * self._compose )
        if limit < x:
            if self._d:
                I = bisect([g[1] for g in glyphs], x - limit)
            else:
                I = bisect([g[1] for g in glyphs], limit)
        else:
            I = None
        return glyphs, I
    
    def seg_left(self, a, b, sep=''):
        if sep:
            cp = self._cp[:b]
            cp.append(ord(sep))
            b2 = b + 1
        else:
            cp = self._cp
            b2 = b
        return _compose_glyphs(self._slice_glyphs_left(cp, a, b, b2), * self._compose )

def _HB_cast_glyphs(cp, a, b, font, factor, runinfo, FSTYLE):
    HBB = hb.buffer_create()
    hb.buffer_add_codepoints(HBB, cp, a, b - a)
    hb.buffer_set_direction(HBB, runinfo[1])
    hb.buffer_set_script(HBB, runinfo[2])
    hb.shape(font, HBB, [])
    return _compose_glyphs(_unpack_hb_buffer(HBB), factor, FSTYLE['shift'], FSTYLE['tracking'])

def _return_line(LINE, i, FSTYLE, R):
    LINE['fstyle'] = FSTYLE
    LINE['j'] = i
    return R - 1

def _return_cap_line(LINE, i, FSTYLE, l):
    LINE['fstyle'] = FSTYLE
    LINE.L.append((l, FSTYLE, (-3, 0, 0, 0, i))) # final </p> cap
    LINE['j'] = i + 1
    return None

def cast_liquid_line(LINE, R, RUNS, totalstring, totalcp, hyphenate):
    space = LINE['width']
    i_c = LINE['i']
    RL = len(RUNS)
    while R < RL:
        l, is_text, i, V, runinfo, (FSTYLE, * fontinfo ), * GT = RUNS[R]
        R += 1
        if is_text:
            i_c = max(i, i_c)
            j = V
            get_emoji = fontinfo[2]
            
            glyphs, I = GT[0].seg_right(i_c, space)
            if I is None: # fits
                LINE.add_text(l, FSTYLE, glyphs, is_text == 1, get_emoji)
                space -= glyphs[-1][2]
            
            else:
                try:
                    overrun = glyphs[I][4] - 1
                    if l % 2:
                        overrun = min(j - 1, overrun + 2)
                except IndexError:
                    if l % 2:
                        overrun = i_c
                    else:
                        overrun = j - 1
                break

        elif V is not None:
            tV = type(V)
            if tV is str:
                O = (SPACES[V], 0, FSTYLE['__spacemetrics__'][SPACES[V]], 0, i)
                LINE.L.append((l, FSTYLE, O))
                if O[2] <= space:
                    space -= O[2]
                elif V in breaking_spaces:
                    if R < RL:
                        return _return_line(LINE, i + 1, FSTYLE, R + 1)
                else:
                    i_c = i
                    overrun = i
                    j = i + 1
                    R += 1
                    break
            
            elif tV is Line_break:
                LINE.L.append((l, FSTYLE, (-9, 0, 0, 0, i)))
                if R < RL:
                    return _return_line(LINE, i + 1, FSTYLE, R + 1)

            elif issubclass(tV, Fontpost):
                LINE.L.append((l, FSTYLE, (-5 + tV.countersign, 0, 0, 0, i)))
            elif tV is Reverse:
                LINE.L.append((l, FSTYLE, (-6, 0, 0, 0, i)))
            
            else:                            # fstat
                V.layout_inline(LINE, runinfo, fontinfo[0], FSTYLE)
                if V.width <= space:
                    LINE.L.append((l, FSTYLE, (-89, 0, V.width, 0, i, V)))
                    space -= V.width
                else:
                    return _return_line(LINE, i, FSTYLE, R)
    
    else:
        return _return_cap_line(LINE, len(totalstring), FSTYLE, l)
    
    is_first = not bool(LINE.L)
    for breakpoint, sep, is_whitespace in find_breakpoint(totalstring, LINE['i'], overrun, hyphenate=hyphenate):
        if breakpoint <= i_c:
            if is_first:
                return _return_line(LINE, breakpoint, FSTYLE, R)
            else:
                R -= 1
                bR = next(r for r in range(R - 1, R - len(LINE.L) - 1, -1) if breakpoint > RUNS[r][2])
                backtrack = R - bR
                if backtrack > 1:
                    del LINE.L[-backtrack + 1:]
                cracked_run = LINE.L.pop()
                glyphs = cracked_run[2]
                space = LINE['width'] - LINE.get_length()
                l, is_text, i, V, runinfo, (FSTYLE, * fontinfo ), * GT = RUNS[bR]
                R = bR + 1
                if is_text:
                    i_c = max(i, LINE['i'])
                    j = V
                    get_emoji = fontinfo[2]
                else: # we know that the None only occurs on run 0
                    LINE.L.append(cracked_run)
                    space -= cracked_run[2][2]
                    i += 1
                    R += 1
                    # find font and factor
                    try:
                        hR = next(run for run in RUNS[bR - 1:0:-1] if run[1] == 1)
                        hruninfo = hR[4]
                        hFSTYLE, hfont, hfactor, _ = hR[5]
                    except StopIteration:
                        break
                    if sep:
                        sep_cp = totalcp[:breakpoint]
                        sep_cp.append(ord(sep))
                        seperator, sep_x = _HB_cast_glyphs(sep_cp, breakpoint, breakpoint + 1, hfont, hfactor, hruninfo, hFSTYLE)
                        if sep_x < space:
                            LINE.add_text(l, FSTYLE, seperator, True, None)
                        else:
                            continue
                    break
        
        if breakpoint == j:
            LINE.add_text(l, FSTYLE, glyphs, is_text == 1, get_emoji)
            if R < RL:
                return _return_line(LINE, breakpoint, FSTYLE, R + 1) # the overrun is a whitespace char
            else:
                return _return_cap_line(LINE, len(totalstring), FSTYLE, l)
        
        l_glyphs, x = GT[0].seg_left(i_c, breakpoint, sep)
        if x < space or is_whitespace:
            if l_glyphs:
                LINE.add_text(l, FSTYLE, l_glyphs, is_text == 1, get_emoji)
            i = breakpoint
            break
    
    return _return_line(LINE, i, FSTYLE, R)

def cast_multi_line(totalstring, RUNS, linemaker, hyphenate):
    i = 0
    R = 0
    totalcp = list(map(ord, totalstring))

    # l, is_text, i, V, runinfo, fontinfo
    for RUN in RUNS:
        if type(RUN) is list:
            RUN.append(_Glyph_template(totalcp, RUN[2], RUN[3], RUN[4], RUN[5]))
    
    while R is not None:
        LINE = next(linemaker)
        LINE['i'] = i
        R = cast_liquid_line(LINE, R, RUNS, totalstring, totalcp, hyphenate)
        i = LINE['j']
        yield LINE

def _align_left(LINES, * I ):
    for LINE in LINES:
        LINE['x'] = LINE['start']
        yield LINE
        
def _align_other(LINES, align, * I ):
    for LINE in LINES:
        rag = LINE['width'] - LINE['advance']
        LINE['x'] = LINE['start'] + rag * align
        yield LINE

def _align_to(LINES, align, align_chars, totalstring):
    for LINE in LINES:
        if LINE['j'] - LINE['i']:
            searchtext = totalstring[LINE['i'] : LINE['j']]
            ai = -1
            for aligner in align_chars:
                try:
                    ai = searchtext.index(aligner)
                    break
                except ValueError:
                    continue
            anchor = LINE['start'] + LINE['width'] * align
            LINE['x'] = anchor - LINE.X[ai]
        else:
            LINE['x'] = LINE['start']
        yield LINE
        
def cast_paragraph(linemaker, BLOCK, runinfo, hyphenate, align, align_chars):
    totalstring, RUNS = bidir_levels(runinfo, BLOCK.content, BLOCK)
    if runinfo[0]:
        align = 1 - align
    if align_chars:
        align_func = _align_to
    elif align:
        align_func = _align_other
    else:
        align_func = _align_left
    return align_func((line.fuse_glyphs(True) for line in cast_multi_line(totalstring, RUNS, linemaker, hyphenate)), 
                      align, align_chars, totalstring)

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
    totalstring, RUNS = bidir_levels(runinfo, letters, BLOCK, F)
    totalcp = list(map(ord, totalstring))
    for l, is_text, i, V, runinfo, (FSTYLE, * fontinfo ) in RUNS:
        if is_text:
            font, factor, get_emoji = fontinfo
            glyphs, x = _HB_cast_glyphs(totalcp, i, V, font, factor, runinfo, FSTYLE)
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
            self.L.append((l, FSTYLE, [(-22, x1, x2, y - fontsize, i, get_emoji(cp)) for cp, x1, x2, y, i in glyphs]))
        
    def _rearrange_line(self):
        line = self.L
        line_segments = [(l % 2, * k ) for l, * k in line]
        if len(line) > 1:
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
            
            for level in reversed(steps): # perform reversals
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
                if glyphs[0][0] == -22:
                    IMG.extend(((cp, 0, x2 - x1, * O ), dx + x1) for cp, x1, x2, * O in glyphs)
                else:
                    G.append((fontstyle['hash'], fontstyle, [(glyph[0], glyph[1] + dx, glyph[3]) for glyph in glyphs]))
                dx += glyphs[-1][2]
        
        self['advance'] = dx
        self['ascent'] = ascent
        self['descent'] = descent
        
        self.IXF = IXF = []
        if editable and SEARCH:
            SEARCH.sort()
            i_p = self['i'] - 1
            for i, x, FSTYLE in SEARCH:
                if i - i_p == 1:
                    IXF.append((i, x, FSTYLE))
                elif i - i_p > 1:
                    x_p = IXF[-1][1]
                    unitgap = (x - x_p)/(i - i_p)
                    IXF.extend((i_p + j + 1, x_p + unitgap*(j + 1), FSTYLE) for j in range(i - i_p))
                i_p = i
            del IXF[self['j']:]
        self.X = [k[1] for k in IXF]
        self._IX = sorted(IXF, key=lambda k: k[1])
        self._xkey = [k[1] for k in self._IX]
        return self
    
    def I(self, x):
        if self._IX:
            x -= self['x']
            bi = bisect(self._xkey, x)
            if bi:
                try:
                    # compare before and after glyphs
                    x1 = self._xkey[bi - 1]
                    x2 = self._xkey[bi]
                    i = self._IX[bi - (x2 - x > x - x1)][0]
                except IndexError:
                    i = self._IX[-1][0]
            else:
                i = self._IX[0][0]
            if i >= self['j']:
                i = self['j'] - 1
        else:
            i = self['i']
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
