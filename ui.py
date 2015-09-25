import bisect
import array
import cairo
import math

class Button(object):
    def __init__(self, label, cb):
        self.label = label
        self.cb = cb
        self.r = 0.9
        self.g = 0.9
        self.b = 0.9
    def stack(self, x, y, width, height):
        self.x1 = x
        self.x2 = x + width
        self.y1 = y
        self.y2 = y + height
    def set_color(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    def draw(self, context, x, y):
        if self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2:
            context.set_source_rgba(self.r, self.g, self.b, 0.7)
        else:
            context.set_source_rgba(self.r, self.g, self.b, 1)
        context.rectangle(self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1)
        context.fill()
        context.move_to(self.x1, self.y2)
        context.set_source_rgb(0, 0, 0)
        context.show_text(self.label)

class Circle(object):
    def __init__(self, x, y, r, red=0, green=0, blue=0, alpha=1):
        self.x = x
        self.y = y
        self.r = r
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
    def move_to(self, x, y):
        self.x = x
        self.y = y
    def set_color(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
    def draw(self, cr):
        cr.set_source_rgba(self.red, self.green, self.blue, self.alpha)
        cr.arc(self.x, self.y, self.r, 0, 2*math.pi)
        cr.fill()

class Line(object):
    def __init__(self, points, r, g, b, a):
        self.points = points
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    
    def add_node(self, x, y, i=-1):
        if i >= 0:
            points.insert(i, [x, y])
        else:
            points.append([x, y])
    
    def replace_nodes(self, points):
        self.points = points

    def draw(self, cr, x, y):
        cr.set_source_rgba(self.r, self.g, self.b, self.a)
        cr.move_to(self.points[0][0], self.points[0][1])
        for point in self.points[1:]:
            cr.line_to(point[0], point[1])
            cr.set_line_width(2)
            cr.stroke()
                   

        
class Broken_bar(object):
    def __init__(self, x1, y1, x2, r, g, b, a, highlight=False):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1

        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
        self.highlight = highlight

    def draw(self, cr):
        cr.set_source_rgba(self.r, self.g, self.b, self.a)

        cr.rectangle(self.x1, self.y1, self.x2 - self.x1, 5)
        cr.clip()
        for f in range( (self.x2 - self.x1) //4):
            cr.move_to(self.x1 + 4*f, self.y1)
            if self.highlight:
                cr.rel_line_to(2, 0)
                cr.rel_line_to(-4, 7)
                cr.rel_line_to(-2, 0)
            else:
                cr.rel_line_to(1.5, 0)
                cr.rel_line_to(-4, 7)
                cr.rel_line_to(-1.5, 0)
            cr.close_path()

        cr.fill()
        cr.reset_clip()

class ErrorPanel(object):
    def __init__(self, speed):
        self.errorname = ''
        self.name = ''
        self.location = ''
        self.speed = speed
        self.phase = 0
    
    def update_message(self, error, name, location):
        self.errorname = error
        self.name = name
        self.location = location
    
    def increment(self):
        self.phase += 1

    def draw(self, cr, width):
        if self.phase >= 18:
            phase = 1
        else:
            phase = self.phase/18
        cr.set_source_rgb(1, 0.15, 0.2)
        cr.rectangle(100, phase*55 - 55, width - 100, 55)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, phase)
        cr.move_to(100 + 30, 20)
        cr.show_text(self.errorname + ': ' + self.name)
        
        cr.move_to(100 + 30, 40)
        cr.show_text(self.location)

class Panel(object):
    def __init__(self, width, buttons):
#        self.cc = context
        self.width = width
        self.buttons = buttons
        self.circles = []
        self.interactivelines = []
        self.brokenbars = []
        
        self.x = 0
        self.y = 0
        
#        self.buttonsx = []
#        self.buttonsy = []
        

#            self.buttonsx.append(b.x)
#            self.buttonsy.append(b.y)
#        buttons.sort(key = lambda k: k.x1)

    def update(self, x, y):
        self.x = x
        self.y = y


    def replace_brokenbars(self, bars):
        self.brokenbars = bars
    
    def is_clicked(self, x, y):
        
        clicked = None
        
        for button in self.buttons:
            if y >= button.y1:
                if y <= button.y2:
                    if x >= button.x1 and x <= button.x2:
                        clicked = button
                        break
        return clicked
        
    def draw(self, context):
        for i, b in enumerate(self.buttons):
            b.stack(20, i*40 + 100, 60, 20)
            b.draw(context, self.x, self.y)
        for c in self.circles:
            c.draw(context)
        for l in self.interactivelines:
            l.draw(context, self.x, self.y)
        for b in self.brokenbars:
            b.draw(context, self.x, self.y)
