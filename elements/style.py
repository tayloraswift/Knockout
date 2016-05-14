from elements.box import Box

from elements.datablocks import Textstyles_D

class Textstyles(Box):
    name = 'textstyles'

    def __init__(self, * II, ** KII ):
        Box.__init__(self, * II, ** KII )
        Textstyles_D.update_datablocks(self)
    
class Textstyle(Box):
    name = 'textstyle'

    DNA  = [('name',        'str', 'Untitled fontstyle'),
            
            ('fontsize',    'float'),
            ('path',        'str'),
            ('tracking',    'float'),
            ('shift',       'float'),
            ('capitals',    'bool'),
            ('color',       'rgba')]

class Blockstyles(Box):
    name = 'blockstyles'

class Blockstyle(Box):
    name = 'blockstyle'
    textfacing = False
    
    DNA  = [('class',           'paracounter',  'body'),
    
            ('hyphenate',       'bool'),
            ('indent',          'binomial'),
            ('indent_range',    'int set'),
            ('leading',         'float'),
            ('margin_bottom',   'float'),
            ('margin_left',     'float'),
            ('margin_right',    'float'),
            ('margin_top',      'float'),
            ('align',           'float'),
            ('align_to',        'str'),
            
            ('incr_place_value','int'),
            ('incr_assign',     'fn'),
            ('show_count',      'farray')]

members = (Textstyles, Textstyle, Blockstyles, Blockstyle)
