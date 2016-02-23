from cairosvg import surface, parser
from cairosvg.helpers import node_format, preserved_ratio, size

class RSurface(surface.Surface):
    def __init__(self, tree):
        self.context_width, self.context_height = None, None

        self.markers = {}
        self.gradients = {}
        self.patterns = {}
        self.masks = {}
        self.paths = {}
        self.filters = {}
        self._old_parent_node = self.parent_node = None
        
        self.output = None
        self.dpi = 1989

        width, height, viewbox = node_format(self, tree)

        # Initial, non-rounded dimensions
        self.set_context_size(width, height, viewbox, preserved_ratio(tree))
        
        self.tree_cache = {(tree.url, tree.get('id')): tree}
        self.TREE = tree
    
    def paint_SVG(self, CR):
        self.context = CR
        
        self.cursor_position = [0, 0]
        self.cursor_d_position = [0, 0]
        self.text_path_width = 0

        self.font_size = size(self, '12pt')
        self.stroke_and_fill = True
        self.context.move_to(0, 0)
        
        self.draw(self.TREE)

def render_SVG(url):
    tree = parser.Tree(url=url)
    return RSurface(tree)
