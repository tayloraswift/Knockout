from elements.box import Box

class Meredith(Box):
    name = 'body'

class Section(Box):
    name = 'section'
    
#    DNA  = [('repeat',      'int range',    ''),
#            ('outlines',    '',             '')]

class Paragraph_block(Box):
    name = 'p'
    textfacing = True
    
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

class Block_style(Paragraph_block):
    name = 'blockstyle'
    textfacing = False

members = (Meredith, Section, Paragraph_block, Block_style)
