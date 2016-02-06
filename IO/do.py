from IO import un
from model import meredith
from style import styles
from state import contexts
    
def redo():
    if un.history.forward():
        styles.PARASTYLES.update_p()
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()

def undo():
    if un.history.back():
        styles.PARASTYLES.update_p()
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()
        
