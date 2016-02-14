def print_attrs(name, attrs):
    if attrs:
        return '<' + name + ' ' + ' '.join(A + '="' + repr(V)[1:-1] + '"' for A, V in attrs.items()) + '>'  
    else:
        return '<' + name + '>'
