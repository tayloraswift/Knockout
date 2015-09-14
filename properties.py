import textbox
import constants
import meredith

import bisect
import fonts

from freetype import ft_errors


_ui_font = fonts.paragraph_classes['_interface'].fontclasses[()]


class _Font_file_Field(textbox.Blank_Space):
    def __init__(self, x, y, width, p, f, name=None, update=False):
        # must be list
        self._text = list(fonts.paragraph_classes[p].fontclasses[f].path) + [None]
        self._previous = fonts.paragraph_classes[p].fontclasses[f].path
        
        self.p = p
        self.f = f
        
        self._callback = self._push_fontname

        if not fonts.paragraph_classes[self.p].fontclasses[self.f].path_valid:
            self.broken = True
        else:
            self.broken = False
            
        self._common(x, y, width, name, update)

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


   
class _Font_size_Field(textbox.Numeric_Field):
    def __init__(self, x, y, width, p, f, name=None, update=False):
        
        self.broken = False
        
        # must be list
        self._text = list(str(fonts.paragraph_classes[p].fontclasses[f].fontsize)) + [None]
        self._previous = str(fonts.paragraph_classes[p].fontclasses[f].fontsize)
        
        self.p = p
        self.f = f
        
        self._callback = self._push_fontsize
        
        self._common(x, y, width, name, update)
        

    def _push_fontsize(self, size):
        fonts.paragraph_classes[self.p].fontclasses[self.f].update_size(self._to_number(size))
        meredith.mipsy.rerender()

class _Font_tracking_Field(textbox.Numeric_Field):
    def __init__(self, x, y, width, p, f, name=None, update=False):
        
        self.broken = False
        
        # must be list
        self._text = list(str(fonts.paragraph_classes[p].fontclasses[f].tracking)) + [None]
        self._previous = str(fonts.paragraph_classes[p].fontclasses[f].tracking)
        
        self.p = p
        self.f = f
        
        self._callback = self._push_tracking
        
        self._common(x, y, width, name, update)
        

    def _push_tracking(self, tracking):
        fonts.paragraph_classes[self.p].fontclasses[self.f].update_tracking(self._to_number(tracking))
        meredith.mipsy.rerender()

class _Paragraph_leading_Field(textbox.Numeric_Field):
    def __init__(self, x, y, width, p, name=None, update=False):
        
        self.broken = False
        
        # must be list
        self._text = list(str(fonts.paragraph_classes[p].leading)) + [None]
        self._previous = str(fonts.paragraph_classes[p].leading)
        
        self.p = p
        
        self._callback = self._push_leading
        
        self._common(x, y, width, name, update)

    def _push_leading(self, leading):
        fonts.paragraph_classes[self.p].update_leading(self._to_number(leading))
        meredith.mipsy.rerender()

class _Paragraph_margin_Field(textbox.Numeric_Field):
    def __init__(self, x, y, width, p, name=None, update=False):
        
        self.broken = False
        
        # must be list
        self._text = list(str(fonts.paragraph_classes[p].margin_bottom)) + [None]
        self._previous = str(fonts.paragraph_classes[p].margin_bottom)
        
        self.p = p
        
        self._callback = self._push_margin
        
        self._common(x, y, width, name, update)

    def _push_margin(self, margin):
        fonts.paragraph_classes[self.p].update_margin(self._to_number(margin))
        meredith.mipsy.rerender()

class _Paragraph_style_menu(textbox.Object_Menu):
    def __init__(self, x, y, width, p, menu_callback, name=None, update=False):
        # must be list
        self._text = list(p) + [None]
        self._previous = p
        
        self.p = p
        
        self._callback = self._push_pname
        self._menu_callback = menu_callback
        
#        self.font = fonts.paragraph_classes['_interface'].fontclasses[('title',)]
        
        self.broken = False
            
        self._common(x, y, width, name, update)

    def _push_pname(self, name):

        fonts.paragraph_classes[name] = fonts.paragraph_classes.pop(self.p)
        meredith.mipsy.rename_paragraph_class(self.p, name)
        self.p = name
#        fonts.paragraph_classes[self.p].fontclasses[self.f].path_valid = True
        meredith.mipsy.rerender()



class _preview(textbox.heading):
    def __init__(self, x, y, width, text, p, f):
        
        self.x = x
        self.y = y
        self.width = width
        self._text = text
        
        self.p = p
        self.f = f
        
        self.font = fonts.paragraph_classes[self.p[0]].fontclasses[self.f]
        
        self._glyphs = []
        self._stamp_glyphs(_ui_font.fontsize/self.font.fontsize)
        self._anchor_0()
        
    def draw(self, cr):
        
        cr.set_source_rgb(0,0,0)
        cr.set_font_size(_ui_font.fontsize)
        cr.set_font_face(fonts.paragraph_classes[self.p[0]].fontclasses[self.f].font)
        cr.show_glyphs(self._glyphs)

class Properties_Panel(object):
    def __init__(self):
        self._h = constants.windowwidth
        
        
        self._tabstrip = textbox.Mode_Buttons(self._h - constants.propertieswidth/2 , 50, 100, 2, callback=self._tab_switch, names=['paragraph', 'font', '?'], labels=['P', 'F', '?'])
        self._tab = self._tabstrip.active_name()
        
        self.menu = None
        
        self.refresh_class(meredith.mipsy.glyph_at()[2])

    
    def refresh_class(self, p):
        
        self._items = [self._tabstrip]
        
        y = 150
        
        self._items.append(textbox.heading(self._h - constants.propertieswidth + 15, 100, 250, p[0]))

        if self._tab == 'font':
        
            for key, item in sorted(fonts.paragraph_classes[p[0]].fontclasses.items()):
                if key:
                    classname = 'CLASS: ' + ', '.join(key).upper()
                else:
                    classname = 'CLASS: NONE'
                self._items.append(_preview(self._h - constants.propertieswidth + 16, y, 250, classname, p, key ))
                self._items.append(_Font_file_Field(self._h - constants.propertieswidth + 15, y + 30, 250, p[0], key, name='FONT FILE' ))
                self._items.append(_Font_size_Field(self._h - constants.propertieswidth + 15, y + 70, 250, p[0], key, name='FONT SIZE' ))
                self._items.append(_Font_tracking_Field(self._h - constants.propertieswidth + 15, y + 110, 250, p[0], key, name='TRACKING' ))
                y += 180
        
        elif self._tab == 'paragraph':
            self._items.append(_Paragraph_style_menu(self._h - constants.propertieswidth + 15, y, 250, p[0], self._create_paragraph_style_menu, name='RENAME CLASS', update=True))
            
            self._items.append(_Paragraph_leading_Field(self._h - constants.propertieswidth + 15, y + 40, 250, p[0], name='LEADING' ))
            self._items.append(_Paragraph_margin_Field(self._h - constants.propertieswidth + 15, y + 80, 250, p[0], name='BOTTOM MARGIN' ))
        
        
        self._active_box_i = None

    def _create_paragraph_style_menu(self):
        self.menu = textbox.Menu(self._h - constants.propertieswidth + 100, 150 + 5, 165, 30, self._menu_select_class, sorted(fonts.paragraph_classes.keys()) )
        
    def _menu_select_class(self, name):
        p = meredith.mipsy.glyph_at()[2]
        meredith.mipsy.change_paragraph_class(p[1], name)
        self.menu = None
        meredith.mipsy.rerender() # must come before because it rewrites all the paragraph styles
        self.refresh_class(meredith.mipsy.glyph_at()[2])
        
        
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

            bb = bisect.bisect([item.y + 10 for item in self._items], y)

            try:
                if self._items[bb].y - y < 30:
                    border_status = self._items[bb].in_borders(x)
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
            bb = bisect.bisect([item.y + 10 for item in self._items], y)

            try:
                if self._items[bb].y - y < 30:
                    border_status = self._items[bb].hover_in_borders(x)
                    if border_status is not None:
                        x = border_status

                        self._items[bb].hover(x)
            except IndexError:
                pass
            
panel = Properties_Panel()
