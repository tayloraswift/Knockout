import os

from libraries import freetype

from fonts import fontloader

_type_registry = {}

def get_font(path, overwrite=False):
    if path not in _type_registry or overwrite:
        # check if is sfd or binary
        fontname, ext = os.path.splitext(path)
        if ext == '.sfd':
            print('Warning: implicit OTF build triggered')
            os.system('fontforge -script IO/sfd2otf.pe ' + path)
            #raise freetype.ft_errors.FT_Exception('SFD not supported')
            filepath = fontname + '.otf'
        else:
            filepath = path
        FT_font = Memo_font(filepath)
        CR_font = fontloader.create_cairo_font_face_for_file(filepath)
        _type_registry[path] = FT_font, CR_font
        
    return _type_registry[path]

spaces = {
            '\t': -7,
            '\u00A0': -30, # nbsp
            '\u2003': -31, # em
            '\u2002': -32, # en
            '\u2004': -33, # 1/3
            '\u2005': -34, # 1/4
            '\u2006': -35, # 1/6
            '\u2007': -36, # figure
            '\u2008': -37, # punctuation
            '\u2009': -38, # thin
            '\u200A': -39, # hair
            '\u202F': -40, # narrow nbsp
            '\u205F': -41, # math med
            
            }

# extended fontface class
class Memo_font(freetype.Face):
    
    def __init__(self, path):
        freetype.Face.__init__(self, path)
        UPM = self.units_per_EM
        self._kerning = {}
        self._ordinals = spaces.copy()
                # '<p>':        -2
                # '</p>':       -3
                # '<f>':        -4
                # '</f>':       -5
                # '<br/>':      -6
                # '<image/>':   -13
                # '<mod:/>':    -89
                
                # 'ERROR':      -23
        spacemap = {o: c for c, o in self._ordinals.items()}
        space = self.get_advance(self.character_index(' '), True)/UPM
        fig = self.get_advance(self.character_index('0'), True)/UPM
        punc = self.get_advance(self.character_index(','), True)/UPM
        self._widths = {
                None: 0,
                ' ': space,
                '\t': 0,
                '\u00A0': space,
                '\u2003': 1, # em
                '\u2002': 0.5, # en
                '\u2004': 1/3, # 1/3
                '\u2005': 0.25, # 1/4
                '\u2006': 1/6, # 1/6
                '\u2007': fig, # figure
                '\u2008': punc, # punctuation
                '\u2009': 0.2, # thin
                '\u200A': 0.1, # hair
                '\u202F': 0.2, # narrow nbsp
                '\u205F': 4/18, # math med
                }

        self.spacenames = {
                -30: 'nb', # nbsp
                -31: 'em', # em
                -32: 'en', # en
                -33: '1/3', # 1/3
                -34: '1/4', # 1/4
                -35: '1/6', # 1/6
                -36: 'fig', # figure
                -37: 'pn', # punctuation
                -38: '1/5', # thin
                -39: 'h', # hair
                -40: 'nnb', # narrow nbsp
                -41: 'mt', # math med
                }
        self.spacewidths = {c: self._widths[spacemap[c]] for c in range(-41, -29)}
        
        self.vmetrics = self.ascender / UPM, self.descender / UPM
    
    def advance_pixel_width(self, character):
        try:
            return self._widths[character]
        except KeyError:
            p = self.get_advance(self.character_index(character), True)/self.units_per_EM
            self._widths[character] = p
            return p
    
    def character_index(self, character):
        try:
            return self._ordinals[character]
        except KeyError:
            i = self.get_char_index(character)
            self._ordinals[character] = i
            return i

    def kern(self, g1, g2):
        try:
            return self._kerning[(g1, g2)]
        except KeyError:
            kern = self.get_kerning(g1, g2, 2)
            dx = kern.x / self.units_per_EM
            dy = kern.y / self.units_per_EM
            self._kerning[(g1, g2)] = (dx, dy)
            return (dx, dy)
    
class Memo_I_font(Memo_font):
    def __init__(self, path):
        Memo_font.__init__(self, path)
        self._ordinals = {}
        self._widths = {None: 1}
