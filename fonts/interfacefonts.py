from bulletholes.counter import TCounter as Counter

from meredith.styles import Textstyle
from meredith.settings import interface_kt

from fonts import get_ot_font, Grid_font

from state import constants

class Interface_fonts(dict):
    def __init__(self, KT, IBSTYLE, ITSTYLES, * combos ):
        FD = {name: Textstyle(KT, IT) for name, IT in ITSTYLES.items()}
        self._P = [(FD[F], Counter(tags)) for F, tags in IBSTYLE]
        dict.__init__(self)
        for U in combos:
            self.__missing__(U)
        
    def __missing__(self, U):
        F = Counter(U)
        # iterate through stack
        projection = Textstyle.BASE.copy()
        
        for TS in (TS for TS, tags in self._P if tags <= F):
            projection.update(TS)

        # set up fonts
        upem, hb_face, projection['__hb_font__'], projection['font'] = get_ot_font(projection['path'])
        projection['__factor__'] = projection['fontsize']/upem
        projection['__gridfont__'] = Grid_font(projection['__hb_font__'], upem)
        
        self[U] = projection
        return projection

ISTYLES = Interface_fonts(interface_kt, constants.interface_bstyle, constants.interface_tstyles, (), ('title',), ('strong',), ('label',), ('mono',))
