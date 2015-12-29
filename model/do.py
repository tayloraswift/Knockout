from model import un
from model.meredith import mipsy
from fonts import styles
from interface import karlie
from state import contexts
    
def redo():
    if un.history.forward():
        styles.FONTSTYLES.update_tables()
        styles.PARASTYLES.update_tables()
        contexts.Text.update_force()
        contexts.Tag.update()
        mipsy.recalculate_all()

def undo():
    if un.history.back():
        styles.FONTSTYLES.update_tables()
        styles.PARASTYLES.update_tables()
        contexts.Text.update_force()
        contexts.Tag.update()
        mipsy.recalculate_all()
