from itertools import chain
from random import random, uniform
from math import sin, cos, pi

from os.path import isfile

import cairo

from fonts.interfacefonts import ISTYLES

from interface.base import text, show_text

from state.constants import window

splash_accent = 1, 0, 0.12

def make_rects(glyphs, y, fontsize, tracking, dy):
    height   = int(round(fontsize*1.7))
    tracking = int(round(tracking*0.5))
    xb = chain((k[1] for k in glyphs[2]), (glyphs[2][0][1] + glyphs[3],))
    
    extraspace = len(glyphs[2])*tracking
    x = int(round(next(xb) - extraspace))
    
    for (i, x1, _), x2 in zip(glyphs[2], xb):
        y1 = int(round(y + (2*random() - 1)*dy))
        width = int(round(x2 - x1 + 2*tracking))
        yield (x, y1, width, height), (i, x + tracking, y1 + (height + 0.7*fontsize)*0.5)
        x    +=  width

def make_snow(x, y, rx, ry, n):
    _2pi = 2*pi
    for i in range(n):
        t = uniform(0, _2pi)
        r = random()
        yield x + rx*r*cos(t), y + ry*r*sin(t), 4*random()*(1.5 - r), 0, _2pi

def get_recent(location):
    if isfile(location):
        with open(location, 'r') as F:
            recent = list(filter(isfile, (f.strip() for f in F.readlines())))
    else:
        recent = False
    if not recent:
        recent = ['test.html']
    return recent
    
class Recent(object):
    def __init__(self, location):
        self.font = ISTYLES[()]
        self.linespacing = 20
        self.recent   = get_recent(location)
        self.location = location
        self.add()
    
    def set_reload_func(self, reload_func):
        self.reload_func = reload_func
    
    def add(self, name=None):
        if name is not None:
            if name in self.recent:
                self.recent.remove(name)
            self.recent.insert(0, name)
            del self.recent[6:]
            with open(self.location, 'w') as F:
                F.write('\n'.join(self.recent))
                F.write('\n')
        
        else:
            del self.recent[6:]
        self.recent_links = list(self.arrange_recent(10, 0))
    
    def arrange_recent(self, x, y):
        linespacing = self.linespacing
        for i, recent in enumerate(self.recent):
            yield text(x, y + (i + 1)*linespacing, recent, self.font)
    
    def hover(self, y):
        i = int(y//self.linespacing)
        if i < len(self.recent):
            return i
        else:
            return None
    
    def press(self, y):
        i = self.hover(y)
        if i is not None:
            name = self.recent[i]
            self.reload_func(name)
            self.add(name)
    
    def draw(self, cr, hover):
        for i, link in enumerate(self.recent_links):
            if i == hover:
                cr.set_source_rgba( * splash_accent )
            else:
                cr.set_source_rgba(0, 0, 0)
            show_text(cr, link)
    
class Splash(object):
    def __init__(self, recent, queue_draw, h=400, k=300):
        self.queue_draw  = queue_draw
        
        self.h    = h
        self.k    = k
        self.x0   = int((window.get_h() - h)*0.5)
        self.y0   = int((window.get_k() - k)*0.5)
        self.x_center  = int(h*0.5)
        
        self.HOV = None,
        
        fontsize  = 48
        logo = text(self.x_center, 0, 'KNOCKOUT', ISTYLES[('splash',)], fontsize=fontsize, align=0, grid=True)

        self.rectangles, sorts = zip( * make_rects(logo, 50, fontsize, 10, 20) )
        self.sorts = logo[0], logo[1], sorts
        
        self.snow = list(make_snow(self.x_center, 100, h*0.8, k*0.8, 220))
        
        self._recent_y = 160
        self.recent = recent
    
    def get_recent(self, location):
        if isfile(location):
            with open(location, 'r') as F:
                recent = list(filter(isfile, (f.strip() for f in F.readlines())))
        else:
            recent = False
        if not recent:
            recent = ['test.html']
        else:
            del recent[6:]
        return recent
    
    def arrange_recent(self, x, y, linespacing):
        for i, recent in enumerate(self.recent):
            yield text(x, y + i*linespacing, recent, self.font)
    
    def hover(self, x, y):
        x -= self.x0
        y -= self.y0
        if x > self.x_center and y >= self._recent_y:
            HOV = 1, self.recent.hover(y - self._recent_y)
        else:
            HOV = None,
        if HOV != self.HOV:
            self.HOV = HOV
            self.queue_draw()
        return x, y
    
    def press(self, x, y):
        x, y = self.hover(x, y)
        if self.HOV[0] == 1:
            self.recent.press(y - self._recent_y)
    
    def draw(self, cr):
        cr.translate(self.x0, self.y0)
        
        cr.push_group()
        
        #cr.rectangle(-2, 2, self.h, self.k)
        #cr.set_source_rgba(0, 0, 0, 0.6)
        #cr.fill()
        
        cr.set_operator(cairo.OPERATOR_SOURCE)
        
        #cr.rectangle(0, 0, self.h, self.k)
        #cr.set_source_rgba(1, 1, 1, 0.9)
        #cr.fill()

        for rectangle in self.rectangles:
            cr.rectangle( * rectangle )
        for snowflake in self.snow:
            cr.arc( * snowflake )
            cr.close_path()
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        
        cr.fill_preserve()
        cr.pop_group_to_source()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.paint()
        
        cr.set_source_rgba( * splash_accent )
        cr.set_operator(cairo.OPERATOR_ADD)
        cr.fill()
        cr.set_operator(cairo.OPERATOR_OVER)
        
        cr.set_source_rgba(1, 1, 1)
        show_text(cr, self.sorts)
        
        cr.save()
        cr.translate(self.x_center, self._recent_y)
        if self.HOV[0] == 1:
            rh = self.HOV[1]
        else:
            rh = None
        self.recent.draw(cr, rh)
        cr.restore()
