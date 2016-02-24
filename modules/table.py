from bisect import bisect
from itertools import chain, accumulate

from model.olivia import Atomic_text, Block
from model.george import Swimming_pool
from interface.base import accent
from IO.xml import print_attrs, print_styles
from elements.elements import Block_element

_namespace = 'table'

def _print_td(td):
        A = td[1]
        if 'rowspan' not in A or A['rowspan'] == 1:
            if 'colspan' not in A or A['colspan'] == 1:
                return '<td>'
            else:
                return '<td colspan="' + A['colspan'] + '">'
        else:
            if 'colspan' not in A or A['colspan'] == 1:
                return '<td rowspan="' + A['rowspan'] + '">'
            else:
                return '<td rowspan="' + A['rowspan'] + '" colspan="' + A['colspan'] + '">'

class _Table_cell(Atomic_text):
    def __init__(self, text, rowspan, colspan):
        Atomic_text.__init__(self, text)
        self.rs = rowspan
        self.cs = colspan
    
    def nail(self, i, j):
        self.col = j
        self.row = i

class TCell_container(Swimming_pool):
    def __init__(self, bounds, i, j):
        Swimming_pool.__init__(self, bounds.railings, bounds.page)
        self._main_bounds = bounds.bounds
        self.i = i
        self.j = j
    
    def bounds(self, y):
        x1, x2 = self._main_bounds(y)
        advance = x2 - x1
        return x1 + advance*self.i, x1 + advance*self.j

class Matrix(list):
    def __str__(self):
        M = []
        for row in self:
            R = ''
            for cell in row:
                if cell is None:
                    C = '|    None    |'
                else:
                    value = ''.join(c for c in cell.text if isinstance(c, str))
                    C = '|' + value + '            |'[len(value):]
                R += C
            M.append(R)
        return '\n'.join(M)

def _row_height(data, r, y):
    cells = (cell for cell in chain.from_iterable(row for row in data) if cell.row + cell.rs - 1 == r)
    return max(cell.y for cell in cells)

def _build_matrix(data):
    MATRIX = Matrix()
    length = 0
    for i, row in enumerate(data):
        # append rows to matrix if needed
        height = max(r.rs for r in row)
        if i + height > len(MATRIX):
            MATRIX += [[None] for k in range(i + height - len(MATRIX))]

        # extend matrix to fit the width
        length = max(length, sum(r.cs for r in row) + sum(k is not None for k in MATRIX[i]))
        empty = [None] * length
        if length > len(MATRIX[-1]):
            MATRIX[:] = [R + empty[:max(0, length - len(R))] for R in MATRIX]
        
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
                cell.nail(i, s)
                for rs in range(cell.rs):
                    for cs in range(cell.cs):
                        MATRIX[i + rs][s + cs] = cell
    return MATRIX

class Table(Block_element):
    namespace = _namespace
    tags = {'tr', 'td'}
    DNA = {'table': {},
            'thead': {},
            'tleft': {}}

    ADNA = {_namespace: [('distr', '', 'float tuple'), ('celltop', 0, 'float'), ('cellbottom', 0, 'float'), ('hrules', set(), 'int set'), ('vrules', set(), 'int set'), ('rulemargin', 0, 'int'), ('rulewidth', 1, 'float')],
            'td': [('rowspan', 1, 'int'), ('colspan', 1, 'int')]
            }
    documentation = [(0, _namespace), (1, 'tr'), (2, 'td')]

    def _load(self, L):
        self._tree = L
        self.PP = L[0][2]
        
        GA = self._get_attributes
        self.data = [[_Table_cell(C, * GA('td', td[1])) for td, C in R] for tr, R in L[1]]
        self._FLOW = [cell for row in self.data for cell in row]
        self._MATRIX = _build_matrix(self.data)
        
        distr, self._celltop, self._cellbottom, hrules, vrules, rulemargin, rulewidth = self._get_attributes(_namespace)
        # columns
        cl = len(self._MATRIX[0])
        distr = [0] + [d if d else 1 for d in distr]
        distr.extend([1] * (cl - len(distr) + 1))
        total = sum(distr)
        self._MATRIX.partitions = tuple(accumulate(d/total for d in distr))
        
        # rules
        hrules = [i for i in hrules if 0 <= i <= len(self._MATRIX)]
        vrules = [i for i in vrules if 0 <= i <= cl]
                
        self._table = {'rulemargin': rulemargin, 'rulewidth': rulewidth, 'hrules': hrules, 'vrules': vrules}
        
    def represent(self, indent):
        name, attrs = self._tree[0][:2]
        attrs.update(print_styles(self.PP))
        lines = [[indent, '<' + print_attrs(name, attrs) + '>']]
        for tr, R in self._tree[1]:
            lines.append([indent + 1, '<tr>'])
            for td, C in R:
                lines.append([indent + 2, _print_td(td)])
                lines.extend(self._SER(C, indent + 3))
                lines.append([indent + 2, '</td>'])
            lines.append([indent + 1, '</tr>'])
        lines.append([indent, '</' + self.namespace + '>'])
        return lines

    def typeset(self, bounds, c, y, overlay):
        P_table, P_head, P_left = self._modstyles(overlay, 'table', 'thead', 'tleft')
        head = P_table + P_head
        left = P_table + P_left
        
        row_y = [y]
        part = self._MATRIX.partitions
        for r, overlay, row in ((c, P_table, b) if c else (c, head, b) for c, b in enumerate(self.data)):
            y += self._celltop
            for i, cell in enumerate(row):
                # calculate percentages
                cellbounds = TCell_container(bounds, part[cell.col], part[cell.col + cell.cs])
                if not i:
                    cell.cast(cellbounds, c, y, overlay + P_left)
                else:
                    cell.cast(cellbounds, c, y, overlay)
            y = _row_height(self.data, r, y) + self._cellbottom
            row_y.append(y)
            
        self._table['row_y'] = row_y
        return _MBlock(self._FLOW, self._MATRIX, bounds, self._table, self.PP)

class _MBlock(Block):
    def __init__(self, FLOW, matrix, bounds, table, PP):
        self._table = table
        row_y = table['row_y']
        x1, x2 = bounds.bounds(row_y[0])
        Block.__init__(self, FLOW, row_y[0], row_y[-1], x1, x2, PP)
        
        self._matrix = matrix
        self._bounds = bounds

        grid = []
        cl = len(matrix[0])
        part = matrix.partitions
        for y in row_y:
            x1, x2 = bounds.bounds(y)
            width = x2 - x1
            grid.append([(x1 + width*factor, y) for factor in part])
        self._grid = grid
        self._ortho = list(zip( * grid ))

    def _print_annot(self, cr, O):
        if O in self._FLOW:
            cr.set_source_rgb( * accent)
            for x, y in chain.from_iterable(self._grid):
                cr.rectangle(int(x), y - 3.25, 0.5, 7)
                cr.rectangle(int(x) - 3.25, y, 7, 0.5)
            self._handle(cr)
            cr.fill()

    def _print_table(self, cr):
        rulewidth = self._table['rulewidth']
        e = (rulewidth % 2) / 2
        p = self._table['rulemargin']
        cr.set_line_width(rulewidth)
        cr.set_source_rgb(0, 0, 0)
        for hrule in self._table['hrules']:
            if p:
                for a, b in zip(self._grid[hrule], self._grid[hrule][1:]):
                    cr.move_to(a[0] + p, a[1] + e)
                    cr.line_to(b[0] - p, b[1] + e)
                    cr.stroke()
            else:
                a = self._grid[hrule][0]
                b = self._grid[hrule][-1]
                cr.move_to(a[0], a[1] + e)
                cr.line_to(b[0], b[1] + e)
                cr.stroke()

        for vrule in self._table['vrules']:
            if p:
                for a, b in zip(self._ortho[vrule], self._ortho[vrule][1:]):
                    cr.move_to(a[0] + e, a[1] + p)
                    cr.line_to(b[0] + e, b[1] - p)
                    cr.stroke()
            else:
                a = self._ortho[vrule][0]
                b = self._ortho[vrule][-1]
                cr.move_to(a[0] + e, a[1])
                cr.line_to(b[0] + e, b[1])
                cr.stroke()

    def I(self, x, y):
        x1, x2 = self._bounds.bounds(y)
        r = bisect(self._table['row_y'], y) - 1
        c = max(0, bisect(self._matrix.partitions, (x - x1) / (x2 - x1)) - 1)
        try:
            O = self._matrix[r][c]
            if O is None or not O.text:
                print('Empty cell selected')
                return self['i']
            else:
                return O
        except IndexError:
            return self['i']

    def deposit(self, repository):
        repository['_paint'].append(self._print_table)
        for A in self._FLOW:
            A.deposit(repository)
        repository['_paint_annot'].append(self._print_annot)
