from meredith.box import Inline

from IO.image import SVG_image, Bitmap_image

class Image(Inline):
    name = 'image'
    DNA = [('src', 'str', ''), ('width', 'int', 89), ('resolution', 'int', 0)]
    
    def _load(self):
        if self['src'][-4:] == '.svg':
            self._image = SVG_image(url=self['src'])
        else:
            self._image = Bitmap_image(self['src'], self['resolution'])
    
    def _cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        self._image.inflate(self['width'], LINE['leading'])
        self._x = x
        self._y = y - LINE['leading']
        return [], self['width'], LINE['leading'], self._image.height - LINE['leading']

    def deposit_glyphs(self, repository, x, y):
        repository['_images'].append((self._image.paint, self._x + x, self._y + y))

members = [Image]
