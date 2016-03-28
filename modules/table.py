from bisect import bisect
from itertools import chain, accumulate

from model.olivia import Flowing_text, Block
from model.george import Subcell
from interface.base import accent
from elements.node import Block_element, Node
from state.exceptions import LineOverflow

class Matrix(list):
    def __str__(self):
        M = []
        for row in self:
            R = ''
            for cell in row:
                if cell is None:
                    C = '|    None    |'
                else:
                    value = ''.join(c for c in cell.text if len(c) == 1)
                    C = '|' + value + '            |'[len(value):]
                R += C
            M.append(R)
        return '\n'.join(M)

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

class _Table_cell(Flowing_text):
    def __init__(self, td):
        Flowing_text.__init__(self, td.content)
        self.rs = td['rowspan']
        self.cs = td['colspan']
    
    def nail(self, i, j):
        self.col = j
        self.row = i

class Table_td(Node):
    name = 'td'
    ADNA = [('rowspan', 1, 'int'), ('colspan', 1, 'int')]

class Table_tr(Node):
    name = 'tr'

class Table(Block_element):
    name = 'table'
    DNA = {'table': {}, 'thead': {}, 'tleft': {}}

    ADNA = [('distr', '', 'float tuple'), ('celltop', 0, 'float'), ('cellbottom', 0, 'float'), ('hrules', set(), 'int set'), ('vrules', set(), 'int set'), ('rulemargin', 0, 'int'), ('rulewidth', 1, 'float')]
    documentation = [(0, name), (1, 'tr'), (2, 'td')]

    def _load(self):
        self._CELLS = [[_Table_cell(td) for td in tr.content] for tr in self.content]
        self._MATRIX = _build_matrix(self._CELLS)
        self._FLOW = [FTX for row in self._CELLS for FTX in row]
        
        # columns
        cl = len(self._MATRIX[0])
        distr = [0] + [d if d else 1 for d in self['distr']]
        distr.extend([1] * (cl - len(distr) + 1))
        total = sum(distr)
        self._MATRIX.partitions = tuple(accumulate(d/total for d in distr))
        
        # rules
        r = len(self._MATRIX)
        self._table = {'rulemargin': self['rulemargin'], 'rulewidth': self['rulewidth'], 
                'hrules': [i for i in self['hrules'] if 0 <= i <= r], 
                'vrules': [i for i in self['vrules'] if 0 <= i <= cl]}

    def regions(self, x, y, bounds, yy):
        x1, x2 = bounds(y)
        r = bisect(yy, y) - 1
        c = max(0, bisect(self._MATRIX.partitions, (x - x1) / (x2 - x1)) - 1)
        try:
            return self._FLOW.index(self._MATRIX[r][c])
        except (IndexError, ValueError):
            return None
    
    def typeset(self, bounds, c, y, y2, overlay):
        P_table, P_head, P_left = self.styles(overlay, 'table', 'thead', 'tleft')
        head = P_table + P_head
        left = P_table + P_left
        
        row_y = [y] * (len(self._MATRIX) + 1)
        part = self._MATRIX.partitions
        cellbottom = self['cellbottom']
        for r, overlay, row in ((c, P_table, b) if c else (c, head, b) for c, b in enumerate(self._CELLS)):
            y = row_y[r] + self['celltop']
            for i, cell in enumerate(row):
                # calculate percentages
                cellbounds = Subcell(bounds, part[cell.col], part[cell.col + cell.cs])
                if not i:
                    ol = overlay + P_left
                else:
                    ol = overlay
                cell.layout(cellbounds, c, y, ol)
                
                bottom = cell.y + cellbottom
                ki = r + cell.rs
                if bottom > row_y[ki]:
                    row_y[ki] = bottom
        
        table = {'_row_y': row_y, '_bounds': bounds.bounds}
        table.update(self._table)
        # calculate grid
        grid = []
        cl = len(self._MATRIX[0])
        part = self._MATRIX.partitions
        for y in row_y:
            x1, x2 = bounds.bounds(y)
            width = x2 - x1
            grid.append([(x1 + width*factor, y) for factor in part])
        
        if grid[-1][-1][1] > y2:
            raise LineOverflow
        return _MBlock(self._FLOW, grid, table, self.regions, self.PP)

members = [Table, Table_tr, Table_td]
inline = False

class _MBlock(Block):
    def __init__(self, FLOW, grid, table, regions, PP):
        self._table = table
        Block.__init__(self, FLOW, grid[0][0][1], grid[-1][-1][1], grid[0][0][0], grid[-1][-1][0], PP)
        
        self._grid = grid
        self._ortho = list(zip( * grid ))
        self._regions = regions

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

    def target(self, x, y):
        if x <= self['right']:
            return self._regions(x, y, self._table['_bounds'], self._table['_row_y'])
        return None

    def deposit(self, repository):
        repository['_paint'].append((self._print_table, 0, 0))
        repository['_paint_annot'].append((self._print_annot, 0, 0))
        for A in self._FLOW:
            A.deposit(repository)
