from itertools import chain, groupby
from re import finditer

from libraries.pyphen import pyphen

from fonts import breaking_spaces, SPACES
from edit.wonder import alphabet
from data.emoji.unicode_codes import EMOJIS

from olivia.languages import generate_runinfo
from olivia import Tagcounter

from meredith.elements import Reverse, Fontpost, Line_break
from meredith import datablocks

pyphen.language_fallback('en_US')
hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = frozenset(chain(' ', breaking_spaces))
_BREAK_ONLY_AFTER = frozenset('-')
_BREAK_AFTER_ELSE_BEFORE = frozenset('–—')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE

_APOSTROPHES = frozenset("'’")

_S_SPACES = frozenset(SPACES)
_EMOJI_SPACES = _S_SPACES | EMOJIS # for shortcircuiting codepoint sorting

def find_breakpoint(string, start, n, hyphenate=False, is_first=False):
    CHAR = string[n]
    if CHAR in _BREAK_WHITESPACE:
        yield n + 1, ''
    else:
        try:
            if CHAR in _BREAK_ONLY_AFTER:
                i = n - 1 - next(i for i, v in enumerate(reversed(string[start:n - 1])) if v in _BREAK)
            elif CHAR in _BREAK_AFTER_ELSE_BEFORE:
                i = n
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
        
        if is_first:
            for i in range(n, start - 1, -1):
                yield i, ''
        else:
            yield i, ''

def _raise_digits(string):
    ranges = list(chain((0,), * ((i, j) for i, j in (m.span() for m in finditer("[-+]?\d+[\.,]?\d*", string)) if j - i > 1) , (len(string),)))
    if ranges:
        return zip(ranges, ranges[1:])
    else:
        return (0, len(string)),

def _get_fontinfo(BLOCK, F):
    FSTYLE = datablocks.BSTYLES.project_t(BLOCK, F)
    
    t_font = FSTYLE['__hb_font__']
    t_factor = FSTYLE['__factor__']
    
    e_font = FSTYLE['__hb_emoji__']
    e_factor = FSTYLE['__factor_emoji__']
    
    emojifont = FSTYLE['__emoji__']
    fontsize = FSTYLE['fontsize']
    def get_emoji(glyph_index):
        return emojifont.generate_paint_function(glyph_index, fontsize, e_factor)
    #      nontextual |              text               |               emoji
    return (FSTYLE, F), (FSTYLE, t_font, t_factor, None), (FSTYLE, e_font, e_factor, get_emoji)

def bidir_levels(runinfo, text, BLOCK, F=None):
    if F is None:
        F = Tagcounter()
    else:
        F = F.copy()
    i = 0
    j = i
    SS = []
    o_fontinfo, t_fontinfo, e_fontinfo = _get_fontinfo(BLOCK, F)
    
    runinfo_stack = [runinfo]
    l = runinfo[0]
    RUNS = [(l, False, i, None, runinfo, o_fontinfo)]
    
    SP = _S_SPACES
    EMSP = _EMOJI_SPACES
    def sorting(k):
        if type(k) is str:
            if k in EMSP:
                if k in SP:
                    return 0
                else:
                    return 2
            else:
                return 1
        else:
            return -1
    
    emojijoin = False
    for K, G in groupby(text, key=sorting):
        if K >= 0:
            string = ''.join(G)
            j += len(string)
            if K == 1:
                if emojijoin and string == '\u200D':
                    RUNS.append((l, True, i, j, runinfo, t_fontinfo))
                    emojijoin += 1
                else:
                    emojijoin = False
                    if t_fontinfo[0]['capitals']:
                        string = string.upper()
                    if l % 2:
                        RUNS.extend((l + n % 2, True, i + p, i + q, runinfo, t_fontinfo) for n, (p, q) in enumerate(_raise_digits(string)) if q - p)
                    else:
                        RUNS.append((l, True, i, j, runinfo, t_fontinfo))
            elif K == 2:
                if emojijoin > 1:
                    del RUNS[-(emojijoin - 1):]
                    RUNS[-1][3] = j
                else:
                    RUNS.append([l, 2, i, j, runinfo, e_fontinfo])
                emojijoin = True
            else:
                emojijoin = False
                RUNS.extend((l, False, i + ii, sp, runinfo, o_fontinfo) for ii, sp in enumerate(string))
            i = j
            SS.append(string)
        else:
            emojijoin = False
            for v in G:
                if type(v) is Reverse:
                    if v['language'] is None:
                        if len(runinfo_stack) > 1:
                            old_runinfo = runinfo_stack.pop()
                            runinfo = runinfo_stack[-1]
                            if old_runinfo[0] != runinfo[0]:
                                l -= 1
                            RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                    else:
                        RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                        
                        runinfo = generate_runinfo(v['language'])
                        if runinfo[0] != runinfo_stack[-1][0]:
                            l += 1
                        runinfo_stack.append(runinfo)
                
                elif v is not None:
                    if isinstance(v, Fontpost):
                        F = o_fontinfo[1].copy()
                        if v.countersign:
                            F += v['class']
                            o_fontinfo, t_fontinfo, e_fontinfo = _get_fontinfo(BLOCK, F)
                            RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                        else:
                            F -= v['class']
                            RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                            o_fontinfo, t_fontinfo, e_fontinfo = _get_fontinfo(BLOCK, F)
                    else:
                        RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                if type(v) is str:
                    SS.append(v)
                else:
                    SS.append('\u00A0')
                j += 1
                i = j

    return ''.join(SS), RUNS
