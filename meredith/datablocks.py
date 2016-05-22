class Datablock_lib(dict):
    def update_datablocks(self, box):
        self.clear()
        self.update((TT['name'], TT) for TT in box.content)

Texttags_D = Datablock_lib()
Blocktags_D = Datablock_lib()
Textstyles_D = Datablock_lib()
