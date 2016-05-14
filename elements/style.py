from elements.box import Box

from elements.datablocks import Textstyles_D

from style.fonts import get_font

class Textstyles(Box):
    name = 'textstyles'

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        Textstyles_D.update_datablocks(self)

_text_DNA = [('fontsize',    'float',   13),
            ('path',        'str',      'style/Ubuntu-R.ttf'),
            ('tracking',    'float',    0),
            ('shift',       'float',    0),
            ('capitals',    'bool',     False),
            ('color',       'rgba',     (1, 0.15, 0.2, 1))]

class Textstyle(Box):
    name = 'textstyle'

    DNA  = [('name',        'str', 'Untitled fontstyle')] + [A[:2] for A in _text_DNA]
    BASE = {A: D for A, TYPE, D in _text_DNA}

class _Layer(dict):
    def __init__(self, BASE):
        dict.__init__(self, BASE)
        self.Z = {A: None for A in BASE}
        self.Z['class'] = None
        self.members = []
    
    def overlay(self, B):
        for A, V in B.items():
            self[A] = V
            self.Z[A] = B
        self.members.append(B)

class _FLayer(_Layer):
    def vmetrics(self):
        ascent, descent = self['fontmetrics'].vmetrics
        return ascent * self['fontsize'] + self['shift'], descent * self['fontsize'] + self['shift']

class Blockstyles(Box):
    name = 'blockstyles'
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        
        self._block_projections = {}
        self._text_projections = {}
        
        self.update_ts = self._text_projections.clear

    def project_p(self, BLOCK):
        if BLOCK.implicit_ is None:
            P = BLOCK['class']
        else:
            P = BLOCK['class'] + BLOCK.implicit_
        
        H = hash(frozenset(P.items()))
        if len(BLOCK) > 1:
            H += 13 * id(BLOCK)
        
        try:
            return self._block_projections[H]
        except KeyError:
            # iterate through stack
            projection = _Layer(Blockstyle.BASE)
            for B in chain((b for b in self if b['class'] <= P), [BLOCK]):
                projection.overlay(B)
            
            self._block_projections[H] = projection
            return projection

    def project_f(self, BLOCK, F):
        if BLOCK.implicit_ is None:
            P = BLOCK['class']
        else:
            P = BLOCK['class'] + BLOCK.implicit_
        
        H = 22 * hash(frozenset(P.items())) + hash(frozenset(F.items())) # we must give paragraph a different factor if a style has the same name as a fontstyle
        
        try:
            return self._text_projections[H]
        except KeyError:
            # iterate through stack
            projection = _FLayer(Textstyle.BASE)
            for B in (b for b in self if b['class'] <= P):
                for TS in (c['textstyle'] for c in B.content if c['class'] <= F and c['textstyle'] is not None):
                    projection.overlay(TS)
            
            try:
                projection['fontmetrics'], projection['font'] = get_font(projection['path'])
            except ft_errors.FT_Exception:
                path = Textstyle.BASE['path']
                projection['color'] = (1, 0.15, 0.2, 1)
                projection['fontmetrics'], projection['font'] = get_font(path)
            
            projection['hash'] = H
            
            self._text_projections[H] = projection
            return projection

_block_DNA = [('hyphenate',       'bool',   False),
            ('indent',          'binomial', 0),
            ('indent_range',    'int set',  0),
            ('leading',         'float',    22),
            ('margin_bottom',   'float',    0),
            ('margin_left',     'float',    0),
            ('margin_right',    'float',    0),
            ('margin_top',      'float',    0),
            ('align',           'float',    0),
            ('align_to',        'str',      ''),
            
            ('incr_place_value','int',      13),
            ('incr_assign',     'fn',       None),
            ('show_count',      'farray',   None)]

class Blockstyle(Box):
    name = 'blockstyle'
    
    DNA  = [('class',           'blocktc',  'body')] + [A[:2] for A in _block_DNA]
    BASE = {A: D for A, TYPE, D in _block_DNA}

class Memberstyle(Box):
    name = 'memberstyle'
    DNA  = [('class',           'texttc',  ''),
            ('textstyle',       'textstyle', None)]

members = (Textstyles, Textstyle, Blockstyles, Blockstyle, Memberstyle)
