from itertools import chain, groupby
from re import finditer

from libraries.pyphen import pyphen

from fonts import breaking_spaces, SPACES
from edit.wonder import alphabet
from data.emoji.unicode_codes import EMOJIS

from olivia.languages import generate_runinfo
from olivia import Tagcounter

from meredith.elements import Reverse, Fontpost, Line_break

pyphen.language_fallback('en_US')
hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = frozenset(chain(' ', breaking_spaces))
_BREAK_ONLY_AFTER = frozenset('-”)]}>»&')
_BREAK_AFTER_ELSE_BEFORE = frozenset('–—')
_BREAK_ONLY_BEFORE = frozenset('“([{<«')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE | _BREAK_ONLY_BEFORE

_BREAK_BEFORE = _BREAK_AFTER_ELSE_BEFORE | _BREAK_ONLY_BEFORE

_APOSTROPHES = frozenset("'’")

_S_SPACES = frozenset(SPACES)
_EMOJI_SPACES = _S_SPACES | EMOJIS # for shortcircuiting codepoint sorting

def hyphenations(word, i, leading_spaces, max_len):
    for pair in hy.iterate(word.strip(' ')):
        k = len(pair[0]) + leading_spaces
        # no sense checking hyphenations that don’t fit, prevent too-short hyphenations
        if k < max_len and sum(c != ' ' for c in pair[0]) >= 2 and sum(c != ' ' for c in pair[1]) >= 2:
            yield i + k

def find_breakpoint(string, start, n, hyphenate=False):
    CHAR = string[n]
    if CHAR == ' ': # all other breaking spaces are handled at the inline-object level
        yield n + 1, '', True
    else:
        try:
            if CHAR in _BREAK_BEFORE:
                i = n
                i0 = i
            else:
                if CHAR in _BREAK_ONLY_AFTER:
                    i = n - 1 - next(i for i, v in enumerate(reversed(string[start:n - 1])) if v in _BREAK)
                else:
                    i = n - next(i for i, v in enumerate(reversed(string[start:n])) if v in _BREAK)
                
                i0 = i - (string[i - 1] in _BREAK_ONLY_BEFORE)
            
        except StopIteration:
            i = start
            i0 = i
        
        ### AUTO HYPHENATION
        if hyphenate:
            try:
                j = i + next(i for i, v in enumerate(string[i:]) if v in _BREAK)
            except StopIteration:
                j = len(string)
            except TypeError:
                j = i
            
            word = string[i:j]
            reduced_word = ''.join(c if c in alphabet else "'" if c in _APOSTROPHES else ' ' for c in word)
            if sum(c != ' ' for c in reduced_word) >= 4:
                leading_spaces = j - i - len(reduced_word.lstrip(' '))
                max_len = n - i + 1
                min_len = leading_spaces + 2
                pyphen_hyphens = hyphenations(reduced_word, i, leading_spaces, max_len)
                soft_hyphens = (i + k + 1 for k, c in enumerate(word) if c == '\u00AD' and min_len < k < max_len)
                yield from ((h, '-', False) for h in sorted(chain(pyphen_hyphens, soft_hyphens), reverse=True))
        
        if i0 > start:
            yield i0, '', string[i0 - 1] in _BREAK_WHITESPACE
        for i in range(n, start - 1, -1):
            yield i, '', False

def _raise_digits(string):
    ranges = list(chain((0,), * ((i, j) for i, j in (m.span() for m in finditer("[-+]?\d+[\.,]?\d*", string)) if j - i > 1) , (len(string),)))
    if ranges:
        return ((n % 2, k) for n, k in enumerate(zip(ranges, ranges[1:])))
    else:
        return (False, (0, len(string))),

def _get_fontinfo(BLOCK, F, CHAR_STYLES):
    FSTYLE = BLOCK.KT.BSTYLES.project_t(BLOCK, F, CHAR_STYLES)
    
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

numeric_runinfo = generate_runinfo('numeric')
def bidir_levels(runinfo, text, BLOCK, F=None):
    if F is None:
        F = Tagcounter()
    else:
        F = F.copy()
    i = 0
    j = i
    SS = []
    CHAR_STYLES = []
    o_fontinfo, t_fontinfo, e_fontinfo = _get_fontinfo(BLOCK, F, CHAR_STYLES)
    
    
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
                        choose_runinfo = runinfo, numeric_runinfo
                        RUNS.extend([l + flip, True, i + p, i + q, choose_runinfo[flip], t_fontinfo] for flip, (p, q) in _raise_digits(string) if q - p)
                    else:
                        RUNS.append([l, True, i, j, runinfo, t_fontinfo])
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
                    SS.append('\u00A0')
                elif v is not None:
                    if isinstance(v, Fontpost):
                        F = o_fontinfo[1].copy()
                        if v.countersign:
                            F += v['class']
                            if v.stylehash is not None:
                                CHAR_STYLES.append(v)
                            o_fontinfo, t_fontinfo, e_fontinfo = _get_fontinfo(BLOCK, F, CHAR_STYLES)
                            RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                        else:
                            F -= v['class']
                            if v['pop'] > 0:
                                del CHAR_STYLES[-v['pop']:]
                            RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                            o_fontinfo, t_fontinfo, e_fontinfo = _get_fontinfo(BLOCK, F, CHAR_STYLES)
                        SS.append('\u00AD')
                    else:
                        RUNS.append((l, False, i, v, runinfo, o_fontinfo))
                        SS.append('[')
                j += 1
                i = j

    return ''.join(SS), RUNS
