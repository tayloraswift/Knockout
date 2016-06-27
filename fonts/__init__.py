import os

import gi
gi.require_version('HarfBuzz', '0.0')

from gi.repository import HarfBuzz as hb
from gi.repository.GLib import Bytes

from itertools import chain

from libraries import freetype

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

from IO.image import SVG_image, render_SVG

try:
    from fontTools.ttLib import TTFont
except ImportError:
    print(_bold + _fail + 'ERROR: The fontTools library can’t be found. Emoji rendering has been disabled.' + _endc + _fail + ' \n\tTry ' + _bold + 'pip3 install fonttools' + _endc + _fail + '\n\tMake sure pip installs hunspell for python3.5, not python3.4!' + _endc)
    TTFont = None

if render_SVG is None:
    print(_bold + _fail + 'WARNING: SVG rendering is disabled. Emoji rendering has been disabled.' + _endc)
    TTFont = None

from fonts import fontloader

_type_registry = {}

_ot_type_registry = {}

# spaces
nonbreaking_spaces = {
            '\u00A0': -30, # nbsp
            '\u2007': -36, # figure
            '\u202F': -40, # narrow nbsp
            }

breaking_spaces = {
            '\u2003': -31, # em
            '\u2002': -32, # en
            '\u2004': -33, # 1/3
            '\u2005': -34, # 1/4
            '\u2006': -35, # 1/6
            
            '\u2008': -37, # punctuation
            '\u2009': -38, # thin
            '\u200A': -39, # hair
            
            '\u205F': -41, # math med
            }

SPACES = nonbreaking_spaces.copy()
SPACES.update(breaking_spaces)
SPACES['\t'] = -7

SPACENAMES = {
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

def get_ot_font(path, overwrite=False):
    if path not in _ot_type_registry or overwrite:
        # check if is sfd or binary
        fontname, ext = os.path.splitext(path)
        if ext == '.sfd':
            print('Warning: implicit OTF build triggered')
            os.system('fontforge -script IO/sfd2otf.pe ' + path)
            #raise freetype.ft_errors.FT_Exception('SFD not supported')
            filepath = fontname + '.otf'
        else:
            filepath = path
        print('\033[92mLoading font\033[0m      :', filepath)
        with open(filepath, 'rb') as fi:
            fontdata = fi.read()
        HB_face = hb.face_create(hb.glib_blob_create(Bytes.new(fontdata)), 0)
        CR_face = fontloader.create_cairo_font_face_for_file(filepath)
        _ot_type_registry[path] = HB_face, CR_face
        
    return _ot_type_registry[path]

def _hb_get_advance(hb_font, char):
    return hb.font_get_glyph_h_advance(hb_font, hb.font_get_glyph(hb_font, ord(char), 0)[1])

def get_ot_space_metrics(hb_font):
    xppem = hb.font_get_scale(hb_font)[0]
    proportions =  (('\u2003', 1   ), # em
                    ('\u2002', 0.5 ), # en
                    ('\u2004', 1/3 ), # 1/3
                    ('\u2005', 0.25), # 1/4
                    ('\u2006', 1/6 ), # 1/6
                    ('\u2009', 0.2 ), # thin
                    ('\u200A', 0.1 ), # hair
                    ('\u202F', 0.2 ), # narrow nbsp
                    ('\u205F', 4/18)) # math med
    widths = {SPACES[c]: x*xppem for c, x in proportions}
    widths[SPACES['\t']]     = 0
    widths[SPACES['\u00A0']] = _hb_get_advance(hb_font, ' ') # nbsp
    widths[SPACES['\u2007']] = _hb_get_advance(hb_font, '0') # figure
    widths[SPACES['\u2008']] = _hb_get_advance(hb_font, ',') # punctuation
    return widths

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
        print('\033[92mLoading font\033[0m      :', filepath)
        FT_font = Memo_font(filepath)
        CR_font = fontloader.create_cairo_font_face_for_file(filepath)
        _type_registry[path] = FT_font, CR_font
        
    return _type_registry[path]

def get_emoji_font(path, overwrite=False):
    if path not in _type_registry or overwrite:
        print('\033[92mLoading emoji font\033[0m:', path)
        _type_registry[path] = Emoji_font(path)
    return _type_registry[path]

# extended fontface class
class Memo_font(freetype.Face):
    
    def __init__(self, path):
        freetype.Face.__init__(self, path)
        UPM = self.units_per_EM
        self._kerning = {}
        self._ordinals = SPACES.copy()
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

def _print_emoji_error(cr, fontsize):
    unit = int(round(fontsize*0.05))
    cr.set_source_rgb(0.4, 0.4, 0.4)
    cr.rectangle(unit, unit, fontsize - 2*unit, fontsize - 2*unit)
    cr.fill()
    cr.set_line_width(2*unit)
    cr.move_to(4*unit, 4*unit)
    cr.line_to(fontsize - 4*unit, fontsize - 4*unit)
    cr.move_to(fontsize - 4*unit, 4*unit)
    cr.line_to(4*unit, fontsize - 4*unit)
    cr.set_source_rgb(1, 1, 1)
    cr.stroke()

class Emoji_font(Memo_font):
    def __init__(self, path):
        Memo_font.__init__(self, path)
        
        
        self._emojis = {}
        self._fac = fac = 1/(self.units_per_EM*0.045)
        if TTFont is not None:
            self._vectors = dict(chain.from_iterable(((n, SVG) for n in range(i, j + 1)) for SVG, i, j in TTFont(path)['SVG '].docList))
        else:
            self._vectors = {}
    
    def generate_paint_function(self, letter, fontsize):
        try:
            return self._emojis[(letter, fontsize)]
        except KeyError:
            i = self.character_index(letter)
            try:
                BS = self._vectors[i]
            except KeyError:
                self._emojis[(letter, fontsize)] = lambda cr, render: _print_emoji_error(cr, fontsize)
                return self._emojis[(letter, fontsize)]
            
            E = Emoji(SVG_image(bytestring=BS, dx=0, dy=1788, hfactor=2.5, kfactor=2.5), 
                      fontsize*self._fac)
            self._emojis[(letter, fontsize)] = E.render_bubble
            return E.render_bubble

class Emoji(object):
    def __init__(self, SVGI, factor):
        self._SVGI = SVGI
        self._factor = factor
    
    def render_bubble(self, cr, render=False):
        cr.save()
        cr.scale(self._factor, self._factor)
        self._SVGI.paint(cr, render)
        cr.restore()
    
class Memo_I_font(Memo_font):
    def __init__(self, path):
        Memo_font.__init__(self, path)
        self._ordinals = {}
        self._widths = {None: 1}
