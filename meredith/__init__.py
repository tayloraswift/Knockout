from itertools import chain

from edit import cursor, caramel
from meredith import box, elements, styles, paragraph, settings
from modules import use

boxes = {B.name: B for B in chain.from_iterable(M.members for M in chain((box, styles, elements, paragraph, settings, cursor, caramel), use))}
