from fonts import fonttable

class StyleErrors(object):
    def __init__(self):
        self.missing = {}
        self.tally = {}
        self.first = ()
    
    def add_style_error(self, style, line):
        if style not in self.tally:
            self.tally[style] = []
        self.tally[style].append(line)
        self.tally[style].sort()
    
    def update(self, linenumber):
        self.missing = { k: [l for l in v if l < linenumber] for k, v in self.missing.items() }
        self.missing = { k: v for k, v in self.missing.items() if v }
        for k, v in self.tally.items():
            if k in self.missing:
                self.missing[k] += v
            else:
                self.missing[k] = v
        self.tally = {}

        if self.missing:
            ky = min(self.missing, key = lambda k: min(self.missing[k]))
            self.first = (ky, self.missing[ky])
        else:
            self.first = ()
    
    def new_error(self, reference=[()]):

        if self.first != reference[0]:
            reference[0] = self.first
            return True
        else:
            return False
        FT_Exception

styleerrors = StyleErrors()

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
        cr.set_font_size(14)
        cr.set_font_face(fonttable.table.get_font('_interface:STRONG')['font'])
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
"""
class Error_noticeboard(object):
    def __init__(self):
        self.new = False
        self.errors = []
    
    def push_new(self, name, subtitle):
        self.errors.append((name, subtitle))
        self.new = True
    
    def is_new(self):
        if self.new:
            return True
"""    

        
