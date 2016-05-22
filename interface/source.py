from itertools import chain, accumulate, zip_longest, groupby
from bisect import bisect

from pygments.lexers import html as pygments_html
from pygments.token import Token

from fonts.interfacefonts import ISTYLES

from IO.tree import serialize, deserialize

#from elements.node import Mod_element
from edit import cursor
from edit.text import expand_cursors_word
#from edit.paperairplanes import interpret_rgba
from state.exceptions import IO_Error

from interface.base import Base_kookie, accent

xml_lexer = pygments_html.XmlLexer(stripnl=False)

def _linebreak(L, n):
    start = 0
    limit = n
    br = limit
    check = {' ', '\n'}
    new = True
    for i, (c, v) in enumerate(L):
        if v in check:
            if v == '\n':
                line = L[start:i + 1], new
                new = True
                start = i + 1
                limit = start + n
                br = limit
                yield line
            else:
                br = i
        if i > limit:
            line = L[start:br + 1], new
            if new:
                new = False
            start = br + 1
            limit = start + n
            br = limit
            yield line

def _paint_select(cl, sl, cx, sx, left, right):
    select = []
    if cl == sl:
                           # y, x1, x2
        select.append((cl, cx, sx))
    else:
        (cl, cx), (sl, sx) = sorted(((cl, cx), (sl, sx)))
        select.append((cl, cx, right))
        select.extend(((l, left, right) for l in range(cl + 1, sl)))
        select.append((sl, left, sx))
    return select

class Rose_garden(Base_kookie):
    def __init__(self, x, y, width, e_acquire, before=lambda: None, after=lambda: None):
        self._BEFORE = before
        self._AFTER = after
        self._e_acquire = e_acquire

        self.font = ISTYLES[('mono',)]
        fontsize = self.font['fontsize']
        self._K = self.font['fontmetrics'].advance_pixel_width(' ') * fontsize
        self._leading = int(fontsize * 1.3)
        
        self._charlength = int((width - 30) // self._K)
        width = int(self._charlength * self._K + 30)

        palatte = {Token.Text: "#2e3436",
                        Token.Name.Attribute: "#7A6ACD",
                        Token.Literal.String: "#9a43ff",
                        Token.Name.Tag: "#6b5fef",
                        Token.Error: "1, 0.2, 0.3"}
        self._palatte = {token: interpret_rgba(color) for token, color in palatte.items()}
        
        Base_kookie.__init__(self, x, y, width, 0, font=None)
        
        self._SYNCHRONIZE()
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = 0
        self._j = 0
        
        self._active = False
        self._invalid = False

    def _ACQUIRE_REPRESENT(self):
        self._element = self._e_acquire()
        self._VALUE = serialize([self._element])
        self._CHARS = list(self._VALUE) + ['\n']
        self._grid_glyphs(self._CHARS)
        self._invalid = False

    def _SYNCHRONIZE(self):
        self._ACQUIRE_REPRESENT()
        self._PREV_VALUE = self._VALUE

    def _grid_glyphs(self, glyphs):
        x = self._x
        y = self._y
        
        K = self._K
        leading = self._leading
        FMX = self.font['fontmetrics'].character_index
        
        colored_chars = list(chain.from_iterable(zip_longest([], text, fillvalue=self._palatte.get(token, (0, 0, 0, 1))) for token, text in xml_lexer.get_tokens(''.join(self._CHARS))))
#        print(set(token for token, text in xml_lexer.get_tokens(''.join(self._CHARS))))
        lines = list(_linebreak(colored_chars, self._charlength))
        self._IJ = [0] + list(accumulate(len(l) for l, br in lines))
        self.y_bottom = y + leading * len(lines)
        
        y += leading
        xd = x + 30
        
        colored_text = {color: [] for color in self._palatte.values()}
        for l, line in enumerate(lines):
            for color, G in groupby(((FMX(character), xd + i*K, y + l*leading, color) for i, (color, character) in enumerate(line[0]) if character != '\n'),
                    key = lambda k: k[3]):
                try:
                    colored_text[color].extend((g, h, k) for g, h, k, c in G)
                except KeyError:
                    colored_text[color] = [(g, h, k) for g, h, k, c in G]
        
        N = zip(accumulate(line[1] for line in lines), enumerate(lines))
        numbers = chain.from_iterable(((FMX(character), x + i*K, y + l*leading) for i, character in enumerate(str(int(N)))) for N, (l, line) in N if line[1])
        colored_text[(0.7, 0.7, 0.7, 1)] = list(numbers)
        self._rows = len(lines)
        self._colored_text = colored_text
        
        #documentation
        """
        if isinstance(self._element, Mod_element):
            self._doc = self._element.get_documentation()
        else:
            self._doc = [(0, str(type(self._element)) + ' element', [])]
        """
    
    def _target(self, x, y):
        y -= self._y
        x -= self._x + 30
        
        l = min(max(int(y // self._leading), 0), self._rows - 1)
        di = int(round(x / self._K))
        i = self._IJ[l]
        j = self._IJ[l + 1]
        if x > self._width - 20:
            j += 1
        g = min(max(di + i, i), j - 1)
        return g
    
    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and self._x <= x <= self._x_right + 10

    def _entry(self):
        return ''.join(self._CHARS[:-1])
    
    # typing
    def type_box(self, name, char):
        changed = False
        output = None
        if name in ['BackSpace', 'Delete']:
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                del self._CHARS[self._i : self._j]
                changed = True
                self._j = self._i
                
            elif name == 'BackSpace':
                if self._i > 0:
                    del self._CHARS[self._i - 1]
                    changed = True
                    self._i -= 1
                    self._j -= 1
            else:
                if self._i < len(self._CHARS) - 2:
                    del self._CHARS[self._i]
                    changed = True

        elif name == 'Left':
            if self._i > 0:
                self._i -= 1
                self._j = self._i
        elif name == 'Right':
            if self._i < len(self._CHARS) - 1:
                self._i += 1
                self._j = self._i
        elif name == 'Up':
            l = self._index_to_line(self._i)
            u = max(0, l - 1)
            z = self._IJ[l]
            a = self._IJ[u]
            b = self._IJ[u + 1]
            self._i = min(a + self._i - z, b)
            self._j = self._i
        elif name == 'Down':
            l = self._index_to_line(self._i)
            u = min(self._rows - 1, l + 1)
            z = self._IJ[l]
            a = self._IJ[u]
            b = self._IJ[u + 1]
            self._i = min(a + self._i - z, b, len(self._CHARS) - 1)
            self._j = self._i
            
        elif name == 'Home':
            l = self._index_to_line(self._i)
            z = self._IJ[l]
            self._i = z
            self._j = z
        elif name == 'End':
            l = self._index_to_line(self._i)
            z = self._IJ[l + 1] - 1
            self._i = z
            self._j = z

        elif name == 'All':
            self._i = 0
            self._j = len(self._CHARS) - 1
        
        elif name == 'Paste':
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                del self._CHARS[self._i : self._j]
                self._j = self._i
            # take note that char is a LIST now
            self._CHARS[self._i:self._i] = char
            changed = True
            self._i += len(char)
            self._j = self._i
        
        elif name == 'Copy':
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                output = ''.join(self._CHARS[self._i : self._j])
        
        elif name == 'Cut':
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                output = ''.join(self._CHARS[self._i : self._j])
                del self._CHARS[self._i : self._j]
                changed = True
                self._j = self._i
        
        elif name == 'Tab':
            self._i, self._j = sorted((self._j, self._i))
            cl = self._index_to_line(self._i)
            sl = self._index_to_line(self._j)
            if cl == sl:
                a = self._IJ[cl]
                self.type_box('Paste', ' ' * (4 - (self._i - a) % 4))
            else:
                IJ = self._IJ
                CHARS = self._CHARS
                di = 0
                dj = 0
                for l in range(sl, cl - 1, -1):
                    a = IJ[l]
                    if CHARS[a - 1] == '\n':
                        CHARS[a : a] = ' ' * 4
                        dj += 4

                changed = True
                self._i += 4
                self._j += dj
        
        elif name in {'Ctrl Tab', 'ISO_Left_Tab'}:
            self._i, self._j = sorted((self._j, self._i))
            cl = self._index_to_line(self._i)
            sl = self._index_to_line(self._j)
            IJ = self._IJ
            CHARS = self._CHARS
            ifloor = None
            di = 0
            dj = 0
            for l in range(sl, cl - 1, -1):
                a = IJ[l]
                if CHARS[a - 1] == '\n':
                    b = IJ[l + 1] - 1
                    if b - a >= 4:
                        try:
                            d = next(i for i, v in enumerate(CHARS[a : a + 4]) if v != ' ')
                        except StopIteration:
                            d = 4
                        dj -= d
                        di = -d
                        ifloor = a
                        del CHARS[a : a + d]
            changed = True
            self._i = max(ifloor, self._i + di)
            self._j += dj

        elif char is not None:
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                del self._CHARS[self._i : self._j]
                self._j = self._i
            if char == '\r':
                char = '\n'
            self._CHARS[self._i:self._i] = [char]
            changed = True
            self._i += 1
            self._j += 1
        
        if changed:
            self._grid_glyphs(self._CHARS)
        
        return output

    def focus(self, x, y):
        self._i = self._target(x, y)
        self._j = self._i
        self._active = True
    
    def dpress(self):
        self._i, self._j = expand_cursors_word(self._CHARS, self._i)

    def focus_drag(self, x, y):
        j = self._target(x, y)
        
        # force redraw if cursor moves
        if self._j != j:
            self._j = j
            return True
        else:
            return False

    def _commit(self, B):
        success = False
        if isinstance(self._element, Mod_element):
            try:
                E = deserialize(B, fragment=True)

                try: # locate object
                    L = [next(e for e in E if type(e) is type(self._element))]
                    success = True
                except StopIteration:
                    # if the object type changed
                    try:
                        L = [next(e for e in E if isinstance(e, Mod_element))]
                        success = True
                    except StopIteration:
                        pass
                    pass

            except (IO_Error, IndexError):
                pass
        
        else:
            try:
                L = deserialize(B, fragment=True)
                success = True
            except IO_Error:
                pass

        if not success:
            self._invalid = True
            return
        i = cursor.fcursor.i
        cursor.fcursor.j = i + 1
        cursor.fcursor.insert(L)
        cursor.fcursor.i = i
        cursor.fcursor.j = i
        self._SYNCHRONIZE()
        self._AFTER()
        
    def defocus(self):
        self._active = False
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._commit(self._VALUE)
            self._PREV_VALUE = self._VALUE
        else:
            return False
        return True

    def hover(self, x, y):
        return 1
    
    def _index_to_line(self, i):
        return bisect(self._IJ, i) - 1
    
    def _cursor_location(self, i):
        l = self._index_to_line(i)
        gx = (i - self._IJ[l]) * self._K
        return l, int(self._x + 30 + gx), self._y + self._leading * l

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        # highlight
        if self._active:
            cr.set_source_rgba(0, 0, 0, 0.1)
            leading = self._leading
            cl, cx, cy = self._cursor_location(self._i)
            sl, sx, sy = self._cursor_location(self._j)

            for l, x1, x2 in _paint_select(cl, sl, cx, sx, self._x + 30, self._x_right):
                cr.rectangle(x1, self._y + l*leading, x2 - x1, leading)
            cr.fill()

        # text
            color_iter = self._colored_text.items()
        else:
            if self._invalid:
                color_iter = (((1, 0.4, 0.4), glyphs) for glyphs in self._colored_text.values())
            else:
                color_iter = self._colored_text.items()
        for color, glyphs in color_iter:
            cr.set_source_rgba( * color )
            cr.show_glyphs(glyphs)
            cr.fill()

        # cursor
        if self._active:
            cr.set_source_rgb( * accent)
            cr.rectangle(cx - 1, cy, 2, leading)
            cr.rectangle(sx - 1, sy, 2, leading)
            cr.fill()
