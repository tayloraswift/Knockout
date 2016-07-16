from os import path

from meredith.box import Box

class Metadata(Box):
    DNA = [('filepath', 'str', 'default.html')]
    
    def __init__(self, KT, filepath):
        super().__init__(KT, {'filepath': filepath})
        self.after('filepath')
    
    def after(self, A):
        if A == 'filepath':
            self.filename = path.split(self['filepath'])[-1]
