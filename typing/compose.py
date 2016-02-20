from state import noticeboard

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
with open('libraries/XCompose/add.txt', 'rb') as F:
    sequences.update(_read_xcompose(F))

class Composition(object):
    def __init__(self, compose):
        self._sequence = [compose]
        self._char_sequence = ['X composition: ']
        noticeboard.composition_sequence = self._char_sequence[:]
    
    def key_input(self, name, char):
        self._sequence.append(name)
        self._char_sequence.append(char)
        
        noticeboard.composition_sequence = []
        
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
                    
                    noticeboard.composition_sequence = self._char_sequence[:]
                    
        return composition
