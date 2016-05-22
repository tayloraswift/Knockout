from bulletholes.counter import TCounter as Counter

from meredith.styles import Textstyle

from fonts import get_font

from state import constants

def _create_interface():
    FD = {name: Textstyle(IT) for name, IT in constants.interface_fstyles.items()}
    P = [(FD[F], Counter(tags)) for F, tags in constants.interface_pstyle]
    ui_styles = ((), ('title',), ('strong',), ('label',), ('mono',))
    for U in ui_styles:
        F = Counter(U)
        # iterate through stack
        projection = Textstyle.BASE.copy()
        
        for TS in (TS for TS, tags in P if tags <= F):
            projection.update(TS)

        # set up fonts
        projection['fontmetrics'], projection['font'] = get_font(projection['path'])
        
        yield U, projection

ISTYLES = dict(_create_interface())
