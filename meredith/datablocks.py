class Datablock_lib(dict):
    def set_funcs(self, ordered):
        self._content_new = ordered.content_new
        self.update_datablocks(ordered)
    
    def update_datablocks(self, ordered):
        self.clear()
        self.update((TT['name'], TT) for TT in ordered.content)

class Tag_lib(Datablock_lib):
    def __missing__(self, key):
        O = self._content_new({'name': key})
        return self[key]
