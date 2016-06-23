import gi
gi.require_version('HarfBuzz', '0.0')

from gi.repository import HarfBuzz as hb

from gi.repository.GLib import Bytes

path = '/home/kelvin/amiri-regular.ttf'

with open(path, 'rb') as fi:
    fontdata = fi.read()

hbfontface = hb.face_create(hb.glib_blob_create(Bytes.new(fontdata)), 0)

from itertools import chain, accumulate
from bisect import bisect
from re import finditer

from meredith.box import Box
from meredith.elements import Reverse, Fontpost, Line_break
from meredith import datablocks

from olivia.languages import directionality
from olivia import Tagcounter


from libraries.pyphen import pyphen

from fonts import breaking_spaces

from edit.wonder import alphabet

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
    n = len(text)
    fontinfo = F, datablocks.BSTYLES.project_t(BLOCK, F)
    
    l = directionality[base]
    runinfo = (base,)
    runinfo_stack = [runinfo]
    RUNS = [(l, False, None, runinfo, fontinfo)]
    
    for j, v in chain((k for k in enumerate(text) if type(k[1]) is not str), ((n, Reverse({})),) ):
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
                    if j < n:
                        RUNS.append((l, False, v, runinfo, fontinfo))
            else:
                RUNS.append((l, False, v, runinfo, fontinfo))
                l += 1
                runinfo = (v['language'],)
                runinfo_stack.append(runinfo)
        else:
            print(type(v))
            if isinstance(v, Fontpost):
                fontinfo = get_font_info(BLOCK, fontinfo[0], v)
            RUNS.append((l, False, v, runinfo, fontinfo))
        i = j + 1
    
    return RUNS

def cast_paragraph(linemaker, BLOCK, base):
    runs = bidir_levels(base, BLOCK.content, BLOCK)
    return runs[0][0], [line.fuse_glyphs() for line in shape_in_pieces(runs, linemaker)]

def _get_glyphs_entire(sequence, font, runinfo):
    HBB = hb.buffer_create()
    cp = list(map(ord, sequence))
    hb.buffer_add_codepoints(HBB, cp, 0, len(cp))
    hb.buffer_guess_segment_properties(HBB)
    hb.shape(font, HBB, [])

    x = 0
    y = 0
    glyphs = []
    for N, P in zip(hb.buffer_get_glyph_infos(HBB), hb.buffer_get_glyph_positions(HBB)):
        gx = x + P.x_offset
        x += P.x_advance
        glyphs.append((N.codepoint, gx, x, y + P.y_offset, N.cluster))
        y += P.y_advance
    
    return int(hb.buffer_get_direction(HBB)) - 4, x, glyphs
    
def shape_right_glyphs(string, glyphs, i, font, runinfo, limit):
    direction, x, glyphs = _get_glyphs_entire(string[i:], font, runinfo)
    
    if limit < x:
        if direction:
            I = bisect([g[1] for g in glyphs], x - limit) - 1
        else:
            I = bisect([g[1] for g in glyphs], limit)
    else:
        I = None
    return glyphs, I
    
def shape_left_glyphs(string, glyphs, start, i, font, runinfo, sep=''):
    substr = string[start:i]
    if sep:
        substr = chain(substr, (sep,))
    
    direction, x, glyphs = _get_glyphs_entire(substr, font, runinfo)
    return glyphs, x

def shape_in_pieces(runs, linemaker):
    LINE = next(linemaker)
    space = LINE['width']
    i = 0
    for l, is_text, V, runinfo, (fstat, FSTYLE) in runs:
        if is_text:
            i_limit = len(V)
            font = hb.font_create(hbfontface)
            hb.font_set_scale(font, FSTYLE['fontsize'], FSTYLE['fontsize'])
            hb.ot_font_set_funcs(font)
            
            i = 0
            r_glyphs = []
            
            while True:
                r_glyphs, I = shape_right_glyphs(V, r_glyphs, i, font, runinfo, space)
                if I is None: # entire line fits
                    LINE.L.append((l, FSTYLE, r_glyphs))
                    space -= r_glyphs[-1][2]
                    break
                    
                else:
                    try:
                        i_over = i + r_glyphs[I + 1][4] - 1
                    except IndexError:
                        i_over = i + len(V) - 1
                    for breakpoint, sep in find_breakpoint(V, i, i_over, True):
                        l_glyphs, x = shape_left_glyphs(V, r_glyphs, i, breakpoint, font, runinfo, sep)
                        if x < space or not sep:
                            if l_glyphs:
                                LINE.L.append((l, FSTYLE, l_glyphs))
                            LINE['fstyle'] = FSTYLE
                            yield LINE
                            LINE = next(linemaker)
                            space = LINE['width']
                            i = breakpoint
                            break
        elif V is not None:
            if isinstance(V, Fontpost):
                LINE.L.append((l, FSTYLE, (-4, 0, 0, 0, i)))
            elif type(V) is Reverse:
                LINE.L.append((l, FSTYLE, (-8, 0, 0, 0, i)))
            else:
                V.layout_inline(LINE, 0, 0, runinfo, fstat, FSTYLE) # reminder to remove x, y parameters later
                LINE.L.append((l, FSTYLE, (-89, 0, V.width, 0, i, V)))
    LINE['fstyle'] = FSTYLE
    yield LINE

class OT_line(dict):
    def __init__(self, * I, ** KI ):
        dict.__init__(self, * I, ** KI )
        self.L = []

    def _rearrange_line(self):
        line = self.L
        line_segments = [k[1:] for k in line]
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
        self._G   =  G  = []
        self._INL = INL = []
        self._IMG = IMG = []
        self._ANO = ANO = []
        dx = 0
        ascent, descent = self['fstyle'].vmetrics()
        for fontstyle, glyphs in segments:
            if type(glyphs) is tuple: # special char
                if glyphs[0] == -89:
                    E = glyphs[5]
                    INL.append((dx, E))
                    if E.ascent > ascent:
                        ascent = E.ascent
                    if E.descent < descent:
                        descent = E.descent
                elif glyphs[0] == -22:
                    IMG.append((dx, glyphs))
                else:
                    ANO.append((dx, glyphs, fontstyle))
                dx += glyphs[2]
            else:
                G.append((dx, fontstyle['hash'], fontstyle, glyphs))
                dx += glyphs[-1][2]
        self['advance'] = dx
        self['ascent'] = ascent
        self['descent'] = descent
        return self
    
    def deposit(self, repository, x=0, y=0):
        x += self['x']
        y += self['y']
        BLOCK = self['BLOCK']
        
        for dx, N, FSTYLE, glyphs in self._G:
            dxx = dx + x
            KK = ((glyph[0], glyph[1] + dxx, glyph[3] + y) for glyph in glyphs)
            try:
                repository[N][1].extend(KK)
            except KeyError:
                repository[N] = (FSTYLE, list(KK))
        
        for dx, inline in self._INL:
            inline.deposit_glyphs(repository, dx + x, y)
        
        repository['_images'].extend((glyph[6], glyph[1] + dx + x, glyph[3] + y) for dx, glyph in self._IMG)
        repository['_annot'].extend((glyph[0], glyph[1] + dx + x, glyph[3] + y, BLOCK, FSTYLE) for dx, glyph, FSTYLE in self._ANO)

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
            font = hb.font_create(hbfontface)
            hb.font_set_scale(font, FSTYLE['fontsize'], FSTYLE['fontsize'])
            hb.ot_font_set_funcs(font)
            
            direction, x, glyphs = _get_glyphs_entire(V, font, runinfo)
            LINE.L.append((l, FSTYLE, glyphs))

        elif V is not None:
            if isinstance(V, Fontpost):
                LINE.L.append((l, FSTYLE, (-4, 0, 0, 0, i)))
            elif type(V) is Reverse:
                LINE.L.append((l, FSTYLE, (-8, 0, 0, 0, i)))
            else:
                V.layout_inline(line, 0, 0, runinfo, fstat, FSTYLE) # reminder to remove x, y parameters later
                LINE.L.append((l, FSTYLE, (-89, 0, V.width, 0, i, V)))
    LINE['fstyle'] = FSTYLE
    return LINE.fuse_glyphs()
