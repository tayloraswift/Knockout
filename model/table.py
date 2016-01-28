from model.wonder import character
from model.cat import typeset_liquid

def _bin(data, odelimit, cdelimit):
    for i, v in ((i, v) for i, v in enumerate(data) if character(v) == odelimit):
        try:
            j = data[i:].index(cdelimit) + i
        except ValueError:
            print('unclosed bin')
            continue
        
        bindata = data[i + 1:j]
        if odelimit not in bindata:
            yield [v] + bindata + [cdelimit]
        else:
            print('superfluous bin tag')
            continue

class _Table_cell(list):
    def nail(self, i, j, r, c):
        self.col = j
        self.row = i
        self.colspan = c
        self.rowspan = r

class Matrix(list):
    def __str__(self):
        M = []
        for row in self:
            R = ''
            for cell in row:
                if cell is None:
                    C = '|    None    |'
                else:
                    value = ''.join(c for c in cell[1:-1] if isinstance(c, str))
                    C = '|' + value + '            |'[len(value):]
                R += C
            M.append(R)
        return '\n'.join(M)

class Table(object):
    def __init__(self, fields, data):
        self.fields = fields
        # process table structure
        # build rows
        self.data = [list(_Table_cell(C) for C in _bin(R, '<td>', '</td>')) for R in _bin(data, '<tr>', '</tr>')]
        self._build_matrix()
        
    def _build_matrix(self):
        MATRIX = Matrix()
        for i, row in enumerate(self.data):
            # append rows to matrix if needed
            height = max(r[0][1] for r in row)
            if i + height > len(MATRIX):
                MATRIX += [[None] for k in range(i + height - len(MATRIX))]

            # extend matrix to fit the width
            length = sum(r[0][2] for r in row) + sum(k is not None for k in MATRIX[i])
            empty = [None] * length
            if length > len(MATRIX[-1]):
                MATRIX[:] = [R + empty[:length - len(R)] for R in MATRIX]
            
            # drop in cells
            _cellnumber_ = 0
            for s, slot in enumerate(MATRIX[i]):
                # check if cell is occupied
                if slot is None:
                    try:
                        cell = row[_cellnumber_]
                        _cellnumber_ += 1
                    except IndexError:
                        break
                    rspan, cspan = cell[0][1:]
                    cell.nail(i, s, rspan, cspan)
                    for rs in range(rspan):
                        for cs in range(cspan):
                            MATRIX[i + rs][s + cs] = cell
            
        print(MATRIX)
        self._MATRIX = MATRIX
    
    def fill(self, bounds, c, y):
        pass
    
    def __getitem__(self, i):
        if not i:
            return '<table>'
        else:
            raise IndexError
        
