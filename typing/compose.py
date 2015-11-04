sequences = {}
with open('/usr/share/X11/locale/en_US.UTF-8/Compose', 'rb') as compose_file:
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

            sequences[tuple( [trim[1:-1] for trim in entry[:colon].split()] )] = (name, entry[i:j])

#print(sequences)
class Composition(object):
    def __init__(self, compose):
        self._sequence = [compose]
    
    def key_input(self, name, char):
        self._sequence.append(name)
        
        # check if it matches a sequence
        current = tuple(self._sequence)
        print(current)
        if current in sequences:
            print('found')
            composition = sequences[current]
        else:
            # if there is no chance of finding a composition
            composition = (name, char)
            for key in sequences.keys():
                if current == key[:len(current)]:
                    composition = False
        return composition
