import bisect
import itertools

from state import constants, contexts, noticeboard
from style import styles
from interface import kookies, ui
from edit import ops, caramel, cursor
from model import meredith
from IO import un

def _create_f_field(TYPE, x, y, width, attribute, after, name='', **kwargs):
    if TYPE == kookies.Checkbox:
        z_y = y
    else:
        z_y = y - 7
    V_A = lambda A: styles.PARASTYLES.active.layerable.active.F.attributes[A] if A in styles.PARASTYLES.active.layerable.active.F.attributes else contexts.Fontstyle.fontstyle[A]
    ZI = kookies.Z_indicator(x, y, 10, height=24, 
            get_projection = lambda: contexts.Fontstyle.fontstyle, 
            get_attributes = lambda LIB: LIB.active.F.attributes, 
            A = attribute, 
            copy_value = lambda A: ops.f_set_attribute(V_A(A), A), 
            library=styles.PARASTYLES.active.layerable,
            before=un.history.save, after= lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), contexts.Text.update_force()))
    return [ZI, TYPE(x + 25, z_y, width - 25,
            callback= ops.f_set_attribute, 
            value_acquire = V_A,
            params = (attribute,), 
            before=un.history.save,
            after=after,
            name=name, **kwargs)]
            
def _create_p_field(TYPE, x, y, width, attribute, after, name='', **kwargs):
    if TYPE == kookies.Checkbox:
        z_y = y
    else:
        z_y = y - 7
    V_A = lambda A: styles.PARASTYLES.active.attributes[A] if A in styles.PARASTYLES.active.attributes else contexts.Parastyle.parastyle[A]
    ZI = kookies.Z_indicator(x, y, 10, height=24, 
            get_projection = lambda: contexts.Parastyle.parastyle, 
            get_attributes = lambda LIB: LIB.active.attributes, 
            A = attribute, 
            copy_value = lambda A: ops.p_set_attribute(V_A(A), A), 
            library=styles.PARASTYLES, 
            before=un.history.save, after= lambda: (styles.PARASTYLES.update_p(), meredith.mipsy.recalculate_all(), contexts.Text.update_force()))
    return [ZI, TYPE(x + 25, z_y, width - 25,
            callback = ops.p_set_attribute, 
            value_acquire = V_A,
            params = (attribute,), 
            before=un.history.save,
            after=after,
            name=name, **kwargs)]

class _F_preview(kookies.Heading):
    def __init__(self, x, y, width, height, text, f):
        self._F = f
        self._text = text
        kookies.Heading.__init__(self, x, y, width, height, text, font=self._F, fontsize = 15)

    def _SYNCHRONIZE(self):
        del self._texts[0]
        self._add_static_text(self._x, self._y + 16, self._text, fontsize=15)

    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0,0,0)
        
        cr.set_font_size(15)
        cr.set_font_face(self.font.u_font)
        cr.show_glyphs(self._texts[0])


class _MULTI_COLUMN(object):
    def __init__(self, * args):
        BB = [W.bounding_box() for W in args]
        self.partitions = [(BB[i][1] + BB[i + 1][0]) // 2 for i in range(len(BB) - 1)]
        self.y = max((B[3] for B in BB))
        
        self.draw = lambda cr: None
        self._SYNCHRONIZE = lambda: None

def _columns(columns):
    return [_MULTI_COLUMN( * columns), * columns]

# do not instantiate directly, requires a _reconstruct
class _Properties_panel(ui.Cell):
    def __init__(self, tabs = (), default=0, partition=1 ):
        
        self._partition = partition
        
        self._dy = 0
        width = 140
        self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[partition] - width)//2 , 20, width, 30, default=default, callback=self._tab_switch, signals=tabs)
        self._tab = tabs[default][0]
        
        self._reconstruct()

    def _tab_switch(self, name):
        if self._tab != name:
            self._tab = name
            self._reconstruct()
        
    def _stack(self, y):
        self._rows = [item.y for item in self._items]
        self._total_height = y

    def _stack_bisect(self, x, y):
        i = bisect.bisect(self._rows, y)
        try:
            item = self._items[i]
        except IndexError:
            i -= 1
            item = self._items[i]
        
        if isinstance(item, _MULTI_COLUMN):
            i += bisect.bisect(item.partitions, x) + 1
        return i

    def refresh(self):
        meredith.mipsy.recalculate_all() # must come before because it rewrites all the paragraph styles
        self._reconstruct()
    
    def synchronize(self):
        contexts.Text.update_force()
        for item in self._items:
            item._SYNCHRONIZE()
        
    def render(self, cr, h, k):
        width = h - constants.UI[self._partition]
        # DRAW BACKGROUND
        cr.rectangle(0, 0, 
                width, 
                k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        if noticeboard.refresh_properties_stack.should_refresh():
            mode = noticeboard.refresh_properties_type.should_refresh()
            if mode[0]:
                self._swap_reconstruct(mode[1])
            else:
                self._reconstruct()
        
        cr.save()
        cr.translate(0, self._dy)
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        
        cr.restore()
        
        # scrollbar
        if self._total_height > k:
            factor = k / self._total_height * (k - 20)
            top = -self._dy / self._total_height * (k - 20)
            cr.rectangle(width - 10, top + 10, 3, factor)
            cr.set_source_rgba(0, 0, 0, 0.1)
            cr.fill()
        
        # DRAW SEPARATOR
        cr.rectangle(0, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
        
        self._K = k
    
    def key_input(self, name, char):
        if self._active_box_i is not None:
            if name == 'Return':
                self._items[self._active_box_i].defocus()
                self._active_box_i = None
            else:
                return self._items[self._active_box_i].type_box(name, char)
    
    def press(self, x, y, char):
        y -= self._dy
        
        b = None
        bb = self._stack_bisect(x, y)

        if self._items[bb].is_over(x, y):
            self._items[bb].focus(x, y)
            b = bb

        # defocus the other box, if applicable
        if b is None or b != self._active_box_i:
            if self._active_box_i is not None:
                self._items[self._active_box_i].defocus()
            self._active_box_i = b
            
    def press_motion(self, x, y):
        if self._active_box_i is not None and self._items[self._active_box_i].focus_drag(x):
            noticeboard.redraw_klossy.push_change()
    
    def hover(self, x, y, hovered=[None]):
        y -= self._dy
        
        self._hover_box_ij = (None, None)
        
        bb = self._stack_bisect(x, y)

        if self._items[bb].is_over_hover(x, y):
            self._hover_box_ij = (bb, self._items[bb].hover(x, y))

        if hovered[0] != self._hover_box_ij:
            hovered[0] = self._hover_box_ij
            noticeboard.redraw_klossy.push_change()

    def scroll(self, x, y, char):
        if y > 0:
            if self._dy >= -self._total_height + self._K:
                self._dy -= 22
                noticeboard.redraw_klossy.push_change()
        elif self._dy <= -22:
            self._dy += 22
            noticeboard.redraw_klossy.push_change()

def _print_counter(counter):
    items = [k.name if v == 1 else k.name + ' (' + str(v) + ')' for k, v in counter.tags.items() if v]
    if items:
        return ', '.join(items)
    else:
        return '{none}'

class Properties(_Properties_panel):
    def __init__(self, tabs = (), default=0, partition=1 ):
        self._reconstruct = self._reconstruct_text_properties
        
        _Properties_panel.__init__(self, tabs = tabs, default=default, partition=partition) 

    def _reconstruct_text_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        print('reconstruct')
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 110

        if self._tab == 'font':
            if styles.PARASTYLES.active is not None:
                
                self._items.append(kookies.Heading( 15, 70, 250, 30, ', '.join(T.name for T in styles.PARASTYLES.active.tags), upper=True))
                self._items.append(kookies.Ordered(15, y, 250, 300,
                            library = styles.PARASTYLES.active.layerable, 
                            display = _print_counter,
                            before = un.history.save, after = lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
                y += 300
                
                if styles.PARASTYLES.active.layerable.active is not None:
                    self._items.append(kookies.Counter_editor(15, y, 250, 150, (125, 28),
                                get_counter = lambda: styles.PARASTYLES.active.layerable.active.tags,
                                superset = styles.FTAGS,
                                before = un.history.save, after = lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), self.synchronize())))
                    y += 150

                    _after_ = lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), contexts.Fontstyle.update(cursor.fcursor.styling_at()[1]), self._reconstruct())
                    if styles.PARASTYLES.active.layerable.active.F is None:
                        self._items.append(kookies.New_object_menu(15, y, 250,
                                    value_push = ops.link_fontstyle, 
                                    library = styles.FONTSTYLES,
                                    TYPE = styles.DB_Fontstyle,
                                    before = un.history.save, after = _after_, name='FONTSTYLE', source=self._partition))
                    else:
                        self._items.append(kookies.Object_menu(15, y, 250,
                                    value_acquire = lambda: styles.PARASTYLES.active.layerable.active.F, 
                                    value_push = ops.link_fontstyle, 
                                    library = styles.FONTSTYLES, 
                                    before = un.history.save, after = _after_, name='FONTSTYLE', source=self._partition))

                        y += 55
#                        self._items.append(_F_preview( 16, y, 250, 0, 'Preview  ( ' + key.name + ' )', key ))
#                        y += 30
                        self._items += _columns(_create_f_field(kookies.Blank_space, 15, y, 250, 'path', after=self.synchronize, name='FONT FILE'))
                        y += 45
                        self._items += _columns(_create_f_field(kookies.Numeric_field, 15, y, 250, 'fontsize', after=self.synchronize, name='FONT SIZE'))
                        y += 45
                        self._items += _columns(_create_f_field(kookies.Numeric_field, 15, y, 250, 'tracking', after=self.synchronize, name='TRACKING'))
                        y += 45
                        self._items += _columns(_create_f_field(kookies.Numeric_field, 15, y, 250, 'shift', after=self.synchronize, name='VERTICAL SHIFT'))
                        y += 45
                        self._items += _columns(_create_f_field(kookies.Checkbox, 15, y, 250, 'capitals', after=self.synchronize, name='CAPITALS'))
                        y += 45
                        self._items += _columns(_create_f_field(kookies.RGBA_field, 15, y, 250, 'color', after=self.synchronize, name='COLOR'))
                        y += 45
            else:
                self._items.append(kookies.Heading( 15, 90, 250, 30, '', upper=True))
        
        elif self._tab == 'paragraph':
            self._items.append(kookies.Heading( 15, 70, 250, 30, ', '.join(T.name if V == 1 else T.name + ' (' + str(V) + ')' for T, V in contexts.Text.paragraph.P.items() if V), upper=True))

            self._items.append(kookies.Para_control_panel(15, y, 250, 280, 
                    paragraph = contexts.Text.paragraph, 
                    display = _print_counter,
                    library = styles.PARASTYLES,
                    before = un.history.save, after = lambda: (styles.PARASTYLES.update_p(), meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
            y += 280
            
            if styles.PARASTYLES.active is not None:
                self._items.append(kookies.Counter_editor(15, y, 250, 150, (125, 28),
                            get_counter = lambda: styles.PARASTYLES.active.tags,
                            superset = styles.PTAGS,
                            before = un.history.save, after = lambda: (styles.PARASTYLES.update_p(), meredith.mipsy.recalculate_all(), self.synchronize())))
                y += 150
                
                self._items += _columns(_create_p_field(kookies.Numeric_field, 15, y, 255, 'leading', after=self.synchronize, name='LEADING'))
                y += 45

                self._items += _columns(_create_p_field(kookies.Integer_field, 15, y, 255, 'align', after=self.synchronize, name='ALIGN'))
                y += 45

                self._items += _columns(_create_p_field(kookies.Binomial_field, 15, y, 145, 'indent', after=self.synchronize, name='INDENT', letter='K') +
                                _create_p_field(kookies.Enumerate_field, 175, y, 95, 'indent_range', after=self.synchronize, name='FOR LINES'))
                y += 45

                self._items += _columns(_create_p_field(kookies.Numeric_field, 15, y, 120, 'margin_left', after=self.synchronize, name='SPACE LEFT') + 
                                _create_p_field(kookies.Numeric_field, 150, y, 120, 'margin_right', after=self.synchronize, name='SPACE RIGHT'))
                y += 45

                self._items += _columns(_create_p_field(kookies.Numeric_field, 15, y, 120, 'margin_top', after=self.synchronize, name='SPACE BEFORE') +
                                _create_p_field(kookies.Numeric_field, 150, y, 120, 'margin_bottom', after=self.synchronize, name='SPACE AFTER'))
                y += 45

                self._items += _columns(_create_p_field(kookies.Checkbox, 15, y, 100, 'hyphenate', after=self.synchronize, name='HYPHENATE'))
                y += 45
                
        
        elif self._tab == 'tags':
            self._items.append(kookies.Heading( 15, 70, 250, 30, '', upper=True))
            
            self._items.append(kookies.Unordered( 15, y, 200, 200,
                        library = styles.PTAGS, 
                        display = lambda l: l.name,
                        before = un.history.save, after = lambda: (meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
            
            y += 200
            if styles.PTAGS.active is not None:
                self._items.append(kookies.Blank_space(15, y, width=250, 
                        callback = lambda * args: styles.PTAGS.active.rename( * args), 
                        value_acquire = lambda: styles.PTAGS.active.name, 
                        before=un.history.save, after=self.synchronize, name='TAG NAME'))
            y += 60
            
            self._items.append(kookies.Unordered( 15, y, 200, 200,
                        library = styles.FTAGS, 
                        display = lambda l: l.name,
                        before = un.history.save, after = lambda: (meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
            
            y += 200
            if styles.FTAGS.active is not None:
                self._items.append(kookies.Blank_space(15, y, width=250, 
                        callback = lambda * args: styles.FTAGS.active.rename( * args), 
                        value_acquire = lambda: styles.FTAGS.active.name, 
                        before=un.history.save, after=self.synchronize, name='TAG NAME'))
            
        elif self._tab == 'page':
            self._items.append(kookies.Heading( 15, 70, 250, 30, '', upper=True))
            self._items.append(kookies.Integer_field( 15, y, 250, 
                        callback = meredith.page.set_width,
                        value_acquire = lambda: meredith.page.WIDTH,
                        name = 'WIDTH' ))
            
            y += 45
            self._items.append(kookies.Integer_field( 15, y, 250,
                        callback = meredith.page.set_height,
                        value_acquire = lambda: meredith.page.HEIGHT,
                        name = 'HEIGHT' ))
            y += 45
        
        self._stack(y)

    def _reconstruct_channel_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        c = caramel.delight.C()
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 110
        
        self._items.append(kookies.Heading( 15, 70, 250, 30, 'Channel ' + str(c), upper=True))
        
        if self._tab == 'channels':
            if c is not None:
                self._items.append(kookies.Integer_field( 15, y, 250, 
                        callback = lambda page, C: (caramel.delight.TRACT.channels.channels[C].set_page(page), caramel.delight.TRACT.deep_recalculate()), 
                        params = (c,),
                        value_acquire = lambda C: str(caramel.delight.TRACT.channels.channels[C].page),
                        name = 'PAGE' ))
                y += 30
            
        self._stack(y)
        
    def _swap_reconstruct(self, to):
        width = 160

        if to == 'text':
            tabs = (('page', 'M'), ('tags', 'T'), ('paragraph', 'P'), ('font', 'F'), ('pegs', 'G'))
            default = 2
            self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[self._partition] - width)//2 , 20, width, 30, default=default, callback=self._tab_switch, signals=tabs)
            self._tab = tabs[default][0]
            self._reconstruct = self._reconstruct_text_properties

        elif to == 'channels':
            tabs = (('channels', 'C'), ('', '?'))
            default = 0
            self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[self._partition] - width)//2 , 20, width, 30, default=default, callback=self._tab_switch, signals=tabs)
            self._tab = tabs[default][0]
            self._reconstruct = self._reconstruct_channel_properties
        
        self._reconstruct()
