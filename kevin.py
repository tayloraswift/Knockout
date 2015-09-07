import copy

def serialize(text):
    b = copy.deepcopy(text)
    print(b)
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
    print(b)
    print (''.join(b))
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
                print(style)

                entity = ['<' + tag + '>', style]
            except ValueError:
                entity = '<' + tag + '>'
        
        
        
        
        del b[opentag:closetag + 1]
        b.insert(opentag, entity)

    return b

#print (deserialize('< p class=  "h1">We begin our story in New York. There once was a girl known by everyone and no one. Her heart belonged to someone who couldn’t stay. </p><p>They loved each other recklessly.</p><p>They paid the price. She <em>danced</em> to forget him. He drove past her street every night. <em>She made <strong>friends and enemies</em>. He only</strong> saw her in his dreams. Then one day he came back. Timing is a funny thing. And everyone was watching. She lost him but she found herself and somehow that was everything.</p>'))
#print (serialize([['<p>', 'poptart'], 't', 'h', 'e', 'r', 'e', ' ', 'o', 'n', 'c', 'e', ' ', 'w', 'a', 's', ' ', 'a', ' ', '<br>', 'g', 'i', 'r', 'l', '</p>', ['<p>', 'body'], 'k', 'n', 'o', 'w', 'n', ' ', 'b', 'y', ' ', 'e', 'v', 'e', 'r', 'y', 'o', 'n', 'e', '</p>']))

"""
        try:
            equals = entity.index('=')
            closetag = entity.index('>')

            style = entity[equals + 2:closetag - 1]

            entity = ['<' + entity[1] + '>', ''.join(style)]
        except ValueError:
            if entity[1] == 'p':
                entity = ['<p>', 'body']
            else:
                entity = ''.join(entity)
                
            if entity == '<em>':
                entity = ['<f>', 'emphasis']
            elif entity == '</em>':
                entity = '</f>'
"""
