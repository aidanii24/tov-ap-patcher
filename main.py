from packer import *
from patcher import *

class VesperiaPatcherApp():
    packer: VesperiaPacker
    patcher: VesperiaPatcher

    def __init__(self):
        self.packer = VesperiaPacker()
        self.packer.check_dependencies()

        self.patcher = VesperiaPatcher()

    def unpack_files(self):
        self.packer.unpack_btl()
        self.packer.extract_artes()

    def patch_artes(self):
        self.patcher.patch_artes()

    def pack_files(self):
        self.packer.pack_artes()
        self.packer.pack_btl()


if __name__ == '__main__':
    app = VesperiaPatcherApp()
    # app.unpack_files()
    app.patch_artes()
    app.pack_files()