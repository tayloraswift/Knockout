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

def find_breakpoint(string, start, n, hyphenate=False):
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
        
        yield i, ''

def _raise_digits(string):
    ranges = list(chain((0,), * ((i, j) for i, j in (m.span() for m in finditer("[-+]?\d+[\.,]?\d*", string)) if j - i > 1) , (len(string),)))
    if ranges:
        return (string[i:j] for i, j in zip(ranges, ranges[1:]))
    else:
        return string,

def bidir_levels(runinfo, text, BLOCK, F=None):
    fontproject = datablocks.BSTYLES.project_t
    if F is None:
        F = Tagcounter()
    else:
        F = F.copy()
    i = 0
    fontinfo = F, fontproject(BLOCK, F)
    
    runinfo_stack = [runinfo]
    l = runinfo[0]
    RUNS = [(l, False, None, runinfo, fontinfo)]
    
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
        if K == 1:
            string = ''.join(G)
            if emojijoin and string == '\u200D':
                RUNS.append((l, True, string, runinfo, fontinfo))
                emojijoin += 1
            else:
                emojijoin = False
                if l % 2:
                    RUNS.extend((l + i % 2, True, s, runinfo, fontinfo) for i, s in enumerate(_raise_digits(string)) if s)
                else:
                    RUNS.append((l, True, string, runinfo, fontinfo))
        elif K == 2:
            if emojijoin > 1:
                del RUNS[-(emojijoin - 1):]
                RUNS[-1][2].append('\u200D' * (emojijoin - 1))
                RUNS[-1][2].extend(G)
            else:
                RUNS.append((l, 2, list(G), runinfo, fontinfo))
            emojijoin = True
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
                            RUNS.append((l, False, v, runinfo, fontinfo))
                    else:
                        RUNS.append((l, False, v, runinfo, fontinfo))
                        
                        runinfo = generate_runinfo(v['language'])
                        if runinfo[0] != runinfo_stack[-1][0]:
                            l += 1
                        runinfo_stack.append(runinfo)
                        
                elif v is not None:
                    if isinstance(v, Fontpost):
                        F = fontinfo[0].copy()
                        if v.countersign:
                            F += v['class']
                            fontinfo = F, fontproject(BLOCK, F)
                            RUNS.append((l, False, v, runinfo, fontinfo))
                        else:
                            F -= v['class']
                            RUNS.append((l, False, v, runinfo, fontinfo))
                            fontinfo = F, fontproject(BLOCK, F)
                    else:
                        RUNS.append((l, False, v, runinfo, fontinfo))
    
    return RUNS
