import kookies
import constants
import meredith

import bisect
import fonts

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
    def __init__(self, x, y, width, p, menu_callback, name=None):
        kookies.Object_menu.__init__(self, x, y, width, p, callback=self._push_pname, menu_callback=menu_callback, name=name, update=True)
        
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

        
    def draw(self, cr):
        cr.set_source_rgb(0,0,0)
        
        cr.set_font_size(15)
        cr.set_font_face(self.font.font)
        cr.show_glyphs(self._texts[0])

class Properties_Panel(object):
    def __init__(self):
        self._h = constants.windowwidth
        
        
        self._tabstrip = kookies.Tabs(self._h - constants.propertieswidth/2 - 50 , 50, 100, 30, callback=self._tab_switch, signals=['paragraph', 'font', '?'], strings=['P', 'F', '?'])
        self._tab = self._tabstrip.active_name()
        
        self.menu = None
        
        self.refresh_class(meredith.mipsy.glyph_at()[2])

    
    def refresh_class(self, p):
        
        self._items = [self._tabstrip]
        
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
            self._items.append(_Paragraph_style_menu(self._h - constants.propertieswidth + 15, y, 250, p[0], self._create_paragraph_style_menu, name='RENAME CLASS'))
            
            self._items.append(_Paragraph_leading_Field(self._h - constants.propertieswidth + 15, y + 45, 250, p[0], name='LEADING' ))
            self._items.append(_Paragraph_margin_Field(self._h - constants.propertieswidth + 15, y + 90, 250, p[0], name='BOTTOM MARGIN' ))
            pass
        
        self._active_box_i = None

    def _create_paragraph_style_menu(self):
        self.menu = kookies.Menu(self._h - constants.propertieswidth + 100, 150 + 18, 165, 30, self._menu_select_class, sorted(fonts.paragraph_classes.keys()) )
        
    def _menu_select_class(self, name):
        p = meredith.mipsy.glyph_at()[2]
        meredith.mipsy.change_paragraph_class(p[1], name)
        self.menu = None
        meredith.mipsy.rerender() # must come before because it rewrites all the paragraph styles
        self.refresh_class(meredith.mipsy.glyph_at()[2])
        return False
        
        
    def _tab_switch(self, name):
        self._tab = name
        self.refresh_class(meredith.mipsy.glyph_at()[2])
        print(self._tab)
        
    def resize(self, h, k):
        dx = h - self._h
        self._h = h
        for entry in self._items:
            entry.translate(dx)
    
    def render(self, cr):
        for entry in self._items:
            entry.draw(cr)
        if self.menu:
            self.menu.draw(cr)
    
    def key_input(self, name, char):
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
                border_status = self._items[bb].is_over(x, y)
                if border_status is not None:
                    x = border_status

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
    
    def hover(self, x, y):
        if self.menu is None or not self.menu.hover(x, y):
            bb = bisect.bisect([item.y for item in self._items], y)

            try:
                border_status = self._items[bb].is_over_hover(x, y)
                if border_status is not None:
                    self._items[bb].hover(x)
            except IndexError:
                pass
            
panel = Properties_Panel()
