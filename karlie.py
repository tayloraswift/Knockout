import kookies
import constants
import meredith

import bisect
import fonts

import noticeboard

from freetype import ft_errors


_ui_font = fonts.paragraph_classes['_interface'].fontclasses[()]


class _Font_file_Field(kookies.Blank_space):
    def __init__(self, x, y, width, p, f, name=None, update=False):
    
        kookies.Blank_space.__init__(self, x, y, width, fonts.paragraph_classes[p].fontclasses[f].path, callback=self._push_fontname, name=name, update=update)

        self.p = p
        self.f = f

        if not fonts.paragraph_classes[self.p].fontclasses[self.f].path_valid:
            self.broken = True
        else:
            self.broken = False

    def _push_fontname(self, path):
        try:
            fonts.paragraph_classes[self.p].fontclasses[self.f].update_path(path)
            self.broken = False
            fonts.paragraph_classes[self.p].fontclasses[self.f].path_valid = True
            meredith.mipsy.rerender()
        except ft_errors.FT_Exception:
#            fonts.paragraph_classes[self.p].fontclasses[self.f].font = None
            self.broken = True
            fonts.paragraph_classes[self.p].fontclasses[self.f].path_valid = False
            meredith.mipsy.rerender()
            print('Font not found')

   
class _Font_size_Field(kookies.Numeric_field):
    def __init__(self, x, y, width, p, f, name=None, update=False):
        kookies.Numeric_field.__init__(self, x, y, width, 
                str(fonts.paragraph_classes[p].fontclasses[f].fontsize), 
                callback=self._push_fontsize, 
                name=name, 
                update=update)
        
        self.p = p
        self.f = f
        
    def _push_fontsize(self, size):
        fonts.paragraph_classes[self.p].fontclasses[self.f].update_size(self._to_number(size))
        meredith.mipsy.rerender()

class _Font_tracking_Field(kookies.Numeric_field):
    def __init__(self, x, y, width, p, f, name=None, update=False):
        kookies.Numeric_field.__init__(self, x, y, width, 
                str(fonts.paragraph_classes[p].fontclasses[f].tracking), 
                callback=self._push_tracking, 
                name=name, 
                update=update)
        
        self.p = p
        self.f = f
        
    def _push_tracking(self, tracking):
        fonts.paragraph_classes[self.p].fontclasses[self.f].update_tracking(self._to_number(tracking))
        meredith.mipsy.rerender()

class _Paragraph_leading_Field(kookies.Numeric_field):
    def __init__(self, x, y, width, p, name=None, update=False):
        kookies.Numeric_field.__init__(self, x, y, width, 
                str(fonts.paragraph_classes[p].leading), 
                callback=self._push_leading, 
                name=name, 
                update=update)
        
        self.p = p

    def _push_leading(self, leading):
        fonts.paragraph_classes[self.p].update_leading(self._to_number(leading))
        meredith.mipsy.rerender()

class _Paragraph_margin_Field(kookies.Numeric_field):
    def __init__(self, x, y, width, p, name=None, update=False):
        kookies.Numeric_field.__init__(self, x, y, width, 
                str(fonts.paragraph_classes[p].margin_bottom), 
                callback=self._push_margin, 
                name=name, 
                update=update)
        
        self.p = p

    def _push_margin(self, margin):
        fonts.paragraph_classes[self.p].update_margin(self._to_number(margin))
        meredith.mipsy.rerender()

class _Paragraph_style_menu(kookies.Object_menu):
    def __init__(self, x, y, width, p, addition_callback, menu_callback, name=None):
        kookies.Object_menu.__init__(self, x, y, width, p, callback=self._push_pname, addition_callback=addition_callback, menu_callback=menu_callback, name=name, update=True)
        
        self.p = p

#        self.hover_in_borders = self.in_borders


    def _push_pname(self, name):

        fonts.paragraph_classes[name] = fonts.paragraph_classes.pop(self.p)
        meredith.mipsy.rename_paragraph_class(self.p, name)
        self.p = name

        meredith.mipsy.rerender()
    


class _preview(kookies.Heading):
    def __init__(self, x, y, width, height, text, p, f):
        
        kookies.Heading.__init__(self, x, y, width, height, text, font=fonts.paragraph_classes[p[0]].fontclasses[f], fontsize = 15)
        
        self.p = p
        self.f = f

        
    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0,0,0)
        
        cr.set_font_size(15)
        cr.set_font_face(self.font.font)
        cr.show_glyphs(self._texts[0])

class Properties_Panel(object):
    def __init__(self):
        self._h = constants.windowwidth
        self._k = constants.windowheight
        
        
        self._tabstrip = kookies.Tabs(self._h - constants.propertieswidth/2 - 50 , 50, 100, 30, callback=self._tab_switch, signals=['paragraph', 'font', '?'], strings=['P', 'F', '?'])
        self._tab = self._tabstrip.active_name()
        
        self.menu = None
        
        self.refresh_class(meredith.mipsy.glyph_at()[2])

    
    def refresh_class(self, p):
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading(self._h - constants.propertieswidth + 15, 90, 250, 30, p[0], upper=True))

        if self._tab == 'font':
        
            for key, item in sorted(fonts.paragraph_classes[p[0]].fontclasses.items()):
                if key:
                    classname = 'Class: ' + ', '.join(key)
                else:
                    classname = 'Class: none'
                self._items.append(_preview(self._h - constants.propertieswidth + 16, y, 250, 30, classname, p, key ))
                self._items.append(_Font_file_Field(self._h - constants.propertieswidth + 15, y + 30, 250, p[0], key, name='FONT FILE' ))
                self._items.append(_Font_size_Field(self._h - constants.propertieswidth + 15, y + 75, 250, p[0], key, name='FONT SIZE' ))
                self._items.append(_Font_tracking_Field(self._h - constants.propertieswidth + 15, y + 120, 250, p[0], key, name='TRACKING' ))
                y += 180
        
        elif self._tab == 'paragraph':
            self._items.append(_Paragraph_style_menu(self._h - constants.propertieswidth + 15, y, 250, p[0], addition_callback=self._add_paragraph_class, menu_callback=self._create_paragraph_style_menu, name='RENAME CLASS'))
            
            self._items.append(_Paragraph_leading_Field(self._h - constants.propertieswidth + 15, y + 45, 250, p[0], name='LEADING' ))
            self._items.append(_Paragraph_margin_Field(self._h - constants.propertieswidth + 15, y + 90, 250, p[0], name='BOTTOM MARGIN' ))


    def _create_paragraph_style_menu(self):
        self.menu = kookies.Menu(self._h - constants.propertieswidth + 100, 150 + 18, 165, 30, self._menu_select_class, sorted(fonts.paragraph_classes.keys()) )
        
    def _menu_select_class(self, name):
        p = meredith.mipsy.glyph_at()[2]
        meredith.mipsy.change_paragraph_class(p[1], name)
        self.menu = None
        meredith.mipsy.rerender() # must come before because it rewrites all the paragraph styles
        self.refresh_class(meredith.mipsy.glyph_at()[2])
        return False

    def _add_paragraph_class(self):
        print('done')
        p = meredith.mipsy.glyph_at()[2]
        if len(p[0]) > 3 and p[0][-4] == '.' and len([c for c in p[0][-3:] if c in '1234567890']) == 3:
            serialnumber = int(p[0][-3:])
            while True:
                serialnumber += 1
                name = p[0][:-3] + str(serialnumber).zfill(3)
                if name not in fonts.paragraph_classes:
                    break
        else:
            name = p[0] + '.001'
        fonts.add_paragraph_class(name, p[0])
        meredith.mipsy.change_paragraph_class(p[1], name)
        meredith.mipsy.rerender()
        self.refresh_class(meredith.mipsy.glyph_at()[2])

    def _tab_switch(self, name):
        self._tab = name
        self.refresh_class(meredith.mipsy.glyph_at()[2])
        print(self._tab)
        
    def resize(self, h, k):
        dx = h - self._h
        self._h = h

        for entry in self._items:
            entry.translate(dx=dx)
        self.menu = None
    
    def render(self, cr, h, k):
        # DRAW BACKGROUND
        cr.rectangle(h - constants.propertieswidth, 0, 
                300, 
                k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        if noticeboard.refresh_properties_stack.should_refresh():
            self.refresh_class(meredith.mipsy.glyph_at()[2])
        
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        if self.menu:
            self.menu.draw(cr, hover=self._hover_box_ij)
        
        # DRAW SEPARATOR
        cr.rectangle(h - constants.propertieswidth, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
    
    def key_input(self, name, char):
        if self._active_box_i is not None:
            if name == 'Return':
                if self._items[self._active_box_i].defocus():
                    print('UPDATE PANEL')
                    self.refresh_class(meredith.mipsy.glyph_at()[2])
                
                self._active_box_i = None
            else:
                return self._items[self._active_box_i].type_box(name, char)
    
    def press(self, x, y):
        if self.menu is None or not self.menu.press(x, y):
            self.menu = None
            b = None

            bb = bisect.bisect([item.y for item in self._items], y)

            try:
                if self._items[bb].is_over(x, y):
                    self._items[bb].focus(x)
                    b = bb

            except IndexError:
                pass
            # defocus the other box, if applicable
            if b is None or b != self._active_box_i:
                if self._active_box_i is not None:
                    if self._items[self._active_box_i].defocus():

                        print('UPDATE PANEL')
                        self.refresh_class(meredith.mipsy.glyph_at()[2])
                        
                self._active_box_i = b

            
    def press_motion(self, x):
        if self._active_box_i is not None:
            self._items[self._active_box_i].focus_drag(x)
    
    def hover(self, x, y, hovered=[None]):
    
        self._hover_box_ij = (None, None)
        
        if self.menu is not None:
            j = self.menu.hover(x, y)
            if j is None:
                over_menu = False
            else:
                over_menu = True
        else:
            over_menu = False
        if over_menu:
            self._hover_box_ij = ('menu', j)
        else:
            bb = bisect.bisect([item.y for item in self._items], y)
            try:
                if self._items[bb].is_over_hover(x, y):
                    self._hover_box_ij = (bb, self._items[bb].hover(x))

            except IndexError:
                # if last index
                pass

        if hovered[0] != self._hover_box_ij:
            hovered[0] = self._hover_box_ij
            noticeboard.refresh.push_change()

klossy = Properties_Panel()

