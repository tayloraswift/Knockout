from copy import deepcopy
import html, itertools

from fonts import styles

def serialize(text):
    b = text.copy()
    for e, entity in enumerate(b):
        if not isinstance(entity, str):
            if entity[0] == '<f>':
                if entity[1].name == 'emphasis':
                    b[e] = '<em>'
                elif entity[1].name == 'strong':
                    b[e] = '<strong>'
                else:
                    b[e] = '<f class="' + entity[1].name + '">'
            
            elif entity[0] == '</f>':
                if entity[1].name == 'emphasis':
                    b[e] = '</em>'
                elif entity[1].name == 'strong':
                    b[e] = '</strong>'
                else:
                    b[e] = '</f class="' + entity[1].name + '">'
            
            elif entity[0] == '<p>':
                if entity[1].name != 'body':
                    b[e] = '<p class="' + entity[1].name + '">'
                else:
                    b[e] = '<p>'

            elif entity[0] == '<image>':
                b[e] = '<image data=' + repr(entity[1]) + '>'

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
            entity = ['<p>', styles.PARASTYLES['body'] ]
        elif entity == '/p':
            entity = '</p>'
        elif entity == 'em':
            entity = ('<f>', styles.TAGLIST.elements['emphasis'])
        elif entity == '/em':
            entity = ('</f>', styles.TAGLIST.elements['emphasis'])
        elif entity == 'strong':
            entity = ('<f>', styles.TAGLIST.elements['strong'])
        elif entity == '/strong':
            entity = ('</f>', styles.TAGLIST.elements['strong'])

        else:
            tag = entity.split()[0]

            entity = ' '.join(entity.split())
            try:
                equals = entity.index('=')

                data = entity[equals + 1:closetag]
                data = eval(data)
                
                if tag == 'p':
                    data = styles.PARASTYLES[data]
                
                elif tag in {'f', '/f'}:
                    data = styles.TAGLIST.elements[data]

                entity = ('<' + tag + '>', data)

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
            d += ['</p>', ['<p>', styles.PARASTYLES['body']]]

    return d
