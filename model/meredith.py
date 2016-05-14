from elements.box import Box
from elements.style import Blockstyle

class Meredith(Box):
    name = 'body'

class Section(Box):
    name = 'section'
    
#    DNA  = [('repeat',      'int range',    ''),
#            ('outlines',    '',             '')]

class Paragraph_block(Blockstyle):
    name = 'p'
    textfacing = True

members = (Meredith, Section, Paragraph_block)
