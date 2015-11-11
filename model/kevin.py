from copy import deepcopy
import html

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
    
    segments = []
    CH = False
    i = 0
    for j, e in enumerate(b):
        if len(e) == 1 and e != '\u000A':
            if not CH:
                i = j
                CH = True
        else:
            if CH:
                segments.append((True, ''.join(b[i:j])))
                CH = False
            
            if e == '\u000A':
                if b[j - 1] != '\u000A':
                    segments.append((False, '</p>'))
                    segments.append((False, ('<p>', 'body')))
            else:
                segments.append((False, e))

    if len(b[-1]) == 1:
        segments.append((True, ''.join(b[i:])))
    
    d = []
    for segment in segments:
        if segment[0]:
            d += list(html.unescape(segment[1]))
        else:
            d.append(segment[1])

    return d
