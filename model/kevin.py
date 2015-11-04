from copy import deepcopy

def serialize(text):
    b = deepcopy(text)
    for e, entity in enumerate(b):
        if not isinstance(entity, str):
            if entity[0] == '<f>':
                b[e] = '<f class="' + entity[1] + '">'

            elif entity[0] == '<p>':
                if entity[1] != 'body':
                    b[e] = '<p class="' + entity[1] + '">'
                else:
                    b[e] = '<p>'
            
            elif entity[0] == '</f>':
                b[e] = '</f class="' + entity[1] + '">'

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
            entity = ['<p>', 'body']
        elif entity == '/p':
            entity = '</p>'
        elif entity == 'em':
            entity = ['<f>', 'emphasis']
        elif entity == '/em':
            entity = ['</f>', 'emphasis']
        elif entity == 'strong':
            entity = ['<f>', 'strong']
        elif entity == '/strong':
            entity = ['</f>', 'strong']

        else:
            tag = entity.split()[0]

            entity = ' '.join(entity.split())
            try:
                equals = entity.index('=')

                style = entity[equals + 1:closetag]
                style = style.partition('"')[-1].rpartition('"')[0]

                entity = ['<' + tag + '>', style]
            except ValueError:
                entity = '<' + tag + '>'
        
        
        
        
        del b[opentag:closetag + 1]
        b.insert(opentag, entity)
    
    d = []
    for i, e in enumerate(b):
        if e == '\u000A':
            if b[i - 1] != '\u000A':
                d += ['</p>', ['<p>', 'body']]
        else:
            d += [e]

    return d
