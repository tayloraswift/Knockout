from itertools import chain

from olivia.languages import generate_runinfo

from meredith.box import Box, Datablocks

from fonts import hb, common_features, feature_map, get_ot_font, get_ot_space_metrics, get_emoji_font

_text_DNA = [('fontsize',    'float',   13),
            ('path',        'str',      'fonts/Ubuntu-R.ttf'),
            ('path_emoji',  'str',      'fonts/TwitterColorEmoji-SVGinOT.ttf'),
            ('tracking',    'float',    0),
            ('shift',       'float',    0),
            ('capitals',    'bool',     False),
            ('color',       'rgba',     (1, 0.15, 0.2, 1))]

_text_DNA.extend((feature, 'int', 0) for feature in common_features)

class Textstyle(Box):
    name = 'textstyle'

    DNA  = [('name',        'str', 'Untitled fontstyle')]
    DNA.extend(A[:2] for A in _text_DNA)
    BASE = {A: D for A, TYPE, D in _text_DNA}

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self.isbase = False
    
    def after(self, A):
        if A == 'name':
            self._TSTYLES_D.update_datablocks(self.KT.TSTYLES)
        else:
            self.KT.BSTYLES.text_projections.clear()
            self.KT.BODY.layout_all()
    
    def __str__(self):
        return self['name']

class Textstyles(Datablocks):
    name = 'textstyles'
    contains = Textstyle
    
    defmembername = 'Untitled fontstyle'
    
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self.content.sort(key=lambda k: k['name'])
        self._dblibrary = self._TSTYLES_D
        self._dblibrary.set_funcs(self)

    def after(self, A):
        self.KT.BSTYLES.text_projections.clear()
        self.KT.BODY.layout_all()

class Memberstyle(Box):
    name = 'memberstyle'
    DNA  = [('class',           'texttc',  ''),
            ('textstyle',       'textstyle', None)]
    
    def after(self, A):
        self.KT.BSTYLES.text_projections.clear()
        self.KT.BODY.layout_all()

_block_DNA = [('hyphenate',       'bool'    ,   False),
            ('keep_together',   'bool'      ,   False),
            ('keep_with_next',   'bool'     ,   False),
            ('indent',          'binomial'  ,   (0, 0, 0)),
            ('indent_range',    'int set'   ,   {0}),
            ('leading',         'float'     ,   22),
            ('margin_bottom',   'float'     ,   0),
            ('margin_left',     'float'     ,   0),
            ('margin_right',    'float'     ,   0),
            ('margin_top',      'float'     ,   0),
            ('language',        'str'       ,  'english'),
            ('align',           'float'     ,   0),
            ('align_to',        'str'       ,  ''),
            
            ('incr_place_value','int'       ,  -1),
            ('incr_assign',    ('f', ('n',)),   None),
            ('show_count',     ('f', ('A',)),   None),
            ('counter_space',   'float'     ,   0.5)]

class _Has_tagged_members(Box):
    def content_new(self, active=None, i=None):
        if active is None:
            O = self.__class__.contains({})
        else:
            O = self.__class__.contains({'class': active['class']})
        if i is None:
            self.content.append(O)
        else:
            self.content.insert(i, O)
        return O

class Blockstyle(_Has_tagged_members):
    name = 'blockstyle'
    
    fixed_attrs = {a[0] for a in _block_DNA}
    
    DNA  = [('class',           'blocktc',  'body')] + [A[:2] for A in _block_DNA]
    BASE = {A: D for A, TYPE, D in _block_DNA}
    
    contains = Memberstyle

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        self.isbase = False
    
    def after(self, A):
        self.KT.BSTYLES.block_projections.clear()
        self.KT.BSTYLES.text_projections.clear()
        self.KT.BODY.layout_all()

class _Layer(dict):
    def __init__(self, BASE):
        dict.__init__(self, BASE)
        BASE.isbase = True
        self.Z = {A: BASE for A in BASE}
        self.members = []
    
    def overlay(self, B):
        for A, V in B.items():
            self[A] = V
            self.Z[A] = B
        self.members.append(B)

class Blockstyles(_Has_tagged_members):
    name = 'blockstyles'
    
    contains = Blockstyle
    
    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        
        self.block_projections = {}
        self.text_projections  = {}
        
        self._block_default    = self._cast_default(Blockstyle)
        self._text_default     = self._cast_default(Textstyle)

    def _cast_default(self, cls):
        D = cls.BASE.copy()
        D['class'] = {}
        return cls(self.KT, D)
        
    def after(self, A):
        self.block_projections.clear()
        self.text_projections.clear()
        datablocks.BODY.layout_all()
    
    def project_b(self, BLOCK):
        if BLOCK.implicit_ is None:
            P = BLOCK['class']
        else:
            P = BLOCK['class'] + BLOCK.implicit_
        
        H = hash(frozenset(P.items()))
        if BLOCK.stylehash is not None:
            H += 13 * BLOCK.stylehash
        
        try:
            return self.block_projections[H]
        except KeyError:
            # iterate through stack
            projection = _Layer(self._block_default)
            for B in chain((b for b in self.content if b['class'] <= P), (BLOCK,)):
                projection.overlay(B)
            
            projection['__runinfo__'] = generate_runinfo(projection['language'])
            self.block_projections[H] = projection
            return projection

    def project_t(self, BLOCK, F, CHAR_STYLES):
        if BLOCK.implicit_ is None:
            P = BLOCK['class']
        else:
            P = BLOCK['class'] + BLOCK.implicit_
        
        H = 22 * hash(frozenset(P.items())) + hash(frozenset(F.items())) # we must give paragraph a different factor if a style has the same name as a fontstyle
        if CHAR_STYLES:
            H += 13 * sum(fp.stylehash for fp in CHAR_STYLES)
        
        try:
            return self.text_projections[H]
        except KeyError:
            # iterate through stack
            projection = _Layer(self._text_default)
            iter_blockstyles = (b.content for b in self.content if b.content is not None and b['class'] <= P)
            for TS in chain((c['textstyle'] for c in chain.from_iterable(iter_blockstyles) if c['textstyle'] is not None and c['class'] <= F), CHAR_STYLES):
                projection.overlay(TS)
            
            # text font
            try:
                upem, hb_face, projection['__hb_font__'], projection['font'] = get_ot_font(projection['path'])
            except FileNotFoundError:
                path = Textstyle.BASE['path']
                projection['color'] = (1, 0.15, 0.2, 1)
                upem, hb_face, projection['__hb_font__'], projection['font'] = get_ot_font(path)

            projection['__factor__'] = factor = projection['fontsize']/upem
            hmetrics = hb.font_get_h_extents(projection['__hb_font__'])[1]
            projection['__fontmetrics__'] = hmetrics.ascender*factor + projection['shift'], hmetrics.descender*factor + projection['shift']
            projection['__spacemetrics__'] = get_ot_space_metrics(projection['__hb_font__'], projection['fontsize'], factor)
            
            # emoji font
            try:
                e_upem, projection['__hb_emoji__'], projection['__emoji__'] = get_emoji_font(projection['path_emoji'])
            except FileNotFoundError:
                e_upem, projection['__hb_emoji__'], projection['__emoji__'] = get_emoji_font(Textstyle.BASE['path_emoji'])
            projection['__factor_emoji__'] = projection['fontsize']/e_upem
            ###
            
            # opentype features
            projection['__ot_features__'] = [feature_map[feature][mode == 1] if mode < 2 else feature_map[feature][2][mode] 
                                             for mode, feature in ((projection[feature], feature) for feature in common_features) if mode]
            
            projection['hash'] = H
            
            self.text_projections[H] = projection
            return projection
    
members = (Textstyles, Textstyle, Blockstyles, Blockstyle, Memberstyle)
