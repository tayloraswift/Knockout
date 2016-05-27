class Datablock_lib(dict):
    def update_datablocks(self, box):
        self.clear()
        self.update((TT['name'], TT) for TT in box.content)

class Tag_lib(Datablock_lib):
    def __missing__(self, key):
        self.ordered.new(key)
        return self[key]

Texttags_D = Tag_lib()
Blocktags_D = Tag_lib()
Textstyles_D = Datablock_lib()
