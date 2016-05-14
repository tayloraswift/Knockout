from elements.box import Box
from elements.style import Blockstyle

class Meredith(Box):
    name = 'body'

class Section(Box):
    name = 'section'
    
    DNA  = [('repeat',      'int set',    ''),
            ('frames',    'frames',     '')]

class Paragraph_block(Blockstyle):
    name = 'p'
    textfacing = True

members = (Meredith, Section, Paragraph_block)
