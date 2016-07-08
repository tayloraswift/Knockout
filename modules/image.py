from meredith.box import Inline

from IO.image import SVG_image, Bitmap_image

class Image(Inline):
    name = 'image'
    DNA = [('src', 'str', ''), ('width', 'int', 89), ('resolution', 'int', 0)]
    
    def _load(self):
        if self['src'][-4:] == '.svg':
            self._image = SVG_image   (src=self['src'], h=self['width'])
        else:
            self._image = Bitmap_image(src=self['src'], h=self['width'], resolution=self['resolution'])
    
    def _cast_inline(self, LINE, runinfo, F, FSTYLE):
        self._image.inflate(LINE['leading'])
        self._y_offset = -LINE['leading']
        return [], self['width'], LINE['leading'], self._image.height - LINE['leading']

    def deposit_glyphs(self, repository, x, y):
        repository['_images'].append((self._image.paint, x, self._y_offset + y, 0))

members = [Image]
