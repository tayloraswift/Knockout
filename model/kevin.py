from copy import deepcopy
import html, itertools

def serialize(text):
    b = deepcopy(text)
    for e, entity in enumerate(b):
        if not isinstance(entity, str):
            if entity[0] == '<f>':
                if entity[1] == 'emphasis':
                    b[e] = '<em>'
                elif entity[1] == 'strong':
                    b[e] = '<strong>'
                else:
                    b[e] = '<f class="' + entity[1] + '">'
            
            elif entity[0] == '</f>':
                if entity[1] == 'emphasis':
                    b[e] = '</em>'
                elif entity[1] == 'strong':
                    b[e] = '</strong>'
                else:
                    b[e] = '</f class="' + entity[1] + '">'
            
            elif entity[0] == '<p>':
                if entity[1] != 'body':
                    b[e] = '<p class="' + entity[1] + '">'
                else:
                    b[e] = '<p>'

        elif entity == '<':
            b[e] = '&lt;'
        elif entity == '>':
            b[e] = '&gt;'

    return ''.join(b)

def deserialize(string):
    b = list(string)
    while True:
        try:
            opentag = b.index('<')
            closetag = b.index('>')

        except ValueError:
            break
        entity = ''.join(b[opentag + 1:closetag])
        
        if entity == 'p':
            entity = ('<p>', 'body')
        elif entity == '/p':
            entity = '</p>'
        elif entity == 'em':
            entity = ('<f>', 'emphasis')
        elif entity == '/em':
            entity = ('</f>', 'emphasis')
        elif entity == 'strong':
            entity = ('<f>', 'strong')
        elif entity == '/strong':
            entity = ('</f>', 'strong')

        else:
            tag = entity.split()[0]

            entity = ' '.join(entity.split())
            try:
                equals = entity.index('=')

                style = entity[equals + 1:closetag]
                style = style.partition('"')[-1].rpartition('"')[0]

                entity = ('<' + tag + '>', style)
            except ValueError:
                entity = '<' + tag + '>'
        
        del b[opentag:closetag + 1]
        b.insert(opentag, entity)

    d = []
    for k, g in [(k, list(g)) for k, g in itertools.groupby(b, key=lambda e: 1 if len(e) != 1 else 2 if e == '\u000A' else 0)]:
        if k == 0:
            d += list(html.unescape(''.join(g)))
        elif k == 1:
            d += g
        elif k == 2:
            d += ['</p>', ('<p>', 'body')]

    return d
