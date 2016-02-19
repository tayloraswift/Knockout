import bisect
from itertools import chain

from state import constants, contexts, noticeboard
from style import styles
from interface import kookies, ui, source
from edit import ops, caramel, cursor
from model import meredith
from IO import un, kevin

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

def _stack_row(i, row, y, gap, width, factory, after):
    width += 10
    divisions = [r[0] * width for r in row]
    divisions = zip(divisions, divisions[1:] + [width], row)
    return _columns(chain.from_iterable(factory(TYPE, 15 + a, y + i*gap, b - a - 10, A, after=after, name=name, **dict(kwargs)) for a, b, (factor, TYPE, A, name, * kwargs) in divisions))

def _stack_properties(factory, after, y, gap, width, L):
    return chain.from_iterable(_stack_row(i, row, y, gap, width, factory, after) for i, row in enumerate(L))

class _MULTI_COLUMN(object):
    def __init__(self, * args):
        BB = [W.bounding_box() for W in args]
        self.partitions = [(BB[i][1] + BB[i + 1][0]) // 2 for i in range(len(BB) - 1)]
        self.y = max((B[3] for B in BB))
        
        self.draw = lambda cr: None
        self._SYNCHRONIZE = lambda: None

def _columns(columns):
    columns = list(columns)
    return [_MULTI_COLUMN( * columns), * columns]

# do not instantiate directly, requires a _reconstruct
class _Properties_panel(ui.Cell):
    def __init__(self, mode, partition=1 ):
        self._partition = partition
        self.hresize()
        self._swap_reconstruct(mode)
    
    def hresize(self):
        self._width = constants.window.get_h() - constants.UI[self._partition]
        self._KW = self._width - 50

    def _tab_switch(self, name):
        if self._tab != name:
            self._dy = 0
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
            return self._items[i + bisect.bisect(item.partitions, x) + 1]
        else:
            return item

    def refresh(self):
        meredith.mipsy.recalculate_all() # must come before because it rewrites all the paragraph styles
        self._reconstruct()
    
    def synchronize(self):
        contexts.Text.update_force()
        for item in self._items:
            item._SYNCHRONIZE()
        
    def render(self, cr, h, k):
        width = self._width
        # DRAW BACKGROUND
        cr.rectangle(0, 0, width, k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        if noticeboard.refresh_properties_stack.should_refresh():
            mode = noticeboard.refresh_properties_type.should_refresh()
            if mode[0]:
                self._swap_reconstruct(mode[1])
            else:
                self._reconstruct()
        
        hover_box = self._hover_box_ij[0]

        cr.save()
        cr.translate(0, self._dy)
        for entry in self._items:
            if entry is hover_box:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        
        cr.restore()

        # tabstrip
        cr.rectangle(0, 0, width, 60)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        cr.rectangle(0, 60, width, 2)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
        if hover_box is self._tabstrip:
            self._tabstrip.draw(cr, hover=self._hover_box_ij)
        else:
            self._tabstrip.draw(cr)
        
        # scrollbar
        if self._total_height > k:
            factor = k / self._total_height * (k - 80)
            top = -self._dy / self._total_height * (k - 80)
            cr.rectangle(width - 10, top + 70, 3, factor)
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
        box = self._active_box_i
        if box is not None:
            if name == 'Return' and type(box) is not source.Rose_garden:
                box.defocus()
                self._active_box_i = None
            else:
                return box.type_box(name, char)
    
    def press(self, x, y, char):
        b = None
        if y < 60:
            box = self._tabstrip
        else:
            y -= self._dy
            box = self._stack_bisect(x, y)

        if box.is_over(x, y):
            box.focus(x, y)
            b = box

        # defocus the other box, if applicable
        if b is None or b is not self._active_box_i:
            if self._active_box_i is not None:
                self._active_box_i.defocus()
            self._active_box_i = b
            
    def press_motion(self, x, y):
        y -= self._dy
        if self._active_box_i is not None and self._active_box_i.focus_drag(x, y):
            noticeboard.redraw_klossy.push_change()
    
    def hover(self, x, y, hovered=[None]):
        if y < 60:
            box = self._tabstrip
        else:
            y -= self._dy
            box = self._stack_bisect(x, y)

        if box.is_over_hover(x, y):
            self._hover_box_ij = (box, box.hover(x, y))
        else:
            self._hover_box_ij = (None, None)

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
    def _reconstruct_text_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        print('reconstruct')
        
        self._items = []
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 110
        KW = self._KW
        tile = int(KW / (KW // 125))

        if self._tab == 'font':
            if styles.PARASTYLES.active is not None:
                
                self._items.append(kookies.Heading( 15, 70, KW, 30, ', '.join(T.name for T in styles.PARASTYLES.active.tags), upper=True))
                self._items.append(kookies.Ordered(15, y, KW, 300,
                            library = styles.PARASTYLES.active.layerable, 
                            display = _print_counter,
                            before = un.history.save, after = lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
                y += 300
                
                if styles.PARASTYLES.active.layerable.active is not None:
                    self._items.append(kookies.Counter_editor(15, y, KW, 150, (tile, 28),
                                get_counter = lambda: styles.PARASTYLES.active.layerable.active.tags,
                                superset = styles.FTAGS,
                                before = un.history.save, after = lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), self.synchronize())))
                    y += 150

                    _after_ = lambda: (styles.PARASTYLES.update_f(), meredith.mipsy.recalculate_all(), contexts.Fontstyle.update(cursor.fcursor.styling_at()[1]), self._reconstruct())
                    if styles.PARASTYLES.active.layerable.active.F is None:
                        self._items.append(kookies.New_object_menu(15, y, KW,
                                    value_push = ops.link_fontstyle, 
                                    library = styles.FONTSTYLES,
                                    TYPE = styles.DB_Fontstyle,
                                    before = un.history.save, after = _after_, name='FONTSTYLE', source=self._partition))
                    else:
                        self._items.append(kookies.Object_menu(15, y, KW,
                                    value_acquire = lambda: styles.PARASTYLES.active.layerable.active.F, 
                                    value_push = ops.link_fontstyle, 
                                    library = styles.FONTSTYLES, 
                                    before = un.history.save, after = _after_, name='FONTSTYLE', source=self._partition))

                        y += 55
                        props = [[(0, kookies.Blank_space, 'path', 'FONT FILE')],
                                [(0, kookies.Numeric_field, 'fontsize', 'FONT SIZE')],
                                [(0, kookies.Numeric_field, 'tracking', 'TRACKING')],
                                [(0, kookies.Numeric_field, 'shift', 'VERTICAL SHIFT')],
                                [(0, kookies.Checkbox, 'capitals', 'CAPITALS')],
                                [(0, kookies.RGBA_field, 'color', 'COLOR')]
                                ]
                        self._items.extend(_stack_properties(_create_f_field, self.synchronize, y, 45, KW, props))
                        y += 45*len(props)

            else:
                self._items.append(kookies.Heading( 15, 90, KW, 30, '', upper=True))
        
        elif self._tab == 'paragraph':
            self._items.append(kookies.Heading( 15, 70, KW, 30, ', '.join(T.name if V == 1 else T.name + ' (' + str(V) + ')' for T, V in contexts.Text.paragraph.P.items() if V), upper=True))

            self._items.append(kookies.Para_control_panel(15, y, KW, 280, 
                    paragraph = contexts.Text.paragraph, 
                    display = _print_counter,
                    library = styles.PARASTYLES,
                    before = un.history.save, after = lambda: (styles.PARASTYLES.update_p(), meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
            y += 280
            
            if styles.PARASTYLES.active is not None:
                self._items.append(kookies.Counter_editor(15, y, KW, 150, (tile, 28),
                            get_counter = lambda: styles.PARASTYLES.active.tags,
                            superset = styles.PTAGS,
                            before = un.history.save, after = lambda: (styles.PARASTYLES.update_p(), meredith.mipsy.recalculate_all(), self.synchronize())))
                y += 150

                props = [[(0, kookies.Numeric_field, 'leading', 'LEADING')],
                        [(0, kookies.Integer_field, 'align', 'ALIGN')],
                        [(0, kookies.Binomial_field, 'indent', 'INDENT', ('letter', 'K')) , (0.6, kookies.Enumerate_field, 'indent_range', 'FOR LINES')],
                        [(0, kookies.Numeric_field, 'margin_left', 'SPACE LEFT'), (0.5, kookies.Numeric_field, 'margin_right', 'SPACE RIGHT')],
                        [(0, kookies.Numeric_field, 'margin_top', 'SPACE BEFORE'), (0.5, kookies.Numeric_field, 'margin_bottom', 'SPACE AFTER')],
                        [(0, kookies.Checkbox, 'hyphenate', 'HYPHENATE')]
                        ]
                self._items.extend(_stack_properties(_create_p_field, self.synchronize, y, 45, KW, props))
                y += 45*len(props)
                
        
        elif self._tab == 'tags':
            self._items.append(kookies.Heading( 15, 70, KW, 30, '', upper=True))
            
            self._items.append(kookies.Unordered( 15, y, KW - 50, 200,
                        library = styles.PTAGS, 
                        display = lambda l: l.name,
                        before = un.history.save, after = lambda: (meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
            
            y += 200
            if styles.PTAGS.active is not None:
                self._items.append(kookies.Blank_space(15, y, width=KW, 
                        callback = lambda * args: styles.PTAGS.active.rename( * args), 
                        value_acquire = lambda: styles.PTAGS.active.name, 
                        before=un.history.save, after=self.synchronize, name='TAG NAME'))
            y += 60
            
            self._items.append(kookies.Unordered( 15, y, KW - 50, 200,
                        library = styles.FTAGS, 
                        display = lambda l: l.name,
                        before = un.history.save, after = lambda: (meredith.mipsy.recalculate_all(), self._reconstruct()), refresh = self._reconstruct))
            
            y += 200
            if styles.FTAGS.active is not None:
                self._items.append(kookies.Blank_space(15, y, width=KW, 
                        callback = lambda * args: styles.FTAGS.active.rename( * args), 
                        value_acquire = lambda: styles.FTAGS.active.name, 
                        before=un.history.save, after=self.synchronize, name='TAG NAME'))
            
        elif self._tab == 'page':
            self._items.append(kookies.Heading( 15, 70, KW, 30, '', upper=True))
            self._items.append(kookies.Integer_field( 15, y, 300, 
                        callback = meredith.page.set_width,
                        value_acquire = lambda: meredith.page.WIDTH,
                        name = 'WIDTH' ))
            
            y += 45
            self._items.append(kookies.Integer_field( 15, y, KW,
                        callback = meredith.page.set_height,
                        value_acquire = lambda: meredith.page.HEIGHT,
                        name = 'HEIGHT' ))
            y += 45
        
        elif self._tab == 'character':
            self._items.append(source.Rose_garden(10, y, width=KW + 10, 
                    e_acquire = lambda: cursor.fcursor.text[cursor.fcursor.i],
                    before = un.history.save, after = meredith.mipsy.recalculate_all))
            y = self._items[-1].bounding_box()[3]
        self._stack(y)

    def _reconstruct_channel_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        c = caramel.delight.C()
        
        self._items = []
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 110
        KW = self._KW
        
        self._items.append(kookies.Heading( 15, 70, KW, 30, 'Channel ' + str(c), upper=True))
        
        if self._tab == 'channels':
            if c is not None:
                self._items.append(kookies.Integer_field( 15, y, KW, 
                        callback = lambda page, C: (caramel.delight.TRACT.channels.channels[C].set_page(page), caramel.delight.TRACT.deep_recalculate()), 
                        params = (c,),
                        value_acquire = lambda C: str(caramel.delight.TRACT.channels.channels[C].page),
                        name = 'PAGE' ))
                y += 30
            
        self._stack(y)
        
    def _swap_reconstruct(self, to):
        width = 160

        if to == 'text':
            tabs = (('page', 'M'), ('tags', 'T'), ('paragraph', 'P'), ('font', 'F'), ('character', 'C'))
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
        
        self._dy = 0
        self._reconstruct()
