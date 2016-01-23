from model import un
from model.meredith import mipsy
from fonts import styles
from interface import karlie
from state import contexts
    
def redo():
    if un.history.forward():
        styles.PARASTYLES.update_p()
        mipsy.recalculate_all()
        contexts.Text.update_force()

def undo():
    if un.history.back():
        styles.PARASTYLES.update_p()
        mipsy.recalculate_all()
        contexts.Text.update_force()
        
