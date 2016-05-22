from fonts.interfacefonts import ISTYLES

compose_keys = set(('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Caps_Lock', 'Escape', 'Alt_L', 'Alt_R', 'Super_L'))

sequences = {}

def _read_xcompose(compose_file):
    S = {}
    for entry in compose_file:
        entry = entry.decode("utf-8")
        if entry[0] == '<':
            colon = entry.find(':')

            i = entry[colon:].find('"') + colon + 1
            j = entry[i:].find('"') + i
            
            try:
                name = entry[j + 1:].split()[0]
            except IndexError:
                name = ''

            S[tuple( [trim[1:-1] for trim in entry[:colon].split()] )] = (name, entry[i:j])
    return S

with open('libraries/XCompose/Compose.txt', 'rb') as F:
    sequences.update(_read_xcompose(F))
with open('data/compose/add.txt', 'rb') as F:
    sequences.update(_read_xcompose(F))

class Compositor(object):
    def __init__(self):
        self._sequence = []
        self._char_sequence = []
        self._b = False
    
    def compose(self, compose):
        self._sequence = [compose]
        self._char_sequence = []
        self._b = True
    
    def __bool__(self):
        return self._b
    
    def key_input(self, name, char, key_input):
        self._sequence.append(name)
        self._char_sequence.append(char)
        
        # check if it matches a sequence
        current = tuple(self._sequence)

        if current in sequences:
            composition = sequences[current]
            # prevent a disaster
            if composition[0] == 'backslash':
                composition = ('backslash', '\\')
        else:
            # if there is no chance of finding a composition
            composition = (name, char)
            for key in sequences.keys():
                if current == key[:len(current)]:
                    composition = False
                    
        if composition:
            self.__init__()
            key_input( * composition )

    def draw(self, cr):
        if self._b:
            cr.set_source_rgba(0, 0, 0, 0.8)
            font = ISTYLES[('strong',)]
            cr.set_font_size(font['fontsize'])
            cr.set_font_face(font['font'])
            cr.move_to(130, 40)
            cr.show_text('X Composition: ' + ' '.join(self._char_sequence))
