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

        
