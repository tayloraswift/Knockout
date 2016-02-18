from itertools import chain, accumulate

from interface.base import Base_kookie
from style.styles import ISTYLES

def _chunks(L, n):
    br = [i + 1 for i, v in enumerate(L) if v == '\n']
    for line in (L[i : j - 1] for i, j in zip([0] + br, br + [len(L)])):
        for i in range(0, len(line), n):
            yield line[i : i + n], not bool(i)

class Rose_garden(Base_kookie):
    def __init__(self, x, y, width, callback, value_acquire):        
        Base_kookie.__init__(self, x, y, width, 28, font=('mono',))

        self._callback = callback
        self._value_acquire = value_acquire
        
        self._SYNCHRONIZE()
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = 0
        self._j = 0
        
        self._scroll = 0

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = self._value_acquire()
        self._GLYPHS = list(self._VALUE) + [None]
        self._grid_glyphs(self._GLYPHS)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_REPRESENT()
        self._PREV_VALUE = self._VALUE

    def _grid_glyphs(self, glyphs):
        width = 34
        x = self._x
        y = self._y
        font = self.font
        fontsize = font['fontsize']
        K = font['fontmetrics'].advance_pixel_width(' ') * fontsize
        leading = int(fontsize * 1.3)
        FMX = font['fontmetrics'].character_index
        
        lines = list(_chunks(self._GLYPHS, width))
        A = list(accumulate(len(l) + 1 for l, br in lines))
        IJ = zip([0] + A[:-1], A)
        xd = x + 30
        self._LL = [[(FMX(character), xd + i*K, y + l*leading) for i, character in enumerate(line)] for l, (line, br) in enumerate(lines)]
        self._numbers = [[(FMX(character), x + i*K, y + l*leading) for i, character in enumerate(str(l))] for l, (line, br) in enumerate(lines) if br]
        
        self._y_bottom = y + leading * len(self._LL)
        
    def is_over(self, x, y):
        return self._y <= y <= self._y_bottom and self._x - 10 <= x <= self._x_right + 10

    def _entry(self):
        return ''.join(self._GLYPHS[:-1])
    
    # typing
    def type_box(self, name, char):
        pass

    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._scroll = 0
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._callback(self._domain(self._VALUE), * self._params)
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            return False
        return True

    def hover(self, x, y):
        return 1
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        # line numbers
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.show_glyphs(chain.from_iterable(self._numbers))
        
        cr.set_source_rgb(0, 0, 0)
        # don't print the cap glyph
        cr.show_glyphs(chain.from_iterable(self._LL))
        cr.fill()

