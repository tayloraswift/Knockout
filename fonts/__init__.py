import os

import gi
gi.require_version('HarfBuzz', '0.0')

from gi.repository import HarfBuzz as hb
from gi.repository.GLib import Bytes

from itertools import chain

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

_ot_type_registry = {}
_emoji_type_registry = {}

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
SPACES['\t'] = -8

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

def ot_feature(bytename, value):
    b, O = hb.feature_from_string(bytename)
    if b:
        O.value = value
        return O
    else:
        raise ValueError('invalid opentype feature name ' + repr(str(bytename)))
       
class OT_feature_modes(dict):
    def __init__(self, bytename):
        self._bytename = bytename
        dict.__init__(self)
    
    def __missing__(self, key):
        self[key] = v = ot_feature(self._bytename, key)
        return v

def get_ot_feature_modes(name):
    bytename = list(map(ord, name))
    return ot_feature(bytename, 0), ot_feature(bytename, 1), OT_feature_modes(bytename)

common_features =  ['kern', 'calt', 'liga', 'hlig',
                    'case', 'cpsp', 'smcp', 'pcap', 'c2sc', 'c2pc', 
                    'unic', 'ordn', 'zero', 'frac', 'afrc', 'sinf', 
                    'subs', 'sups', 'ital', 'mgrk', 
                    'lnum', 'onum', 'pnum', 'tnum', 
                    'rand', 'salt', 'swsh', 'titl']
feature_map = {feature: get_ot_feature_modes(feature) for feature in common_features}

def _hb_face_from_path(filepath):
    with open(filepath, 'rb') as fi:
        fontdata = fi.read()
    return hb.face_create(hb.glib_blob_create(Bytes.new(fontdata)), 0)

def get_ot_font(path, overwrite=False):
    if path not in _ot_type_registry or overwrite:
        # check if is sfd or binary
        fontname, ext = os.path.splitext(path)
        if ext == '.sfd':
            print('Warning: implicit OTF build triggered')
            os.system('fontforge -script IO/sfd2otf.pe ' + path)
            filepath = fontname + '.otf'
        else:
            filepath = path
        print('\033[92mLoading font\033[0m      :', filepath)
        HB_face = _hb_face_from_path(filepath)
        HB_font = hb.font_create(HB_face)
        upem = hb.face_get_upem(HB_face)
        hb.font_set_scale(HB_font, upem, upem)
        hb.ot_font_set_funcs(HB_font)

        CR_face = fontloader.create_cairo_font_face_for_file(filepath)
        _ot_type_registry[path] = upem, HB_face, HB_font, CR_face
        
    return _ot_type_registry[path]

def get_emoji_font(path, overwrite=False):
    if path not in _emoji_type_registry or overwrite:
        print('\033[92mLoading emoji font\033[0m:', path)
        upem, HB_face, HB_font, CR_face = get_ot_font(path)
        _emoji_type_registry[path] = upem, HB_font, Emoji_font(path)
    return _emoji_type_registry[path]

def _hb_get_advance(hb_font, char):
    return hb.font_get_glyph_h_advance(hb_font, hb.font_get_glyph(hb_font, ord(char), 0)[1])

def get_ot_space_metrics(hb_font, fontsize, factor):
    proportions =  (('\u2003', 1   ), # em
                    ('\u2002', 0.5 ), # en
                    ('\u2004', 1/3 ), # 1/3
                    ('\u2005', 0.25), # 1/4
                    ('\u2006', 1/6 ), # 1/6
                    ('\u2009', 0.2 ), # thin
                    ('\u200A', 0.1 ), # hair
                    ('\u202F', 0.2 ), # narrow nbsp
                    ('\u205F', 4/18)) # math med
    widths = {SPACES[c]: x*fontsize for c, x in proportions}
    widths[SPACES['\t']]     = 0
    widths[SPACES['\u00A0']] = _hb_get_advance(hb_font, ' ')*factor # nbsp
    widths[SPACES['\u2007']] = _hb_get_advance(hb_font, '0')*factor # figure
    widths[SPACES['\u2008']] = _hb_get_advance(hb_font, ',')*factor # punctuation
    return widths

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

class Emoji_font(object):
    def __init__(self, path):
        self._emojis = {}
        if TTFont is not None:
            self._vectors = dict(chain.from_iterable(((n, SVG) for n in range(i, j + 1)) for SVG, i, j in TTFont(path)['SVG '].docList))
        else:
            self._vectors = {}
    
    def generate_paint_function(self, i, fontsize, factor):
        try:
            return self._emojis[(i, fontsize)]
        except KeyError:
            try:
                BS = self._vectors[i]
            except KeyError:
                self._emojis[(i, fontsize)] = E = lambda cr, render: _print_emoji_error(cr, fontsize)
                return E
            
            E = Emoji(SVG_image(bytestring=BS, dx=0, dy=1788, hfactor=2.5, kfactor=2.5), factor)
            self._emojis[(i, fontsize)] = E.render_bubble
            return E.render_bubble

class Emoji(object):
    def __init__(self, SVGI, factor):
        self._SVGI = SVGI
        self._factor = factor/0.045
    
    def render_bubble(self, cr, render=False):
        cr.save()
        cr.scale(self._factor, self._factor)
        self._SVGI.paint(cr, render)
        cr.restore()

class Grid_font(object):
    def __init__(self, hb_font, upem):
        self._upem_fac = 1/upem
        self._hb_font = hb_font
        self._ordinals = {}
        self._widths = {None: 1}
    
    def advance_pixel_width(self, character):
        try:
            return self._widths[character]
        except KeyError:
            self._widths[character] = p = hb.font_get_glyph_h_advance(self._hb_font, self.character_index(character)) * self._upem_fac
            return p
    
    def character_index(self, character):
        try:
            return self._ordinals[character]
        except KeyError:
            self._ordinals[character] = i = hb.font_get_glyph(self._hb_font, ord(character), 0)[1]
            return i
