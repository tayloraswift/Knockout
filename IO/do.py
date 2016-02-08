from IO import un
from model import meredith
from typing import typing
from style import styles
from state import contexts
    
def redo():
    if un.history.forward():
        styles.PARASTYLES.update_p()
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()
        
        typing.keyboard.__init__()

def undo():
    if un.history.back():
        styles.PARASTYLES.update_p()
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()
        
        typing.keyboard.__init__()
