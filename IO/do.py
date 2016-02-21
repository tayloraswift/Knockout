from IO import un
from model import meredith
from typing import typing
from style import styles
from state import contexts
from elements.elements import Mod_element
    
def redo():
    if un.history.forward():
        styles.PARASTYLES.update_p()
        
        typing.keyboard.turnover()
        Mod_element.MSL.turnover()
        
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()

def undo():
    if un.history.back():
        styles.PARASTYLES.update_p()

        typing.keyboard.turnover()
        Mod_element.MSL.turnover()
        
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()
