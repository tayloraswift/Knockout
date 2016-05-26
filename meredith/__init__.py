from itertools import chain

from meredith import box, elements, styles, paragraph
from modules import use

boxes = {B.name: B for B in chain.from_iterable(M.members for M in chain((box, styles, elements, paragraph), use))}
