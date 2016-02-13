from model.cat import Glyphs_line
from style import styles
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image

def _fracbound(glyphs, fontsize):
    if glyphs:
        width = glyphs[-1][5]
        subfrac = [glyph[6].height for glyph in glyphs if glyph[0] == -89]
        if subfrac:
            height = max(subfrac)
        else:
            height = fontsize
    else:
        width = 0
        height = leading
    return width, height

class Fraction(object):
    def __init__(self, L):
        self._fraction = L
        
        numerator = next(E for tag, E in L[1] if tag[0] == 'module:fraction:numerator')
        denominator = next(E for tag, E in L[1] if tag[0] == 'module:fraction:denominator')
        
        self._INLINE = [numerator, denominator]
    
    def _draw_vinculum(self, cr, x, y):
        cr.set_source_rgba( * self._color)
        cr.rectangle(x + self._vx, y + self._vy, self._fracwidth, 0.5)
        cr.fill()
    
    def cast_inline(self, x, y, leading, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        fontsize = FSTYLE['fontsize']
        vy = y - fontsize/4
        numerator = _cast_mono_line(self._INLINE[0], 13, PP, F)
        denominator = _cast_mono_line(self._INLINE[1], 13, PP, F)
        nwidth, nheight = _fracbound(numerator['GLYPHS'], fontsize)
        dwidth, dheight = _fracbound(denominator['GLYPHS'], fontsize)
        fracwidth = max(nwidth, dwidth) + leading/2
        fracheight = nheight + dheight
        numerator['x'] = x + (fracwidth - nwidth)/2
        numerator['y'] = vy - nheight/2
        numerator['hyphen'] = None
        denominator['x'] = x + (fracwidth - dwidth)/2
        denominator['y'] = vy + dheight
        denominator['hyphen'] = None
        self._fracwidth = fracwidth
        self._vy = vy
        self._vx = x
        return _MInline([numerator, denominator], self._draw_vinculum, fracwidth, fracheight)

    def __len__(self):
        return 11

class _MInline(object):
    def __init__(self, lines, vinculum, width, height):
        self._LINES = lines
        self._draw_vinculum = vinculum
        self.width = width
        self.height = height
    
    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        repository['_paint'].append(lambda cr: self._draw_vinculum(cr, x, y))

def _cast_mono_line(letters, leading, PP, F):
    LINE = Glyphs_line({
            'i': 0,
      
            'leading': leading,
            
            'F': F,
            'PP': PP
            })
    
    # list that contains glyphs
    GLYPHS = []
    x = 0
    y = 0

    # retrieve font style
    fstat = F.copy()
    FSTYLE = styles.PARASTYLES.project_f(PP, F)

    glyphwidth = 0

    for letter in letters:
        CT = type(letter)
        if CT is OpenFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] += 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            GLYPHS.append((-4, x, y, FSTYLE, fstat, x))
            
        elif CT is CloseFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] -= 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            GLYPHS.append((-5, x, y, FSTYLE, fstat, x))
            
        elif CT is Paragraph:
            GLYPHS.append((
                    -2,                      # 0
                    x - FSTYLE['fontsize'],  # 1
                    y,                       # 2
                    
                    FSTYLE,                  # 3
                    fstat,                   # 4
                    x - FSTYLE['fontsize']   # 5
                    ))
        
        elif letter == '</p>':
            GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
        
        elif letter == '<br/>':
            GLYPHS.append((-6, x, y, FSTYLE, fstat, x))

        else:
            if CT is str:
                glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(letter) * FSTYLE['fontsize']
                GLYPHS.append((
                        FSTYLE['fontmetrics'].character_index(letter),  # 0
                        x,                                              # 1
                        y,                                              # 2
                        
                        FSTYLE,                                         # 3
                        fstat,                                          # 4
                        x + glyphwidth                                  # 5
                        ))
            
            elif CT is Image:
                glyphwidth = letter.width
                                                              # additional fields:  image object | scale ratio
                GLYPHS.append((-13, x, y - leading, FSTYLE, fstat, x + glyphwidth, (letter.image_surface, letter.factor)))

            else:
                try:
                    inline = letter.cast_inline(x, y, leading, PP, F, FSTYLE)
                    glyphwidth = inline.width                               #6. object
                    GLYPHS.append((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
                except AttributeError:
                    glyphwidth = leading
                    GLYPHS.append((-23, x, y, FSTYLE, fstat, x + leading))
            
            x += glyphwidth + FSTYLE['tracking']

    LINE['j'] = len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    # cache x's
    LINE['_X_'] = [g[1] for g in GLYPHS]
    
    try:
        LINE['F'] = GLYPHS[-1][4]
    except IndexError:
        pass
    
    return LINE
