from fonts import fonttable

from model import un
from model.meredith import mipsy

from interface import karlie
    
def redo():
    if un.history.forward():
    
        fonttable.table.clear()
        fonttable.p_table.clear()
        karlie.klossy.refresh()

def undo():
    if un.history.back():
    
        fonttable.table.clear()
        fonttable.p_table.clear()
        karlie.klossy.refresh()
